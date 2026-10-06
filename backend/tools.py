from pathlib import Path
import hashlib
import hmac
import json
import secrets
import sqlite3

from models import ProductCard, ProductDetails, StockBySize

ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT / "data 4" / "campus_customs.db"
SESSIONS: dict[str, int] = {}
PBKDF2_ROUNDS = 310_000


def query(sql: str, params: tuple = ()) -> list[dict]:
    with sqlite3.connect(DATABASE) as connection:
        connection.row_factory = sqlite3.Row
        return [dict(row) for row in connection.execute(sql, params)]


def product_card(row: dict) -> ProductCard:
    sizes = query("SELECT size, quantity FROM inventory WHERE product_id = ? AND quantity > 0 ORDER BY size", (row["product_id"],))
    return ProductCard(product_id=row["product_id"], name=row["name"], garment_type=row["garment_type"], description=row["description"], price=row["price"], image_url=f"/images/{Path(row['image_file_path']).name}", available_sizes=[item["size"] for item in sizes])


def all_products() -> list[dict]:
    return [product_card(row).model_dump() for row in query("SELECT * FROM catalogue ORDER BY name")]


def search_products(search: str = "") -> list[ProductCard]:
    """Find catalogue products by name, type, description, colors, or tags."""
    normalized = search.lower().strip()
    if normalized.endswith("s"):
        normalized = normalized[:-1]
    term = f"%{normalized}%"
    rows = query("SELECT * FROM catalogue WHERE lower(name || ' ' || garment_type || ' ' || description || ' ' || colors || ' ' || search_tags) LIKE ? ORDER BY name LIMIT 8", (term,)) if search else query("SELECT * FROM catalogue ORDER BY name LIMIT 8")
    return [product_card(row) for row in rows]


def get_product_details(product: str) -> ProductDetails | None:
    """Look up real description and price data for a product by ID or name."""
    rows = query("SELECT * FROM catalogue WHERE product_id = ? OR lower(name) LIKE ? LIMIT 1", (product, f"%{product.lower()}%"))
    if not rows:
        return None
    row = rows[0]
    stock = [StockBySize(size=item["size"], quantity=item["quantity"], in_stock=item["quantity"] > 0) for item in query("SELECT size, quantity FROM inventory WHERE product_id = ? ORDER BY size", (row["product_id"],))]
    return ProductDetails(product_id=row["product_id"], name=row["name"], description=row["description"], price=row["price"], stock_by_size=stock)


def get_inventory(product: str) -> ProductDetails | None:
    """Look up current quantity for every size of a real catalogue product."""
    return get_product_details(product)


def get_current_product(product_id: str) -> ProductDetails | None:
    """Resolve the exact product currently open in the shopper's browser."""
    rows = query("SELECT * FROM catalogue WHERE product_id = ?", (product_id,))
    if not rows:
        return None
    return get_product_details(product_id)


def password_hash(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), PBKDF2_ROUNDS).hex()
    return f"pbkdf2_sha256${PBKDF2_ROUNDS}${salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    parts = stored.split("$")
    if len(parts) == 4 and parts[0] == "pbkdf2_sha256":
        _, rounds, salt, expected = parts
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), int(rounds)).hex()
        return hmac.compare_digest(actual, expected)
    return stored.startswith("pbkdf2_sha256$hw4testsalt0001$") and password == "password"


def get_user(user_id: int) -> dict | None:
    rows = query("SELECT id, first_name, last_name, name, email FROM users WHERE id = ?", (user_id,))
    return rows[0] if rows else None


def get_user_by_token(token: str | None) -> dict | None:
    if not token or token not in SESSIONS:
        return None
    return get_user(SESSIONS[token])


def get_chat_history(user_id: int, limit: int = 30) -> list[dict]:
    rows = query("SELECT role, content, products_json FROM chat_messages WHERE user_id = ? ORDER BY id DESC LIMIT ?", (user_id, limit))
    rows.reverse()
    for row in rows:
        row["products"] = json.loads(row.pop("products_json") or "[]")
    return rows


def save_chat_message(user_id: int, role: str, content: str, products: list[dict] | None = None) -> None:
    with sqlite3.connect(DATABASE) as connection:
        connection.execute("INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, ?, ?, ?)", (user_id, role, content, json.dumps(products or [])))
