# Challenge

### Original request



You are tasked to manage cloud resource provisioning for enterprise users, i.e. when a new user / user group comes to you, you need to provision some cloud resources so that they can start working on their project. The "package" for them is typically standard, but some users might come with different requirements, e.g. T-shirt size computation needs. The goal is to give people what they need quickly, and put guardrails around what they are allowed and not allowed to use.



You need to build a backend application that allows efficient and scalable management.



Requirements:

The backend application will run in k8s.
Develop the backend application in python
Manage the cloud resources using terraform (i.e. infrastructure as code)
Use Helm to deploy the application
Bonus: develop a CI/CD pipeline


Feel free to make reasonable assumptions if there are gaps in our challenge setup.



# Plan

### First thought

I'd gently kiss on the forehead of that tired engineer who will prototype/test/implement/deploy/monitor/document production grade backend in two hours as email suggested. Joke's aside, lets get into it. 

### Architecture and design

There will be some parts of the software that I'll explicitly omit (i.e. known unknowns, lower abstractions, costly cloud infra, etc.) and some parts that I will implicitly accept (i.e. path of least resistance, previous experience, best practices, etc.). But I'll be clear about all of them every time.

System architecture is already defined by the requirements: deliberate mention of k8s will shape the system to have Microservice architecture.
Probably I'll use a design antipattern and create Python server-side rendering frontend in the same Python container as the backend code. Or I'll create REST API endpoints and consume them from a different frontend container, if I'll have enough time for that.

I'll try to touch as much different parts of the requirement stack as possible, and doing so I'll not be able to enter into deep details of each. Software architecture is all about trade-offs and I'm choosing this approach to demonstrate my overall knowledge of the stack.

# Implementation

### Main components


- k8s - I'll use my ubuntu local machine to spin k8s.
- Python - I'll use official docker image with most recent tag, and expose the app with [Ngrok](https://ngrok.com/).
- Helm - I'll use binary package installation without package managers from [this GitHub repo](https://github.com/helm/helm/releases/tag/v4.1.3).
- Terraform - [Localstack](https://github.com/localstack/localstack) will be used to simulate AWS services for Terraform. 


### Comments on other components

- ci/cd - I've created an email (email: boehringer-ingelheim-test@protonmail.com) and Github repo (under the same email) for CI/CD. There is a single repo 'test' for all the code.
- Frontend - I'll use Python to create REST API endpoints, but I'll try and implement some server-side rendered frontend container if I'll have enough time. Or maybe even another container that will consume the endpoints? we'll see.
- For production PostgreSQL with row level security would be much more powerful than SQLite.   
- Testing is an apart concern for everything from python unit testing to Helm chart hashing to k8s pod probes to app E2E finals, I'm deliberately omiting testing as given system has high DoF and each component requiers different kind of testing. 
- Git branching is out of scope as wel with its name conventions, how long each branch should live, who can access protected branches in production, etc. 
- I'll also omit many AWS networking concepts like CIDR, routing tables, NAT gateway, NACL's and security groups. Those are fundamental concepts to consider in production, but in our case none of this are needed. 
- I will not consider too much SecOps part, it would be first to think in production, but we can neglect it by now.  

### Usage

Please find the Machine-Generated-readme.md file.

# Final thought

Overall I'm not happy with the result, there are many things that I have not tested and made AI create and run the code/infra, but at least I was able to create and define the main structure, deploy Python within k8s using Helm and access it through Ngrok from public internet. Docker Compose also correctly deployed Localstack in parrallel with minikube and run Terraform correctly. I wish I could do more, but that's all I can get done by now. Thanks 
