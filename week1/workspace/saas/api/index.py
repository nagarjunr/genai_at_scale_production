import os
import logging
from fastapi import FastAPI, Depends  # type: ignore
from fastapi.responses import StreamingResponse  # type: ignore
from fastapi_clerk_auth import ClerkConfig, ClerkHTTPBearer, HTTPAuthorizationCredentials  # type: ignore
from openai import OpenAI  # type: ignore

app = FastAPI()

# Setup logging to catch streaming errors without crashing the server
logger = logging.getLogger(__name__)

# Clerk Configuration
clerk_config = ClerkConfig(jwks_url=os.getenv("CLERK_JWKS_URL"))
clerk_guard = ClerkHTTPBearer(clerk_config)

# Azure / OpenAI Configuration
# Note: Using OpenAI() defaults to environment variables OPENAI_API_KEY
endpoint = "https://poc-arjun-oai.openai.azure.com/openai/v1"
deployment_name = "gpt-5-nano"

@app.get("/api")
def idea(creds: HTTPAuthorizationCredentials = Depends(clerk_guard)):
    # Authenticated user ID available for database logging or rate limiting
    user_id = creds.decoded["sub"] 
    
    client = OpenAI(base_url=endpoint)
    prompt = [{"role": "user", "content": "Reply with a new business idea for AI Agents, formatted with headings, sub-headings and bullet points"}]
    
    stream = client.chat.completions.create(
        model=deployment_name, 
        messages=prompt, 
        stream=True
    )

    def event_stream():
        try:
            for chunk in stream:
                # 1. Initialize text to avoid UnboundLocalError
                text = None
                
                # 2. Safety check for empty choices (common in Azure/OpenAI end-of-stream)
                if chunk.choices and len(chunk.choices) > 0:
                    # 3. Safely get content using getattr to avoid AttributeError
                    text = getattr(chunk.choices[0].delta, "content", None)

                if text:
                    # 4. Standard SSE Formatting
                    # Splitting by newline and yielding individual data packets
                    lines = text.split("\n")
                    for line in lines:
                        # Each line is sent as a 'data' packet
                        yield f"data: {line}\n"
                    
                    # A single newline after 'data' tells SSE the message is complete
                    yield "\n"
                    
            # 5. Optional: Signal the frontend that we are officially done
            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"Stream error for user {user_id}: {e}")
            yield f"data: [ERROR]: {str(e)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")