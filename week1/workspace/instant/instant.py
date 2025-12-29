from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from openai import OpenAI

app = FastAPI()

endpoint = "https://poc-arjun-oai.openai.azure.com/openai/v1"
deployment_name = "gpt-5-nano"

@app.get("/", response_class=HTMLResponse)
def instant():
    client = OpenAI(
        base_url=endpoint
    )
    message = """
You are on a website that has just been deployed to production for the first time!
Please reply with an enthusiastic announcement to welcome visitors to the site, explaining that it is live on production for the first time!
"""
    messages = [{"role": "user", "content": message}]
    response = client.chat.completions.create(model=deployment_name, messages=messages)
    reply = response.choices[0].message.content.replace("\n", "<br/>")
    html = f"<html><head><title>Live in an Instant!</title></head><body><p>{reply}</p></body></html>"
    return html