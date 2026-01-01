# Stage 1: Build the Next.js static files
FROM node:22.13-alpine AS frontend-builder

WORKDIR /app

#To run in local docker
# ARG http_proxy="http://rb-proxy-na.bosch.com:8080"
# ARG https_proxy="http://rb-proxy-na.bosch.com:8080"
# ARG HTTP_PROXY="http://rb-proxy-na.bosch.com:8080"
# ARG HTTPS_PROXY="http://rb-proxy-na.bosch.com:8080"

# Copy package files first (for better caching)
COPY package*.json ./
RUN npm ci

# Copy all frontend files
COPY . .

# Build argument for Clerk public key
ARG NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
ENV NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=$NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY

# Note: Docker may warn about "secrets in ARG/ENV" - this is OK!
# The NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY is meant to be public (it starts with pk_)
# It's safe to include in the build as it's designed for client-side use

# Build the Next.js app (creates 'out' directory with static files)
RUN npm run build

# Stage 2: Create the final Python container
FROM python:3.12-slim

WORKDIR /app

#To run in local docker
# ARG http_proxy="http://rb-proxy-na.bosch.com:8080"
# ARG https_proxy="http://rb-proxy-na.bosch.com:8080"
# ARG HTTP_PROXY="http://rb-proxy-na.bosch.com:8080"
# ARG HTTPS_PROXY="http://rb-proxy-na.bosch.com:8080"

# Fix SSL_CERTS CERTIFICATE_VERIFY_FAILED issue - Not needed, just proxy variables should be enough
# RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org certifi
# RUN CACERT_PATH=$(python -c "import certifi; print(certifi.where())") && \
#     echo "Found cacert.pem at: $CACERT_PATH" && \
#     echo "export REQUESTS_CA_BUNDLE=$CACERT_PATH" >> /etc/profile.d/requests_ca_bundle.sh && \
#     echo "$CACERT_PATH" > /tmp/cacert_path.txt
# # ENV REQUESTS_CA_BUNDLE=/tmp/cacert_path.txt
# # RUN export REQUESTS_CA_BUNDLE=$(cat /tmp/cacert_path.txt)
# COPY ./certs/* /app/certs/
# RUN python /app/certs/update_certs_python.py

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI server
COPY api/server.py .

# Copy the Next.js static export from builder stage
COPY --from=frontend-builder /app/out ./static

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Expose port 8000 (FastAPI will serve everything)
EXPOSE 8000

# Start the FastAPI server
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]