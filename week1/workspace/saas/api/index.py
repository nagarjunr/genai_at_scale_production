from fastapi import FastAPI # type: ignore
from fastapi.responses import StreamingResponse # type: ignore
from openai import OpenAI # type: ignore
import logging

app = FastAPI()

# Setup basic logging to see errors in your terminal/logs instead of crashing the stream
logger = logging.getLogger(__name__)

endpoint = "https://poc-arjun-oai.openai.azure.com/openai/v1"
deployment_name = "gpt-5-nano"

@app.get("/api")
def idea():
    client = OpenAI(base_url=endpoint)
    prompt = [{"role": "user", "content": "Reply with a new business idea for AI Agents, formatted with headings, sub-headings and bullet points"}]
    
    # We call the API outside the generator to catch immediate connection issues
    stream = client.chat.completions.create(
        model=deployment_name, 
        messages=prompt, 
        stream=True
    )

    def event_stream():
        try:
            for chunk in stream:
                # 1. Safely navigate the nested object
                if not chunk.choices:
                    continue
                
                delta = chunk.choices[0].delta
                text = getattr(delta, "content", None)

                if text:
                    # 2. Format as valid Server-Sent Events
                    lines = text.split("\n")
                    for line in lines:
                        yield f"data: {line}\n"
                    yield "\n" # SSE message separator
                    
        except Exception as e:
            # 3. Log the error and send a final error message to the frontend
            logger.error(f"Stream error: {e}")
            yield f"data: [ERROR]: {str(e)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")