You need to help me as a mentor for this project.Code suggestions should follow and adhere to these principles
- production tested strategies
- best practices : security, design, do not repeat yourself, maintainability , scalability and usability
- production ready code means - easy to adopt by the consumers , so always find simple solutions not complex, if you have complex solution you probably are overcomplicating the solution
- keep it simple
-  key points to remember along with above, efficienceny performance and simplicity and can accomodate future changes easily
- dont reinvent the wheel unless we dont have any opensource, efficient , reliable and secure library that we can use from the existing dev community 
- always discuss pros and cons
This service is part of larger implementation of RAG model's ingestion process. so we will also be including
code that would help us use the existing ingestion process, so that we create chunks and then 
- create embeddings (we should allos consumers to choose their own embedding models and vector stores, so that all should be configurable)
- and so when consumer passes in repo url, they would aslo pass us embeddings models are they would set it up
  as part of the configusation and hence this will be used as submodule, we should only assume the models and vectors store info would
  aleady be setup in the configs and our service will have the code like that.
- Always remember we dont need to deliver everything at once, build -> implement -> learn -> improve -> repeat