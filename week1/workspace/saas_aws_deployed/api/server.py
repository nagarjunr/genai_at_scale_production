import os
import logging
from pathlib import Path
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi_clerk_auth import ClerkConfig, ClerkHTTPBearer, HTTPAuthorizationCredentials
from openai import OpenAI
import requests
from starlette.middleware.base import BaseHTTPMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add middleware to log all authentication errors
class AuthLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            if response.status_code == 403:
                auth_header = request.headers.get("Authorization", "")
                logger.error(f"403 Forbidden on {request.url.path}")
                logger.error(f"Authorization header present: {bool(auth_header)}")
                logger.error(f"Request host: {request.headers.get('host')}")
                logger.error(f"Origin: {request.headers.get('origin', 'not present')}")
            return response
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}", exc_info=True)
            raise

app.add_middleware(AuthLoggingMiddleware)

# Azure / OpenAI Configuration
endpoint = "https://poc-arjun-oai.openai.azure.com/openai/v1"
deployment_name = "gpt-5-nano"

# Add CORS middleware (allows frontend to call backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Clerk authentication setup
jwks_url = os.getenv('CLERK_JWKS_URL')
logger.info(f"Initializing Clerk with JWKS URL: {jwks_url}")
logger.info(f"Environment: AWS App Runner (no proxy needed)")

'''
# To test the proxy settings, we can attempt to fetch the JWKS directly
# Configure proxy settings for requests - USE PROXY for DNS resolution in corporate network
http_proxy = os.getenv('http_proxy') or os.getenv('HTTP_PROXY')
https_proxy = os.getenv('https_proxy') or os.getenv('HTTPS_PROXY')

proxies = {}
if http_proxy:
    proxies['http'] = http_proxy
if https_proxy:
    proxies['https'] = https_proxy

# logger.info(f"Using proxy for all external requests including Clerk: {proxies}")

try:
    # Test if we can reach the JWKS endpoint through the proxy
    # logger.info(f"Attempting to fetch JWKS from {jwks_url} through proxy")
    response = requests.get(jwks_url, timeout=30, proxies=proxies, verify=True)
    # logger.info(f"Successfully fetched JWKS, status: {response.status_code}")
    jwks_data = response.json()
    # logger.info(f"JWKS keys count: {len(jwks_data.get('keys', []))}")
except Exception as e:
    # logger.error(f"Failed to fetch JWKS from {jwks_url}: {str(e)}", exc_info=True)
    # logger.error(f"This will cause authentication to fail. Check proxy settings and network connectivity.")
    pass
'''
try:
    # Initialize Clerk
    clerk_config = ClerkConfig(jwks_url=jwks_url)
    clerk_guard = ClerkHTTPBearer(clerk_config)
    logger.info("Clerk authentication initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Clerk: {str(e)}", exc_info=True)
    pass

class Visit(BaseModel):
    patient_name: str
    date_of_visit: str
    notes: str

system_prompt = """
You are provided with notes written by a doctor from a patient's visit.
Your job is to summarize the visit for the doctor and provide an email.
Reply with exactly three sections with the headings:
### Summary of visit for the doctor's records
### Next steps for the doctor
### Draft of email to patient in patient-friendly language
"""

def user_prompt_for(visit: Visit) -> str:
    return f"""Create the summary, next steps and draft email for:
Patient Name: {visit.patient_name}
Date of Visit: {visit.date_of_visit}
Notes:
{visit.notes}"""

@app.post("/api/consultation")
async def consultation_summary(
    request: Request,
    visit: Visit,
    creds: HTTPAuthorizationCredentials = Depends(clerk_guard),
):
    # Log authentication details
    auth_header = request.headers.get("Authorization", "")
    logger.info(f"Received consultation request for patient: {visit.patient_name}")
    logger.info(f"Authorization header present: {bool(auth_header)}")
    
    try:
        user_id = creds.decoded["sub"]
        azp = creds.decoded.get("azp", "not present")
        logger.info(f"Successfully authenticated user: {user_id}")
        logger.info(f"Token azp (authorized party): {azp}")
        logger.info(f"Request host: {request.headers.get('host', 'unknown')}")
    except Exception as e:
        logger.error(f"Failed to decode JWT credentials: {str(e)}", exc_info=True)
        raise HTTPException(status_code=403, detail="Authentication failed")
    
    client = OpenAI(base_url=endpoint)
    
    user_prompt = user_prompt_for(visit)
    prompt = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    
    stream = client.chat.completions.create(
        model="gpt-5-nano",
        messages=prompt,
        stream=True,
    )
    
    def event_stream():
        for chunk in stream:
            # Check if chunk has choices before accessing
            if chunk.choices and len(chunk.choices) > 0:
                text = chunk.choices[0].delta.content
                if text:
                    lines = text.split("\n")
                    for line in lines[:-1]:
                        yield f"data: {line}\n\n"
                        yield "data:  \n"
                    yield f"data: {lines[-1]}\n\n"
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")

@app.get("/health")
def health_check():
    """Health check endpoint for AWS App Runner"""
    # logger.info("Health check endpoint called")
    return {"status": "healthy"}

# Serve static files (our Next.js export) - MUST BE LAST!
static_path = Path("static")
if static_path.exists():
    # Serve index.html for the root path
    @app.get("/")
    async def serve_root():
        return FileResponse(static_path / "index.html")
    
    # Mount static files for all other routes
    app.mount("/", StaticFiles(directory="static", html=True), name="static")