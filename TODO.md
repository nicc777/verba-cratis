# Current issues to sort out

* [X] Fix command line argument parsing when using Docker
* [X] Fix logging to include the actual function calling the logger function
* [ ] Fix logging configuration
* [ ] Add logging of exceptions everywhere where the app is currently printing stack traces.

# Features to Implement

* [x] Parse system manifest
* [x] Parse project manifest
* [ ] Implement script parser
* [ ] Parse shell script manifest
* [ ] Parse environment variables manifest
* [ ] Enable environment variables to consume variables produced by shell script execution
* [ ] Parse task manifest
* [ ] Parse deployment manifest
* [ ] Calculate task execution plan
* [ ] Execute task execution
* [ ] Implement state DB
* [ ] Persist results from task execution in state DB
* [ ] Calculate difference between current deployment plan and previous persisted execution
* [ ] Load global configs from configuration files
  
