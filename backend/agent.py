from pathlib import Path
import os
import json
from functools import wraps

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from models import AuditEntry, ChatDeps, ChatReply
from tools import get_current_product, get_inventory, get_product_details, search_products

ROOT = Path(__file__).resolve().parent
AUDIT_FILE = ROOT.parent / "output" / "audit_trail.json"
PROMPT = (ROOT / "prompts" / "prompt.md").read_text()

for line in (ROOT.parent.parent / ".env").read_text().splitlines():
    if "=" in line and not line.lstrip().startswith("#"):
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())

provider = OpenAIProvider(api_key=os.environ["PORTKEY_API_KEY"], base_url="https://api.portkey.ai/v1")
agent = Agent(OpenAIChatModel("gpt-5.6-luna", provider=provider), system_prompt=PROMPT, output_type=ChatReply, deps_type=ChatDeps)


@agent.system_prompt
def shopper_context(ctx: RunContext[ChatDeps]) -> str:
    identity = f"Signed-in shopper: {ctx.deps.first_name} {ctx.deps.last_name} ({ctx.deps.email})." if ctx.deps.user_id else "Guest shopper: no account identity is available."
    page = f"Current page context: {ctx.deps.page_context}. Use this product/page context when the shopper says 'this' or 'it'." if ctx.deps.page_context else "No page context was provided."
    return f"{identity}\n{page}"
def _audit(entry: AuditEntry) -> None:
    AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry.model_dump(mode="json"), ensure_ascii=False) + "\n")


def _short(value: object, limit: int = 240) -> str:
    text = str(value)
    return text if len(text) <= limit else text[:limit - 3] + "..."


def _logged_tool(function, name: str):
    @wraps(function)
    def call(*args, **kwargs):
        _audit(AuditEntry(event="tool_call", tool_name=name, args=_short({"args": args, "kwargs": kwargs})))
        try:
            result = function(*args, **kwargs)
            _audit(AuditEntry(event="tool_result", tool_name=name, result=_short(result)))
            return result
        except Exception as error:
            _audit(AuditEntry(event="tool_error", tool_name=name, result=_short(error), stop_reason="tool_error"))
            raise
    call.__name__ = name
    call.__doc__ = function.__doc__
    return call


agent.tool_plain(_logged_tool(search_products, "search_products"))
agent.tool_plain(_logged_tool(get_product_details, "get_product_details"))
agent.tool_plain(_logged_tool(get_inventory, "get_inventory"))
agent.tool_plain(_logged_tool(get_current_product, "get_current_product"))


def chat(message: str, deps: ChatDeps, history: list[dict] | None = None) -> ChatReply:
    _audit(AuditEntry(event="run_start", args=_short({"message": message, "page_context": deps.page_context}), stop_reason=None))
    prior = "\n".join(f"{item['role']}: {item['content']}" for item in (history or [])[-10:])
    context_message = f"{message}\n\nRecent conversation:\n{prior}" if prior else message
    try:
        result = agent.run_sync(context_message, deps=deps)
        _audit(AuditEntry(event="run_stop", result=_short(result.output), stop_reason="completed"))
        return result.output
    except Exception as error:
        _audit(AuditEntry(event="run_stop", result=_short(error), stop_reason="error"))
        raise
