# Detailed Setup Notes

This document contains in-depth technical details about the project structure, deployment process, and design decisions. It serves as a comprehensive reference guide capturing all key learnings from setting up a production-ready FastAPI application with AWS Lambda deployment.

## Architecture Overview

This project implements a serverless API using:
- **FastAPI**: Modern, fast Python web framework
- **Mangum**: Adapter that converts AWS Lambda events to ASGI format for FastAPI
- **AWS Lambda**: Serverless compute service
- **API Gateway**: Managed API endpoint service
- **Serverless Framework**: Infrastructure-as-code deployment tool

The architecture follows these principles:
- **Feature-based structure**: Related files kept together
- **Clean separation of concerns**: Routing, business logic, and data models separated
- **Infrastructure as code**: All AWS resources defined in serverless.yml
- **Python for application logic, Node.js tools for deployment**: Using each technology for its strengths

## Detailed Project Structure Explanation

### Feature-Based Organization

Unlike traditional MVC patterns that separate files by technical role (controllers, models, etc.), this project uses a feature-based approach:

```
app/api/hello/
├── __init__.py
├── router.py      # API endpoints for hello feature
├── schemas.py     # Request/response models for hello feature
└── service.py     # Business logic for hello feature
```

Benefits:
- Related code stays together
- Easier to understand and maintain
- Supports parallel development by different teams
- New developers can quickly understand feature boundaries

### Core Files Explanation

- **app/main.py**: Entry point that creates the FastAPI instance, includes routers, and defines the Mangum handler for AWS Lambda
- **app/api/routes.py**: Central router that includes all feature routers
- **dev.py**: Local development script that runs Uvicorn for testing
- **serverless.yml**: Defines all AWS resources and deployment configuration

## AWS Lambda Deployment Details

### How the API Gateway Integration Works

The serverless.yml configures API Gateway with a "catch-all" route:

```yaml
functions:
  api:
    handler: app.main.handler
    events:
      - httpApi:
          path: /api/{proxy+}
          method: any
```

The `{proxy+}` notation:
- Captures any path after `/api/`
- Forwards the complete path, query parameters, and HTTP method to Lambda
- Lets FastAPI handle the actual routing

### The Role of Mangum

Mangum acts as an adapter between AWS Lambda events and ASGI applications:

1. Lambda receives an API Gateway event
2. Mangum translates this event into an ASGI event
3. FastAPI processes this ASGI event
4. Mangum converts the response back to Lambda format

```python
# app/main.py
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()
# ... router setup ...

# This is what AWS Lambda calls
handler = Mangum(app)
```

This bridge is critical because Lambda and FastAPI speak different "languages":
- Lambda receives API Gateway events in a specific JSON format
- FastAPI expects ASGI-compliant HTTP requests
- Without Mangum, these two systems couldn't communicate

Mangum handles several complex tasks:
- Event translation (API Gateway → ASGI)
- Response transformation (ASGI → Lambda format)
- Context handling (providing Lambda context information)
- Support for different API Gateway integration types (REST, HTTP)

## Local Development vs Production

### Development Environment

Local development uses Uvicorn directly:
```python
# dev.py
import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
```

This provides:
- Hot reloading for code changes
- Direct access to endpoints
- FastAPI's automatic documentation (Swagger UI)

### Production Environment

In production, the request flow is:
1. Client → API Gateway
2. API Gateway → Lambda
3. Lambda (Mangum) → FastAPI
4. FastAPI → Lambda (Mangum)
5. Lambda → API Gateway
6. API Gateway → Client

## AWS Credentials and Security

For production use, never store AWS credentials in your codebase. The project uses environment variables through the `serverless-dotenv-plugin` to load credentials securely.

### AWS Authentication Methods: IAM Users vs. AWS SSO

The project can work with two different AWS authentication approaches:

#### IAM User (Access Key/Secret Key)
- **What it is**: An identity created in AWS Identity and Access Management 
- **How it works**: 
  - You create a user with access key ID and secret access key
  - These long-lived credentials are used for programmatic access
  - You configure these in your environment or AWS config file
- **Security considerations**: 
  - Keys don't expire automatically
  - Need to be rotated manually
  - Risk of exposure if not properly secured

#### AWS SSO (Single Sign-On)
- **What it is**: A modern authentication system that uses your organization's identity provider
- **How it works**:
  - You log in through a web portal
  - You get temporary credentials that expire automatically
  - More secure because there are no long-lived access keys
- **Security considerations**:
  - More secure due to temporary credentials
  - Integrated with organizational identity management
  - Better audit trail

### Setting Up AWS Credentials

1. Create an IAM user with programmatic access:
   - Go to AWS Management Console → IAM → Users → Create User
   - Enable programmatic access
   - Attach appropriate policies (AWSLambdaFullAccess, IAMFullAccess, etc.)
   - Save your access key ID and secret access key securely

2. Configure credentials locally (choose one):
   
   **Option A: Using AWS CLI**
   ```bash
   aws configure
   # Enter access key, secret key, region, and output format
   ```
   
   **Option B: Environment Variables**
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_REGION=us-east-1
   ```
   
   **Option C: .env file with dotenv plugin**
   ```
   # .env file (don't commit to git)
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   ```

3. When working with multiple AWS accounts, use named profiles:
   ```bash
   aws configure --profile project1
   aws configure --profile project2
   ```
   
   Then specify the profile when deploying:
   ```bash
   npx serverless deploy --aws-profile project1
   ```

### Recommended IAM Permissions

For a production environment, create a custom IAM policy with only the necessary permissions:
- Lambda function creation and management
- API Gateway management
- CloudWatch Logs
- S3 access for deployment artifacts
- IAM role management for service execution

## Understanding Serverless.yml Configuration

The `serverless.yml` file is the core configuration that defines how your application is deployed:

```yaml
service: fastapi-lambda-app

provider:
  name: aws
  runtime: python3.9
  region: us-east-1
  stage: ${opt:stage, 'dev'}
  environment:
    STAGE: ${self:provider.stage}

functions:
  api:
    handler: app.main.handler
    events:
      - httpApi:
          path: /api/{proxy+}
          method: any

plugins:
  - serverless-python-requirements
  - serverless-dotenv-plugin

custom:
  pythonRequirements:
    dockerizePip: true
    slim: true
```

Key components explained:
- **service**: Unique name for your service
- **provider**: Specifies AWS as cloud provider, Python runtime, region
- **functions**: Defines Lambda functions
  - **handler**: Points to your Mangum handler function (app.main.handler)
  - **events**: Configures API Gateway triggers
- **plugins**: Serverless plugins (handling Python dependencies, environment variables)
- **custom**: Plugin configuration

## Extending the Project

### Adding a Database

To add DynamoDB:

1. Add to serverless.yml:
```yaml
resources:
  Resources:
    TodosTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: ${self:service}-todos-${self:provider.stage}
        BillingMode: PAY_PER_REQUEST
        AttributeDefinitions:
          - AttributeName: id
            AttributeType: S
        KeySchema:
          - AttributeName: id
            KeyType: HASH
```

2. Give Lambda permission to access DynamoDB:
```yaml
provider:
  iamRoleStatements:
    - Effect: Allow
      Action:
        - dynamodb:Query
        - dynamodb:Scan
        - dynamodb:GetItem
        - dynamodb:PutItem
        - dynamodb:UpdateItem
        - dynamodb:DeleteItem
      Resource: !GetAtt TodosTable.Arn
```

### Adding Authentication

For production APIs, consider:

1. **API Gateway Authorizers**:
```yaml
functions:
  api:
    handler: app.main.handler
    events:
      - httpApi:
          path: /api/{proxy+}
          method: any
          authorizer:
            name: jwtAuthorizer
```

2. **JWT Authentication in FastAPI**:
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    # Verify token and return user
    pass

@app.get("/protected")
async def protected_route(user = Depends(get_current_user)):
    return {"message": "You are authenticated"}
```

## Performance Tuning

### Lambda Configuration

Adjust memory and timeout settings in serverless.yml:
```yaml
functions:
  api:
    handler: app.main.handler
    memorySize: 1024  # MB
    timeout: 10  # seconds
```

### Cold Start Optimization

1. Keep dependencies minimal
2. Use slim packaging
3. Consider provisioned concurrency for critical endpoints

```yaml
functions:
  api:
    handler: app.main.handler
    provisionedConcurrency: 5
```

## Monitoring and Debugging

### CloudWatch Logs

All Lambda executions are logged to CloudWatch. View them with:
```bash
npx serverless logs -f api
```

### X-Ray Tracing

Add X-Ray tracing in serverless.yml:
```yaml
provider:
  tracing:
    lambda: true
    apiGateway: true
```

## AWS Service Costs and Monitoring

### Typical Costs for a Serverless API

For learning projects and small-scale APIs, costs are minimal thanks to AWS's free tier:

- **AWS Lambda**: 
  - Free Tier: 1 million free requests per month and 400,000 GB-seconds of compute time
  - Beyond free tier: $0.20 per million requests and $0.0000166667 per GB-second

- **API Gateway**: 
  - Free Tier: 1 million API calls per month for first 12 months
  - Beyond free tier: $3.50 per million API calls

- **CloudWatch Logs**:
  - Free Tier: 5GB of logs storage
  - Beyond free tier: $0.50 per GB ingested, $0.03 per GB stored

### Monitoring Costs

1. **AWS Cost Explorer**:
   - AWS Management Console → Cost Explorer
   - Shows current and forecasted costs
   - Filter by service (Lambda, API Gateway)

2. **AWS Budgets**:
   - Set alerts when costs exceed thresholds
   - AWS Management Console → Billing → Budgets
   - Create a budget with a specified amount
   - Configure email notifications

3. **Removing All Resources**:
   ```bash
   npx serverless remove
   ```
   This command removes all AWS resources created by your Serverless deployment, including:
   - Lambda functions
   - API Gateway configurations
   - IAM roles
   - CloudWatch Log groups

## Common Issues and Solutions

### Lambda Timeouts
- Increase timeout in serverless.yml
- Optimize slow database queries
- Use async/await for I/O operations

### Deployment Failures
- Check IAM permissions
- Verify AWS credentials
- Examine CloudFormation errors in AWS Console

### Package Size Limits
- Use slim packaging
- Remove unnecessary dependencies
- Use layer for large dependencies

### SSH and Git Issues
- Ensure SSH key is properly configured for GitHub
- Match SSH config host names exactly with Git remote URLs
- For multiple GitHub accounts, use separate SSH host aliases
- Test SSH connection with `ssh -T git@github.com-personal`

### Python Environment Issues
- Keep virtual environment isolated (don't commit to git)
- Use `.gitignore` to exclude `__pycache__`, `.pyc` files
- Pay attention to directory structure when using `import` statements

## Understanding How Node.js and Python Work Together

This project uses both Python and Node.js, which might seem confusing at first:

- **Python**: Used for the application code (FastAPI)
- **Node.js**: Used for deployment tooling (Serverless Framework)

### Why Both Languages?

- **Python is excellent for**:
  - Web APIs (FastAPI is fast and intuitive)
  - Data processing
  - Machine learning and AI
  - Readability and development speed

- **Node.js tools are excellent for**:
  - Deployment automation
  - Infrastructure as code
  - Package management for deployment tools
  - Integration with JavaScript-based cloud services

### How They Work Together

1. You write your application code in Python (FastAPI)
2. Serverless Framework (a Node.js tool) handles deployment
3. Your Python code runs on AWS Lambda
4. The Node.js parts are only used during development and deployment

This separation lets you use each language for what it does best. You don't need deep Node.js knowledge - just enough to use the Serverless Framework as a deployment tool.

## Authentication Options for Production APIs

For real-world applications, you'll want proper authentication. Here are the options:

### 1. API Gateway Usage Plans and API Keys

```yaml
provider:
  apiGateway:
    apiKeys:
      - name: client1
      - name: client2
    usagePlan:
      quota:
        limit: 1000
        period: MONTH
      throttle:
        burstLimit: 200
        rateLimit: 100
```

Pros:
- Managed by AWS
- Includes rate limiting
- Simple to implement

Cons:
- Basic authentication only (no user identity)
- Keys must be distributed manually

### 2. JWT Authentication in FastAPI

```python
from fastapi.security import OAuth2PasswordBearer
from jose import jwt

# Setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Endpoint protection
@router.get("/protected")
async def protected(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    # Continue processing...
```

Pros:
- Stateless authentication
- Includes user identity and claims
- Standard protocol with good library support

Cons:
- You must handle token issuance and validation
- Requires key management

### 3. AWS Cognito Integration

```yaml
resources:
  Resources:
    UserPool:
      Type: AWS::Cognito::UserPool
      Properties:
        UserPoolName: ${self:service}-users

functions:
  api:
    handler: app.main.handler
    events:
      - http:
          authorizer:
            type: COGNITO_USER_POOLS
            authorizerId: !Ref ApiGatewayAuthorizer
```

Pros:
- Fully managed user registration and authentication
- Includes features like MFA, social login
- Handles password policies and recovery

Cons:
- More complex setup
- Higher learning curve