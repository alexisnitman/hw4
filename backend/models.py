from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr, Field


class AuditEntry(BaseModel):
    """One append-only JSONL record for an agent run or tool call."""
    time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event: str
    tool_name: str | None = None
    args: str = ""
    result: str = ""
    stop_reason: str | None = None


class ProductCard(BaseModel):
    product_id: str
    name: str
    garment_type: str
    description: str
    price: float
    image_url: str
    available_sizes: list[str] = Field(default_factory=list)


class StockBySize(BaseModel):
    size: str
    quantity: int
    in_stock: bool


class ProductDetails(BaseModel):
    product_id: str
    name: str
    description: str
    price: float
    stock_by_size: list[StockBySize] = Field(default_factory=list)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    access_token: str | None = None
    page_context: str | None = Field(default=None, max_length=500)


class ChatReply(BaseModel):
    reply: str
    products: list[ProductCard] = Field(default_factory=list)
    lookup: ProductDetails | None = None


class ChatMessage(BaseModel):
    role: str
    content: str
    products: list[ProductCard] = Field(default_factory=list)


class ChatDeps(BaseModel):
    user_id: int | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    page_context: str | None = None


class RegisterRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
