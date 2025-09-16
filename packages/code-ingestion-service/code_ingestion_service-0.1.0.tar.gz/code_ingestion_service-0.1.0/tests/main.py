import json
from src.code_ingestion.chunkers import factory

java_code: str = '''
package com.example.service;

import java.util.*;
import java.time.LocalDateTime;
import java.util.concurrent.CompletableFuture;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import com.example.dto.UserDTO;
import com.example.dto.OrderDTO;
import com.example.entity.User;
import com.example.entity.Order;
import com.example.repository.UserRepository;
import com.example.repository.OrderRepository;
import com.example.exception.UserNotFoundException;
import com.example.exception.OrderNotFoundException;

@Service
@Transactional
@RequestMapping
public class UserOrderManagementService {
    
    private final UserRepository userRepository;
    private final OrderRepository orderRepository;
    private final EmailService emailService;
    private final AuditService auditService;
    private final MetricsCollector metricsCollector;
    
    private static final String DEFAULT_USER_STATUS = "ACTIVE";
    private static final int MAX_ORDERS_PER_USER = 100;
    private static final long CACHE_EXPIRY_MINUTES = 30;
    
    @Autowired
    public UserOrderManagementService(
            UserRepository userRepository, 
            OrderRepository orderRepository,
            EmailService emailService,
            AuditService auditService,
            MetricsCollector metricsCollector) {
        this.userRepository = userRepository;
        this.orderRepository = orderRepository;
        this.emailService = emailService;
        this.auditService = auditService;
        this.metricsCollector = metricsCollector;
    }
    
    @GetMapping
    public UserDTO createUser(String username, String email, String firstName, String lastName) {
        validateUserInput(username, email, firstName, lastName);
        
        User existingUser = userRepository.findByUsernameOrEmail(username, email);
        if (existingUser != null) {
            throw new IllegalArgumentException("User with username or email already exists");
        }
        
        User newUser = new User();
        newUser.setUsername(username);
        newUser.setEmail(email);
        newUser.setFirstName(firstName);
        newUser.setLastName(lastName);
        newUser.setStatus(DEFAULT_USER_STATUS);
        newUser.setCreatedAt(LocalDateTime.now());
        newUser.setUpdatedAt(LocalDateTime.now());
        
        User savedUser = userRepository.save(newUser);
        auditService.logUserCreation(savedUser.getId(), username);
        metricsCollector.incrementUserCreationCounter();
        
        return convertToUserDTO(savedUser);
    }
    
    public Optional<UserDTO> findUserById(Long userId) {
        if (userId == null || userId <= 0) {
            throw new IllegalArgumentException("User ID must be positive");
        }
        
        metricsCollector.incrementUserLookupCounter();
        return userRepository.findById(userId)
                .map(this::convertToUserDTO);
    }
    
    public List<UserDTO> findUsersByStatus(String status, int page, int size) {
        validatePaginationParameters(page, size);
        
        Pageable pageable = PageRequest.of(page, size);
        Page<User> users = userRepository.findByStatus(status, pageable);
        
        return users.getContent().stream()
                .map(this::convertToUserDTO)
                .collect(Collectors.toList());
    }
    
    public UserDTO updateUserProfile(Long userId, String firstName, String lastName, String email) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new UserNotFoundException("User not found with ID: " + userId));
        
        String oldEmail = user.getEmail();
        
        user.setFirstName(firstName);
        user.setLastName(lastName);
        user.setEmail(email);
        user.setUpdatedAt(LocalDateTime.now());
        
        User updatedUser = userRepository.save(user);
        
        if (!oldEmail.equals(email)) {
            emailService.sendEmailChangeNotification(oldEmail, email);
        }
        
        auditService.logUserUpdate(userId, "Profile updated");
        return convertToUserDTO(updatedUser);
    }
    
    public void deactivateUser(Long userId, String reason) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new UserNotFoundException("User not found with ID: " + userId));
        
        user.setStatus("INACTIVE");
        user.setDeactivatedAt(LocalDateTime.now());
        user.setDeactivationReason(reason);
        
        userRepository.save(user);
        
        // Cancel all pending orders for this user
        List<Order> pendingOrders = orderRepository.findByUserIdAndStatus(userId, "PENDING");
        pendingOrders.forEach(order -> {
            order.setStatus("CANCELLED");
            order.setCancellationReason("User deactivated");
        });
        orderRepository.saveAll(pendingOrders);
        
        auditService.logUserDeactivation(userId, reason);
        emailService.sendAccountDeactivationNotification(user.getEmail());
    }
    
    public OrderDTO createOrder(Long userId, List<OrderItemDTO> items, String shippingAddress) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new UserNotFoundException("User not found with ID: " + userId));
        
        if (!"ACTIVE".equals(user.getStatus())) {
            throw new IllegalStateException("Cannot create order for inactive user");
        }
        
        int userOrderCount = orderRepository.countByUserId(userId);
        if (userOrderCount >= MAX_ORDERS_PER_USER) {
            throw new IllegalStateException("User has reached maximum order limit");
        }
        
        validateOrderItems(items);
        
        Order order = new Order();
        order.setUserId(userId);
        order.setStatus("PENDING");
        order.setShippingAddress(shippingAddress);
        order.setCreatedAt(LocalDateTime.now());
        order.setTotalAmount(calculateTotalAmount(items));
        
        Order savedOrder = orderRepository.save(order);
        
        emailService.sendOrderConfirmation(user.getEmail(), savedOrder.getId());
        auditService.logOrderCreation(savedOrder.getId(), userId);
        metricsCollector.incrementOrderCreationCounter();
        
        return convertToOrderDTO(savedOrder);
    }
    
    public List<OrderDTO> getUserOrders(Long userId, String status, int page, int size) {
        if (!userRepository.existsById(userId)) {
            throw new UserNotFoundException("User not found with ID: " + userId);
        }
        
        validatePaginationParameters(page, size);
        Pageable pageable = PageRequest.of(page, size);
        
        Page<Order> orders;
        if (status != null && !status.trim().isEmpty()) {
            orders = orderRepository.findByUserIdAndStatus(userId, status, pageable);
        } else {
            orders = orderRepository.findByUserId(userId, pageable);
        }
        
        return orders.getContent().stream()
                .map(this::convertToOrderDTO)
                .collect(Collectors.toList());
    }
    
    public OrderDTO updateOrderStatus(Long orderId, String newStatus, String reason) {
        Order order = orderRepository.findById(orderId)
                .orElseThrow(() -> new OrderNotFoundException("Order not found with ID: " + orderId));
        
        String oldStatus = order.getStatus();
        
        if (!isValidStatusTransition(oldStatus, newStatus)) {
            throw new IllegalArgumentException(
                String.format("Invalid status transition from %s to %s", oldStatus, newStatus));
        }
        
        order.setStatus(newStatus);
        order.setStatusReason(reason);
        order.setUpdatedAt(LocalDateTime.now());
        
        Order updatedOrder = orderRepository.save(order);
        
        // Send notifications based on status change
        User user = userRepository.findById(order.getUserId()).orElse(null);
        if (user != null) {
            emailService.sendOrderStatusUpdate(user.getEmail(), orderId, newStatus);
        }
        
        auditService.logOrderStatusChange(orderId, oldStatus, newStatus, reason);
        return convertToOrderDTO(updatedOrder);
    }
    
    public CompletableFuture<Map<String, Object>> generateUserActivityReport(Long userId) {
        return CompletableFuture.supplyAsync(() -> {
            User user = userRepository.findById(userId)
                    .orElseThrow(() -> new UserNotFoundException("User not found with ID: " + userId));
            
            List<Order> userOrders = orderRepository.findByUserId(userId);
            
            Map<String, Object> report = new HashMap<>();
            report.put("userId", userId);
            report.put("username", user.getUsername());
            report.put("totalOrders", userOrders.size());
            report.put("totalSpent", userOrders.stream()
                    .mapToDouble(Order::getTotalAmount)
                    .sum());
            report.put("averageOrderValue", userOrders.isEmpty() ? 0 : 
                    userOrders.stream().mapToDouble(Order::getTotalAmount).average().orElse(0));
            report.put("lastOrderDate", userOrders.stream()
                    .map(Order::getCreatedAt)
                    .max(LocalDateTime::compareTo)
                    .orElse(null));
            report.put("generatedAt", LocalDateTime.now());
            
            return report;
        });
    }
    
    private void validateUserInput(String username, String email, String firstName, String lastName) {
        if (username == null || username.trim().isEmpty()) {
            throw new IllegalArgumentException("Username cannot be null or empty");
        }
        if (email == null || !isValidEmail(email)) {
            throw new IllegalArgumentException("Invalid email address");
        }
        if (firstName == null || firstName.trim().isEmpty()) {
            throw new IllegalArgumentException("First name cannot be null or empty");
        }
        if (lastName == null || lastName.trim().isEmpty()) {
            throw new IllegalArgumentException("Last name cannot be null or empty");
        }
    }
    
    private boolean isValidEmail(String email) {
        return email.contains("@") && email.contains(".") && email.length() > 5;
    }
    
    private void validatePaginationParameters(int page, int size) {
        if (page < 0) {
            throw new IllegalArgumentException("Page number must be non-negative");
        }
        if (size <= 0 || size > 100) {
            throw new IllegalArgumentException("Page size must be between 1 and 100");
        }
    }
    
    private void validateOrderItems(List<OrderItemDTO> items) {
        if (items == null || items.isEmpty()) {
            throw new IllegalArgumentException("Order must contain at least one item");
        }
        
        for (OrderItemDTO item : items) {
            if (item.getQuantity() <= 0) {
                throw new IllegalArgumentException("Item quantity must be positive");
            }
            if (item.getPrice() <= 0) {
                throw new IllegalArgumentException("Item price must be positive");
            }
        }
    }
    
    private double calculateTotalAmount(List<OrderItemDTO> items) {
        return items.stream()
                .mapToDouble(item -> item.getPrice() * item.getQuantity())
                .sum();
    }
    
    private boolean isValidStatusTransition(String fromStatus, String toStatus) {
        Map<String, List<String>> validTransitions = Map.of(
            "PENDING", Arrays.asList("CONFIRMED", "CANCELLED"),
            "CONFIRMED", Arrays.asList("SHIPPED", "CANCELLED"),
            "SHIPPED", Arrays.asList("DELIVERED", "RETURNED"),
            "DELIVERED", Arrays.asList("RETURNED"),
            "CANCELLED", Collections.emptyList(),
            "RETURNED", Collections.emptyList()
        );
        
        return validTransitions.getOrDefault(fromStatus, Collections.emptyList())
                .contains(toStatus);
    }
    
    private UserDTO convertToUserDTO(User user) {
        UserDTO dto = new UserDTO();
        dto.setId(user.getId());
        dto.setUsername(user.getUsername());
        dto.setEmail(user.getEmail());
        dto.setFirstName(user.getFirstName());
        dto.setLastName(user.getLastName());
        dto.setStatus(user.getStatus());
        dto.setCreatedAt(user.getCreatedAt());
        return dto;
    }
    
    private OrderDTO convertToOrderDTO(Order order) {
        OrderDTO dto = new OrderDTO();
        dto.setId(order.getId());
        dto.setUserId(order.getUserId());
        dto.setStatus(order.getStatus());
        dto.setTotalAmount(order.getTotalAmount());
        dto.setShippingAddress(order.getShippingAddress());
        dto.setCreatedAt(order.getCreatedAt());
        return dto;
    }
}
'''


def test_chunker():
    chunker = factory.create_java_chunker(max_class_size=2000)
    chunks = chunker.chunk_code(
        java_code,
        file_path="src/main/java/com/example/UserService.java",
        repo_url="https://github.com/example/repo"
    )

    for chunk in chunks:
        chunk_dict = {
            "id": chunk.id,
            "content": chunk.content,
            "metadata": {
                "repoUrl": chunk.metadata.repo_url,
                "filePath": chunk.metadata.file_path,
                "fileName": chunk.metadata.file_name,
                "className": chunk.metadata.class_name,
                "methodName": chunk.metadata.method_name,
                "signature": chunk.metadata.signature,
                "returnType": chunk.metadata.return_type,
                "fields": chunk.metadata.fields,
                "methods": chunk.metadata.methods,
                "chunkType": chunk.metadata.chunk_type,
                "chunkSize": chunk.metadata.chunk_size,
                "startLine": chunk.metadata.start_line,
                "endLine": chunk.metadata.end_line,
                "language": chunk.metadata.language,
                "processedAt": chunk.metadata.processed_at
            }
        }
        print(json.dumps(chunk_dict, indent=2))


def test_embedding_provider():
    """Test embedding provider with chunked code."""
    from src.code_ingestion.embeddings import create_nomic_embedding_provider

    chunker = factory.create_java_chunker(max_class_size=2000)
    chunks = chunker.chunk_code(
        java_code,
        file_path="src/main/java/com/example/UserService.java",
        repo_url="https://github.com/example/repo"
    )

    embedding_provider = create_nomic_embedding_provider()

    texts = [chunk.content for chunk in chunks]
    embeddings = embedding_provider.embed_chunks(texts)

    print(f"\n🧪 Embedding Test Results:")
    print(f"Generated {len(chunks)} chunks")
    print(f"Generated {len(embeddings)} embeddings")
    print(f"Embedding dimension: {embedding_provider.get_embedding_dimension()}")
    print(f"First embedding shape: {len(embeddings[0]) if embeddings else 0}")


def test_pine_cone_ingestion():
    from src.code_ingestion.orchestration import create_ingestion_orchestrator
    
    # Use new orchestrator
    orchestrator = create_ingestion_orchestrator(
        embedding_provider='nomic',
        vector_store='pinecone'
    )
    
    # Prepare source files in expected format
    source_files = [("src/main/java/com/example/UserService.java", java_code)]
    result = orchestrator.execute(source_files)
    
    print(f"✅ Test completed: {result.chunks_processed} chunks processed")


# =================== PERFORMANCE & OPTIMIZATION TESTS ===================

def test_chunking_strategy_decisions():
    """Test that chunking strategy correctly decides between complete class vs method-level chunking."""
    print('\n🔄 Testing chunking strategy decisions...')

    # Small class test data
    small_java_code = '''
package com.example;

public class SmallService {
    public void method1() { return; }
    public void method2() { return; }
}
'''

    # Large class test data  
    large_java_code = '''
package com.example.service;

import java.util.List;
import java.security.Authentication;

/**
 * Large service class for testing chunking strategy.
 */
public class LargeUserService {
    private String serviceName;
    private boolean isActive;
    
    public LargeUserService() {
        this.serviceName = "UserService";
        this.isActive = true;
    }
    
    public boolean authenticate(String username, String password) {
        if (username == null || username.trim().isEmpty()) {
            return false;
        }
        if (password == null || password.length() < 8) {
            return false;
        }
        return true;
    }
    
    public boolean authorize(String username, String resource) {
        return true;
    }
    
    public Long createUser(String userDetails) {
        return System.currentTimeMillis();
    }
}
'''

    # Create chunker with small threshold to test splitting
    chunker = factory.create_java_chunker(max_class_size=500)

    # Test small class (should stay complete)
    small_chunks = chunker.chunk_code(small_java_code, 'SmallService.java', 'repo')
    print(f'Small class ({len(small_java_code)} chars): {len(small_chunks)} chunks')
    for chunk in small_chunks:
        print(f'  - Type: {chunk.metadata.chunk_type}, Method: {chunk.metadata.method_name}')

    # Test large class (should be split)
    large_chunks = chunker.chunk_code(large_java_code, 'LargeUserService.java', 'repo')
    print(f'Large class ({len(large_java_code)} chars): {len(large_chunks)} chunks')
    for chunk in large_chunks:
        print(f'  - Type: {chunk.metadata.chunk_type}, Method: {chunk.metadata.method_name}')

    # Verify strategy decisions
    assert len(small_chunks) == 1, f"Small class should have 1 chunk, got {len(small_chunks)}"
    assert small_chunks[0].metadata.chunk_type == "complete_class", "Small class should be complete_class type"

    assert len(large_chunks) > 1, f"Large class should be split into multiple chunks, got {len(large_chunks)}"
    assert all(chunk.metadata.chunk_type in ["method", "constructor"] for chunk in
               large_chunks), "Large class chunks should be method/constructor types"

    print('✅ Chunking strategy decisions working correctly!')


def test_single_pass_ast_performance():
    """Test that single-pass CST extraction works correctly and preserves functionality."""
    print('\n🔄 Testing single-pass CST extraction...')

    chunker = factory.create_java_chunker(max_class_size=2000)

    # Test with the main java_code
    chunks = chunker.chunk_code(
        java_code,
        file_path='src/main/java/com/example/UserService.java',
        repo_url='https://github.com/example/repo'
    )

    print(f'✅ Successfully created {len(chunks)} chunks using optimized single-pass CST')

    # Verify chunk structure is preserved
    for i, chunk in enumerate(chunks):
        print(f'Chunk {i + 1}: {chunk.metadata.chunk_type} - {chunk.metadata.method_name or chunk.metadata.class_name}')

        # Verify essential metadata is present
        assert chunk.id is not None, "Chunk ID should not be None"
        assert chunk.content is not None, "Chunk content should not be None"
        assert chunk.metadata.language is not None, "Language should not be None"
        assert chunk.metadata.chunk_type is not None, "Chunk type should not be None"

        # Verify content has proper context (package + imports + class structure)
        assert "package com.example.service;" in chunk.content, "Chunk should contain package info"
        assert "import java.util.*;" in chunk.content, "Chunk should contain import info"

    print('✅ Single-pass CST extraction preserves all functionality!')


def test_metadata_serialization():
    """Test that metadata serialization works correctly for Pinecone without custom objects."""
    print('\n🔄 Testing metadata serialization for Pinecone compatibility...')

    chunker = factory.create_java_chunker(max_class_size=500)  # Force method splitting

    test_code = '''
package com.example;

public class TestService {
    private String name;
    
    public boolean authenticate(String user) {
        return user != null;
    }
}
'''

    chunks = chunker.chunk_code(test_code, 'TestService.java', 'repo')

    for i, chunk in enumerate(chunks):
        print(f'\\nTesting chunk {i + 1} ({chunk.metadata.chunk_type}):')

        # Test serialization
        serialized = chunk.metadata.model_dump(exclude_none=True, exclude_unset=True)
        print(f'  Serialized metadata keys: {list(serialized.keys())}')

        # Verify only Pinecone-compatible types
        for key, value in serialized.items():
            if not isinstance(value, (str, int, float, bool, list)):
                raise AssertionError(f'Invalid type for Pinecone: {key} = {type(value)}')
            elif isinstance(value, list) and value and not all(isinstance(item, str) for item in value):
                raise AssertionError(f'Invalid list type for Pinecone: {key} = {[type(item) for item in value]}')
            print(f'  ✅ {key}: {type(value).__name__}')

        # Verify modifiers are not present (we removed them)
        assert 'modifiers' not in serialized, "Modifiers should be removed from metadata"

        # Verify signature still contains modifier info when present
        if chunk.metadata.signature:
            print(f'  ✅ Signature contains access info: {chunk.metadata.signature}')

    print('\\n✅ Metadata serialization is Pinecone-compatible!')


def test_pinecone_ingestion_with_validation():
    """Test Pinecone ingestion with validation that no custom objects are present."""
    print('\n🔄 Testing Pinecone ingestion with serialization validation...')

    try:
        from src.code_ingestion.orchestration import create_ingestion_orchestrator

        # Create test data - use orchestrator
        orchestrator = create_ingestion_orchestrator(
            embedding_provider='nomic',
            vector_store='pinecone'
        )

        # Prepare source files
        source_files = [("src/main/java/com/example/UserService.java", java_code)]
        
        print(f'Testing Pinecone ingestion with orchestrator')

        # Execute ingestion
        result = orchestrator.execute(source_files)

        print(f'✅ Successfully ingested {result.chunks_processed} chunks to Pinecone')
        print(f'✅ No serialization errors - all custom objects properly excluded')

        return result

    except Exception as e:
        print(f'❌ Pinecone ingestion test failed: {e}')
        raise


def test_performance_optimizations():
    """Test that performance optimizations don't break existing functionality."""
    print('\n🔄 Testing performance optimizations preserve functionality...')

    # Test with various class sizes
    test_cases = [
        ("Small class", 100),
        ("Medium class", 800),
        ("Large class", 300)  # Will force splitting
    ]

    for case_name, max_size in test_cases:
        print(f'\\n--- Testing {case_name} (max_size: {max_size}) ---')

        chunker = factory.create_java_chunker(max_class_size=max_size)
        chunks = chunker.chunk_code(
            java_code,
            file_path=f"src/test/{case_name.replace(' ', '')}.java",
            repo_url="https://github.com/test/repo"
        )

        print(f'  Generated {len(chunks)} chunks')

        # Verify each chunk has proper structure
        for chunk in chunks:
            # Context should include package and imports
            assert "package com.example.service;" in chunk.content
            assert "import java.util.*;" in chunk.content

            # Metadata should be complete
            assert chunk.metadata.language == "java"
            assert chunk.metadata.repo_url == "https://github.com/test/repo"
            assert chunk.metadata.chunk_size > 0

            print(f'    ✅ {chunk.metadata.chunk_type}: {chunk.metadata.method_name or chunk.metadata.class_name}')

    print('\\n✅ Performance optimizations preserve all functionality!')


# =================== CONVENIENCE TEST RUNNERS ===================

def run_all_optimization_tests():
    """Run all optimization and performance tests."""
    print('\\n' + '=' * 60)
    print('RUNNING ALL OPTIMIZATION TESTS')
    print('=' * 60)

    test_chunking_strategy_decisions()
    test_single_pass_ast_performance()
    test_metadata_serialization()
    test_performance_optimizations()

    print('\\n' + '=' * 60)
    print('✅ ALL OPTIMIZATION TESTS PASSED!')
    print('=' * 60)


def run_all_pinecone_tests():
    """Run all Pinecone-related tests."""
    print('\\n' + '=' * 60)
    print('RUNNING ALL PINECONE TESTS')
    print('=' * 60)

    test_metadata_serialization()
    test_pinecone_ingestion_with_validation()

    print('\\n' + '=' * 60)
    print('✅ ALL PINECONE TESTS PASSED!')
    print('=' * 60)
