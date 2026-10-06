from pathlib import Path
import sqlite3
import secrets

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from agent import chat
from models import ChatDeps, ChatMessage, ChatRequest, LoginRequest, RegisterRequest
from tools import DATABASE, SESSIONS, all_products, get_chat_history, get_user_by_token, password_hash, query, save_chat_message, verify_password, product_card

ROOT = Path(__file__).resolve().parents[1]
PRODUCT_IMAGES = ROOT / "data 4" / "products"

app = FastAPI(title="Campus Customs API")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174", "http://localhost:5175", "http://127.0.0.1:5175", "http://localhost:5176", "http://127.0.0.1:5176"], allow_methods=["*"], allow_headers=["*"])
app.mount("/images", StaticFiles(directory=PRODUCT_IMAGES), name="images")


def public_user(row: dict) -> dict:
    return {"id": row["id"], "first_name": row.get("first_name") or row["name"], "last_name": row.get("last_name") or "", "email": row["email"]}


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/products")
def products() -> list[dict]:
    return all_products()


@app.get("/api/products/{product_id}")
def product(product_id: str) -> dict:
    rows = query("SELECT * FROM catalogue WHERE product_id = ?", (product_id,))
    if not rows:
        raise HTTPException(status_code=404, detail="Product not found")
    result = product_card(rows[0]).model_dump()
    result["sizes"] = query("SELECT size, quantity FROM inventory WHERE product_id = ? ORDER BY size", (product_id,))
    return result


@app.post("/api/chat")
def chat_route(request: ChatRequest):
    user = get_user_by_token(request.access_token)
    history = get_chat_history(user["id"]) if user else []
    deps = ChatDeps(user_id=user["id"] if user else None, first_name=user.get("first_name") if user else None, last_name=user.get("last_name") if user else None, email=user.get("email") if user else None, page_context=request.page_context)
    result = chat(request.message, deps, history)
    payload = result.model_dump()
    if user:
        save_chat_message(user["id"], "user", request.message)
        save_chat_message(user["id"], "assistant", result.reply, payload["products"])
    return payload


@app.get("/api/chat/history", response_model=list[ChatMessage])
def chat_history(access_token: str | None = None):
    user = get_user_by_token(access_token)
    return get_chat_history(user["id"]) if user else []


@app.post("/api/auth/register", status_code=201)
def register(request: RegisterRequest) -> dict:
    if request.password != request.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    email = str(request.email).lower()
    if query("SELECT id FROM users WHERE lower(email) = ?", (email,)):
        raise HTTPException(status_code=409, detail="An account with that email already exists")
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.execute("INSERT INTO users (name, email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?, ?)", (f"{request.first_name} {request.last_name}", email, password_hash(request.password), request.first_name, request.last_name))
        user_id = cursor.lastrowid
    token = secrets.token_urlsafe(32)
    SESSIONS[token] = user_id
    return {"access_token": token, "user": {"id": user_id, "first_name": request.first_name, "last_name": request.last_name, "email": email}}


@app.post("/api/auth/login")
def login(request: LoginRequest) -> dict:
    email = str(request.email).lower()
    rows = query("SELECT * FROM users WHERE lower(email) = ?", (email,))
    if not rows or not verify_password(request.password, rows[0]["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if rows[0]["password_hash"].startswith("pbkdf2_sha256$hw4testsalt0001$"):
        with sqlite3.connect(DATABASE) as connection:
            connection.execute("UPDATE users SET password_hash = ? WHERE id = ?", (password_hash(request.password), rows[0]["id"]))
    token = secrets.token_urlsafe(32)
    SESSIONS[token] = rows[0]["id"]
    return {"access_token": token, "user": public_user(rows[0])}
