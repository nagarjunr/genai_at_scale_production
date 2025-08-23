# Our mission

The rest of this file contains prior instructions for converting the Healthcare app built in Days 1-4 into an AWS app with App Runner.

These notes were written for me, not for students. The notes were based on an old version of the app that used Pages Router rather than App Router, and the prior version did not use Tailwind.

Our mission is to convert these into day5.md guide for students: a bulletproof, simple guide, designed for students, picking up from Day 4.

These notes had the following issues:

1. This first built separate docker containers for frontend and backend, before bringing them together. This was unnecessary. All we need to do in this course is built the single docker container for static frontend + backend that serves the static frontend. There was a gotcha also about the docker build not being compatible with Apple Silicon, and I've included that fix below. 

2. We will need to create a .env file based on .env.local, and we should keep note of the AWS_ACCOUNT_ID in the .env file, and we should try to load that rather than having people retype it. We should also be careful to note the region used by the students (AWS_REGION is now a reserved name so don't call it that)

3. There was some issue about the IAM user needing permission to manage their own access keys which needed to be manually fixed - hopefully that means something to you and you can preempt it

So the mission:
Based on the below, write notes for students to convert the Day 4 vercel app into Day 5: Deploy the SaaS app on AWS App Runner
Take out: the separate frontend and backend docker files
Add: A section on cautious budget reporting at the start
Add: A very brief explanation of what App Runner is, and the other key AWS components touched on - just a paragraph for anything we use
Change: Keep the frontend / backend folder structure, but then obviously use our existing subdirectories from day 4 (app router)
Change: no need for 'option A' and 'option B' - just use whatever's relevant to our NextJS deployment (I think CommonJS?)
Keep everything simple, clear and bulletproof.
Be sure to be cross-platform; this needs to work on Windows as well as Mac. (Does Windows need WSL in order to run Docker?)
Be sure this is bulletproof! A beautiful week1/day5.md

# And now - here is the original notes to be used as a rough basis:


# Internal Notes: Migrating from Vercel to AWS App Runner

## Overview
This guide will walk you through migrating your FastAPI + Next.js application from Vercel to AWS App Runner. We'll containerize the application using Docker and deploy it with all the necessary environment variables.

## Part 1: Setting Up AWS Account

### Step 1.1: Create AWS Account
1. Go to [https://aws.amazon.com](https://aws.amazon.com)
2. Click "Create an AWS Account"
3. Enter your email and choose a password
4. Select "Personal" account type (for learning purposes)
5. Enter your payment information (AWS offers free tier services)
6. Verify your phone number
7. Select the "Basic (Free)" support plan

### Step 1.2: Secure Your AWS Account
1. Once logged in, click your account name (top right) → "Security credentials"
2. Enable Multi-Factor Authentication (MFA):
   - Click "Assign MFA device"
   - Choose "Authenticator app"
   - Follow the steps with Google Authenticator or similar app
3. Create an IAM user (don't use root account for daily work):
   - Go to IAM service (search "IAM" in the search bar)
   - Click "Users" → "Create user"
   - Username: `aiengineer`
   - Check "Provide user access to the AWS Management Console"
   - Select "I want to create an IAM user"
   - Choose "Custom password" and set a strong password
   - Uncheck "Users must create a new password at next sign-in"
   - Click "Next"

### Step 1.3: Set IAM User Permissions
1. On the permissions page, select "Attach policies directly"
2. Search and select these policies:
   - `AWSAppRunnerFullAccess`
   - `AmazonEC2ContainerRegistryFullAccess`
   - `CloudWatchLogsFullAccess`
3. Click "Next" → "Create user"
4. Download the credentials CSV file and store it safely

NEW SECTION TO BE ADDED HERE: Set up budget notifications - $1 and $5 and $10

5. Sign out and sign back in using the IAM user credentials

**Check Point**: You should now be logged in as your IAM user (check top right corner)

## Part 2: Install Docker Desktop

### Step 2.1: Download and Install Docker Desktop
1. Go to [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. Download Docker Desktop for your operating system (Windows/Mac)
3. Run the installer and follow the installation wizard
4. After installation, start Docker Desktop
5. You may need to restart your computer

### Step 2.2: Verify Docker Installation
1. Open your terminal (Terminal on Mac, Command Prompt or PowerShell on Windows)
2. Run: `docker --version`
3. You should see something like: `Docker version 26.x.x, build xxxxx`
4. Run: `docker run hello-world`
5. You should see a success message

**Check Point**: Docker Desktop icon should be running in your system tray, and the hello-world test should complete successfully

## Part 3: Prepare Your Application

### Step 3.1: Remove Vercel-Specific Files
In your project root, delete these files:
- `vercel.json`
- `.vercel` folder (if it exists)

### Step 3.2: Restructure Your Application
Create the following folder structure:
```
your-project/
├── backend/
│   ├── server.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── pages/
│   ├── styles/
│   ├── public/
│   ├── package.json
│   ├── package-lock.json
│   ├── next.config.js
│   ├── tsconfig.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.local
└── .gitignore
```

Move files:
- Move `api/server.py` to `backend/server.py`
- Move `requirements.txt` to `backend/requirements.txt`
- Move all Next.js files (pages, styles, package.json, etc.) to `frontend/`

### Step 3.3: Update server.py
Edit `backend/server.py` to add CORS support and update the route:

```python
import os
from pathlib import Path
from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi_clerk_auth import ClerkConfig, ClerkHTTPBearer, HTTPAuthorizationCredentials
from openai import OpenAI

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

clerk_guard = ClerkHTTPBearer(ClerkConfig(jwks_url=os.getenv("CLERK_JWKS_URL")))

# ... (your existing Visit model and functions) ...

@app.post("/api/consultation")
def consultation_summary(
    visit: Visit,
    creds: HTTPAuthorizationCredentials = Depends(clerk_guard),
):
    # ... (your existing implementation) ...

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Serve the static files - must be last
static_path = Path("static")
if static_path.exists():
    # Serve index.html for the root path
    @app.get("/")
    async def serve_root():
        return FileResponse(static_path / "index.html")
    
    # Mount static files for all other routes
    app.mount("/", StaticFiles(directory="static", html=True), name="static")
```

### Step 3.4: Update frontend API call
Edit `frontend/pages/product.tsx` to update the API endpoint:

```typescript
// Find this line in handleSubmit function:
await fetchEventSource('/api', {

// Change it to:
await fetchEventSource(`${process.env.NEXT_PUBLIC_API_URL}/api/consultation`, {
```

### Step 3.5: Create next.config.js
Create `frontend/next.config.js` (use the appropriate format based on your package.json):

**Option A: If your package.json has `"type": "module"` (ES modules)**:
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
}

export default nextConfig
```

**Option B: If your package.json doesn't have `"type": "module"` (CommonJS)**:
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
}

module.exports = nextConfig
```

**To check which one you need**: Look in your `frontend/package.json` for a line that says `"type": "module"`. If it's there, use Option A. If not, use Option B.

## Part 4: Create Docker Configuration

### Step 4.1: Create Backend Dockerfile
Create `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY server.py .

# Expose port
EXPOSE 8000

# Start the application
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 4.2: Create Frontend Dockerfile
Create `frontend/Dockerfile`:

```dockerfile
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Accept build arguments and set them as environment variables
ARG NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=$NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Create public directory if it doesn't exist
RUN mkdir -p public

# Copy public folder if it exists in builder stage
RUN --mount=type=bind,from=builder,source=/app,target=/tmp/app \
    if [ -d "/tmp/app/public" ]; then cp -r /tmp/app/public/* ./public/ 2>/dev/null || true; fi

# Copy standalone output
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000

CMD ["node", "server.js"]
```

### Step 4.3: Create docker-compose.yml
Create `docker-compose.yml` in your project root:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - CLERK_JWKS_URL=${CLERK_JWKS_URL}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/docs"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build: 
      context: ./frontend
      args:
        - NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=${NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY}
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=${NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY}
      - CLERK_SECRET_KEY=${CLERK_SECRET_KEY}
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend
```

### Step 4.4: Update .env.local
Make sure your `.env.local` file has all these variables:
```
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
CLERK_JWKS_URL=https://...
OPENAI_API_KEY=sk-...
```

## Part 5: Test Locally with Docker

### Step 5.1: Build and Run with Docker Compose
1. Make sure your `.env` file is in the project root (same directory as docker-compose.yml)
2. Open terminal in your project root
3. Run: `docker-compose build`
   - This will take a few minutes the first time
   - You should see both frontend and backend building successfully
4. Run: `docker-compose up`
   - You should see logs from both services
   - Look for "Uvicorn running on http://0.0.0.0:8000" for backend
   - Look for "Ready on http://localhost:3000" for frontend

**Note**: If you still get the Clerk publishable key error during build, you can also try:
```bash
docker-compose build --no-cache
```

Or explicitly load the .env file:
```bash
docker-compose --env-file .env build
```

### Step 5.2: Test Your Application
1. Open your browser to `http://localhost:3000`
2. You should see the Clerk sign-in page
3. Sign in and test the consultation notes feature
4. Check the terminal for any error messages

**Check Point**: Application should work exactly as it did on Vercel

### Step 5.3: Stop the Application
Press `Ctrl+C` in the terminal to stop the containers

## Part 6: Prepare for AWS App Runner

### Step 6.1: Create a Single Container Setup
Since AWS App Runner works best with single containers, create a new structure:

Create `Dockerfile.production` in your project root:

```dockerfile
# Build frontend
FROM node:22-alpine AS frontend-build
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .

ARG NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
ENV NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=$NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY

RUN npm run build

# Production image
FROM python:3.12-slim
WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend
COPY backend/server.py .

# Copy Next.js static export (now in 'out' directory)
COPY --from=frontend-build /app/out ./static

EXPOSE 8000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```



### Step 6.3: Build and Test Production Container
1. Build with build arguments: 
```bash
docker build -f Dockerfile.production \
  --build-arg NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="$NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY" \
  -t consultation-app .
```

2. Run: 
```bash
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="$NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY" \
  -e CLERK_SECRET_KEY="$CLERK_SECRET_KEY" \
  -e CLERK_JWKS_URL="$CLERK_JWKS_URL" \
  -e OPENAI_API_KEY="$OPENAI_API_KEY" \
  consultation-app
```

3. Test at `http://localhost:3000`

**Note**: Make sure to source your .env file first:
```bash
# On Mac/Linux:
export $(cat .env | xargs)

# Or manually set for Windows PowerShell:
$env:NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="your_key_here"
```

**Check Point**: Single container should run both services successfully

## Part 7: Deploy to AWS App Runner

### Step 7.1: Push to Amazon ECR
1. In AWS Console, search for "ECR" and go to Elastic Container Registry
2. Click "Create repository"
3. Repository name: `consultation-app`
4. Leave other settings as default
5. Click "Create repository"

### Step 7.2: Push Your Image to ECR
1. Click on your new repository
2. Click "View push commands"
3. **Before running the commands, you need to set up AWS CLI credentials:**

   a. **Create Access Keys for your IAM user:**
   - In AWS Console, go to IAM (search "IAM" in search bar)
   - Click "Users" in the left sidebar
   - Click on your user (`aiengineer`)
   - Click the "Security credentials" tab
   - Scroll down to "Access keys" section
   - Click "Create access key"
   - Select "Command Line Interface (CLI)"
   - Check the confirmation box and click "Next"
   - Add a description like "AWS CLI on my computer"
   - Click "Create access key"
   - **IMPORTANT**: Download the CSV file or copy both:
     - Access key ID (looks like: `AKIAIOSFODNN7EXAMPLE`)
     - Secret access key (looks like: `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`)
   - Click "Done"

   b. **Configure AWS CLI:**
   ```bash
   aws configure
   ```
   When prompted, enter:
   - AWS Access Key ID: (paste your access key ID)
   - AWS Secret Access Key: (paste your secret access key)
   - Default region name: `us-east-1` (or your chosen region)
   - Default output format: `json` (or just press Enter)

4. **Now run the 4 push commands** (they'll look something like this):
   ```bash
   # 1. Authenticate Docker to ECR
   aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin [your-account-id].dkr.ecr.us-east-2.amazonaws.com

   # 2. Build specifically for AMD64/x86_64 - IMPORTANT otherwise Apple Silicon will fail

docker build -f Dockerfile.production \
  --platform linux/amd64 \
  --build-arg NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="$NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY" \
  -t consultation-app .

   docker build -f Dockerfile.production \
     --build-arg NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="$NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY" \
     -t consultation-app .

   # 3. Tag your image
   docker tag consultation-app:latest [your-account-id].dkr.ecr.us-east-2.amazonaws.com/consultation-app:latest

   # 4. Push to ECR
   docker push [your-account-id].dkr.ecr.us-east-2.amazonaws.com/consultation-app:latest
   ```

**Security Note**: Never share your secret access key! Treat it like a password. If you accidentally expose it, immediately go back to IAM and delete the access key.

### Step 7.3: Create App Runner Service
1. In AWS Console, search for "App Runner"
2. Click "Create service"
3. Source:
   - Select "Container registry"
   - Select "Amazon ECR"
   - Click "Browse" and select your `consultation-app` repository
   - Select the `latest` tag
   - Click "Next"

### Step 7.4: Configure Deployment
1. Deployment settings:
   - Deployment trigger: "Manual" (for cost control)
   - ECR access role: "Create new service role"
   - Click "Next"

### Step 7.5: Configure Service
1. Service settings:
   - Service name: `consultation-app-service`
   - CPU: `0.25 vCPU`
   - Memory: `0.5 GB`
   - Port: `8000` (changed from 3000!)
   
2. Environment variables - Add these:
   - `CLERK_SECRET_KEY` = (your value)
   - `CLERK_JWKS_URL` = (your value)
   - `OPENAI_API_KEY` = (your value)
   
   Note: We don't need `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` here since it's baked into the static files during build.

3. Auto scaling:
   - Min size: `1`
   - Max size: `1` (to control costs)

4. Health check:
   - Path: `/health`
   - Protocol: `HTTP`
   - Interval: `10` seconds
   - Timeout: `5` seconds
   - Healthy threshold: `1`
   - Unhealthy threshold: `5`

5. Click "Next"

### Step 7.6: Review and Create
1. Review all settings
2. Click "Create & deploy"
3. Wait for deployment (this takes 5-10 minutes)
4. Watch the "Event log" for progress

**Check Point**: Status should change to "Running" and show a green checkmark

### Step 7.7: Access Your Application
1. Once running, click on the "Default domain" URL
2. Your application should load with HTTPS enabled automatically
3. Test all functionality

## Part 8: Monitoring and Logs

### Step 8.1: View Application Logs
1. In your App Runner service, click on the "Logs" tab
2. Select "Application logs" to see your app output
3. Select "System logs" to see deployment information

### Step 8.2: CloudWatch Integration
1. Click "View in CloudWatch" for detailed logs
2. You can set up alerts here for errors or performance issues

## Part 9: Updating Your Application

When you make changes:

1. Rebuild your Docker image:
   ```bash
   docker build -f Dockerfile.production -t consultation-app .
   ```

2. Tag and push to ECR:
   ```bash
   docker tag consultation-app:latest [your-account-id].dkr.ecr.us-east-1.amazonaws.com/consultation-app:latest
   docker push [your-account-id].dkr.ecr.us-east-1.amazonaws.com/consultation-app:latest
   ```

3. In App Runner console:
   - Go to your service
   - Click "Deploy"
   - Wait for the new deployment to complete

## Troubleshooting Tips

### Common Issues:

1. **"Cannot connect to backend"**
   - Check that `NEXT_PUBLIC_API_URL` is set to `http://localhost:8000`
   - Verify both services are running in the logs

2. **"Authentication failed"**
   - Double-check all Clerk environment variables
   - Ensure they're set in App Runner configuration

3. **"Out of memory" errors**
   - Increase memory in App Runner configuration to 1GB

4. **Slow cold starts**
   - This is normal for App Runner
   - Consider keeping minimum instances at 1

### Debugging Commands:

Test environment variables locally:
```bash
docker run -p 3000:3000 \
  --env-file .env.local \
  consultation-app
```

Check container logs:
```bash
docker logs [container-id]
```

## Cost Considerations

With the settings recommended:
- 0.25 vCPU, 0.5 GB memory, 1 instance
- Estimated cost: ~$5-10/month for light usage
- First 3 months may be covered by AWS free tier

To minimize costs:
- Set auto-scaling max to 1
- Use manual deployments
- Monitor usage in AWS Cost Explorer

## Security Best Practices

1. Never commit `.env.local` to git
2. Use AWS Secrets Manager for production (advanced)
3. Restrict ECR repository access
4. Enable App Runner access logs
5. Regularly update dependencies

## Next Steps

1. Set up a custom domain in App Runner
2. Configure auto-deployments with GitHub Actions
3. Add error monitoring (e.g., Sentry)
4. Implement caching for better performance
5. Consider using RDS for data persistence

## Conclusion

Congratulations! You've successfully migrated your application from Vercel to AWS App Runner. The application is now running in a containerized environment with automatic HTTPS, scaling capabilities, and integrated monitoring.

Remember to:
- Check CloudWatch logs regularly
- Monitor your AWS billing dashboard
- Keep your Docker images updated
- Test thoroughly after each deployment

For questions or issues, check the AWS App Runner documentation or the AWS forums.