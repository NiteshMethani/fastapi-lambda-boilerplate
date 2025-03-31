# FastAPI Lambda Boilerplate

A production-ready FastAPI application template designed for deployment to AWS Lambda using the Serverless Framework.

## Project Overview

This boilerplate provides:
- A feature-based project structure
- Configured AWS Lambda deployment
- Automated API Gateway setup
- Local development environment

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 14+ (for Serverless Framework)
- AWS account with credentials

### Local Development

1. **Setup virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   npm install
   ```

3. **Run locally**
   ```bash
   python dev.py
   ```
   
   Access your API at:
   - http://localhost:8000/api/hello
   - http://localhost:8000/api/hello?name=YourName
   - http://localhost:8000/api/health

### Deployment

1. **Configure AWS credentials**
   ```bash
   # Set environment variables
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   # OR
   aws configure
   ```

2. **Deploy to AWS Lambda**
   ```bash
   npx serverless deploy
   ```

3. **Remove deployment**
   ```bash
   npx serverless remove
   ```

## Project Structure

```
fastapi-lambda-boilerplate/
├── app/                          # Main application package
│   ├── __init__.py
│   ├── main.py                   # FastAPI application creation and settings
│   └── api/                      # API endpoints
│       ├── __init__.py
│       ├── routes.py             # Main router that includes feature routers
│       ├── hello/                # Hello endpoint feature
│       │   ├── __init__.py
│       │   ├── router.py         # API routes for hello feature
│       │   ├── schemas.py        # Request/response models
│       │   └── service.py        # Business logic
│       └── health/               # Health check feature
│           ├── __init__.py
│           ├── router.py         # API routes for health check
│           └── schemas.py        # Response models
├── dev.py                        # Local development script
├── serverless.yml                # Serverless Framework configuration
├── requirements.txt              # Python dependencies
├── package.json                  # Node.js dependencies
└── .env                          # Environment variables (not in version control)
```

## Adding a New Feature

1. Create a new directory in `app/api/` with your feature name
2. Add the necessary files:
   - `__init__.py`
   - `router.py` - API endpoints
   - `schemas.py` - Pydantic models
   - `service.py` - Business logic (if needed)
3. Include your feature router in `app/api/routes.py`

## Development Cheatsheet

### FastAPI Commands
```bash
# Run local development server
python dev.py

# Access API docs
# Visit http://localhost:8000/docs in your browser
```

### Serverless Commands
```bash
# Deploy to AWS
npx serverless deploy

# Deploy to a specific stage
npx serverless deploy --stage prod

# View deployed service information
npx serverless info

# View logs
npx serverless logs -f api

# Remove the deployed service
npx serverless remove
```

### Testing Your API
```bash
# Replace with your actual API Gateway URL
export BASE_URL="https://abcdef123.execute-api.us-east-1.amazonaws.com"

# Test endpoints
curl $BASE_URL/api/hello
curl "$BASE_URL/api/hello?name=YourName"
curl $BASE_URL/api/health
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request