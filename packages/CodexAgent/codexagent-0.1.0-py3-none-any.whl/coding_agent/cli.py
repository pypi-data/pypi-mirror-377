from fastapi import FastAPI, Request
from rich.console import Console

from coding_agent.types.gitea import GiteaWebhookPayload
from coding_agent.types.headers import WebhookHeaders

app = FastAPI()
console = Console()


@app.post("/webhook")
async def handle_webhook(request: Request) -> dict[str, str]:
    headers = WebhookHeaders(**dict(request.headers))
    if "Go" not in headers.user_agent:
        return {"status": "ignored"}

    body_dict = await request.json()
    payload = GiteaWebhookPayload(**body_dict)
    payload.save("./logs/webhook_payload.json")
    if payload.action is None:
        return {"status": "no action"}
    console.print(payload)
    return {"status": "received"}
