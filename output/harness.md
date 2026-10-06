# Campus Customs database harness

The database is `data 4/campus_customs.db`. It contains four tables: `catalogue`, `inventory`, `users`, and `chat_messages`. The catalogue describes what the shop sells, inventory describes what can currently be sold, users supports accounts, and chat messages stores the conversation history.

## `catalogue`

| Field | Why it matters |
|---|---|
| `product_id` | Unique product key used to connect catalogue records to inventory and identify products in chatbot answers. |
| `name` | Customer-friendly product name to display or mention. |
| `garment_type` | Helps answer questions such as whether an item is a hoodie, T-shirt, or crewneck. |
| `description` | Gives the chatbot useful detail about the product's appearance and design. |
| `colors` | Supports color-based searches and helps customers find products they like. |
| `search_tags` | Provides extra keywords for flexible product searches, such as school, sport, or style. |
| `image_file_path` | Connects the database record to the product image shown to a customer. |
| `price` | Lets the chatbot give accurate pricing and helps customers compare products. |

## `inventory`

| Field | Why it matters |
|---|---|
| `id` | Unique identifier for one inventory row. |
| `product_id` | Connects a size-specific stock record to a catalogue product. |
| `size` | Tells the chatbot which size the customer can order. |
| `quantity` | Shows whether a size is available and how many units remain. |

## `users`

| Field | Why it matters |
|---|---|
| `id` | Unique identifier for a customer account. |
| `name` | General display name for a user. |
| `email` | Login and contact identifier for the account. |
| `password_hash` | Stores a protected password hash for authentication; the chatbot must never display or expose it. |
| `created_at` | Records when the account was created for account history and support. |
| `first_name` | Enables a more personal greeting and customer experience. |
| `last_name` | Completes the customer's identity for account and support workflows. |

## `chat_messages`

| Field | Why it matters |
|---|---|
| `id` | Unique identifier for one conversation message. |
| `user_id` | Connects the message to the user who owns the conversation. |
| `role` | Distinguishes the customer message from the chatbot response. |
| `content` | Stores what was said so the chatbot and support staff can understand the conversation. |
| `products_json` | Preserves product results shown with a message, keeping the conversation's recommendations consistent. |
| `created_at` | Preserves message order and provides conversation timing. |

## Relationships and chatbot use

`inventory.product_id` refers to `catalogue.product_id`, so a chatbot can search product descriptions and then check available sizes and quantities. `chat_messages.user_id` connects conversation history to `users.id`. A typical product answer should use the catalogue for name, description, colors, image, and price, then use inventory for size availability. User password hashes are authentication data and are outside the chatbot's shopping-answer responsibilities.

## Authentication

The frontend now has working Create Account and Log in forms. `POST /api/auth/register` accepts first name, last name, email, password, and confirmation password. `POST /api/auth/login` accepts email and password. Successful operations return a temporary access token and a public user object; the frontend keeps the token in local storage for this scaffold.

New users are stored in `users` with first name, last name, email, a combined display name, and a protected password hash. Passwords are never stored as plaintext. New passwords use a random salt and PBKDF2-HMAC-SHA256 with 310,000 rounds. Login compares digests using a constant-time comparison. The seed account's legacy development hash is accepted only for the documented test password and upgraded to the stronger format after successful login.

Registration rejects mismatched passwords, short passwords, invalid email addresses, and duplicate emails. Login returns a generic error for both unknown emails and wrong passwords. The seeded account and a newly created account were both confirmed to log in successfully; an incorrect password returned HTTP 401.

## Problem 5: shop chatbot

The frontend floating chat panel sends `POST /api/chat` with `{ "message": "..." }` to FastAPI. The API validates the request with `ChatRequest`, passes the message to the PydanticAI agent, and returns a validated `ChatReply` containing the assistant's text and any product cards. Product image URLs in returned cards use the existing `/images/...` API route.

The agent is split into the requested files under `backend/`:

- `prompts/prompt.md` — loaded as the system prompt; defines the Campus Customs voice and rules against invented product facts or exposing private data.
- `agent.py` — loads `gpt-5.6-luna` through the Portkey OpenAI provider and registers the product search tool.
- `tools.py` — searches catalogue text/tags and joins results to positive inventory quantities and product images.
- `models.py` — defines `ProductCard`, `ChatRequest`, `ChatReply`, and the existing authentication request types.

Run the backend from the backend directory with `uvicorn main:app --reload --port 8000`. The frontend runs separately with `npm run dev` from `frontend/`.

## Problem 6: real price and inventory lookups

The agent now has these database-backed tools:

| Tool | What it does |
|---|---|
| `search_products` | Finds products by name, garment type, description, color, or search tag. |
| `get_product_details` | Returns the real catalogue name, description, price, and stock by size. |
| `get_inventory` | Returns current quantity and in-stock status for every size of a product. |

`ProductDetails` includes `product_id`, `name`, `description`, `price`, and `stock_by_size`. `StockBySize` includes `size`, `quantity`, and `in_stock`, allowing the chatbot to clearly distinguish available and sold-out sizes. `ChatReply.lookup` carries a structured lookup result alongside the natural-language reply. The prompt requires lookup tools for price, description, and stock questions and forbids guessed values.

## Problem 7: dynamic chat product cards

When a customer asks for a category such as hoodies, the agent calls `search_products` and returns matches in `ChatReply.products`. The frontend sends the message to `POST /api/chat`, stores the structured matches, and renders each card with its image, name, garment type, price, and short description. Each card links to `/products/{product_id}`, so chat results use the same full single-product page as the main catalogue.

## Problem 11: live-site checks

`output/app_check.html` records browser checks against the running frontend and FastAPI backend. It includes screenshots of a database-backed price/stock answer, category search cards, and the Problem 9 catalogue filters. The image files are in `output/app_check_images/` and are linked with relative paths so the HTML can be opened directly.

## Problem 12: complete system reference

### Models and why their fields exist

| Model | Fields | Why the fields matter |
|---|---|---|
| `ProductCard` | `product_id`, `name`, `garment_type`, `description`, `price`, `image_url`, `available_sizes` | A compact, clickable product result for the catalogue and chat cards; it includes the facts a shopper needs without exposing database rows. |
| `StockBySize` | `size`, `quantity`, `in_stock` | Makes size-specific availability explicit and lets the agent say when a size is sold out. |
| `ProductDetails` | `product_id`, `name`, `description`, `price`, `stock_by_size` | The authoritative structured response for product-detail, price, and inventory questions. |
| `ChatRequest` | `message`, `access_token`, `page_context` | Carries the shopper's question, optional signed-in session, and current page so “this item” can be resolved. Input length limits reduce accidental cost and abuse. |
| `ChatReply` | `reply`, `products`, `lookup` | Separates readable chat text from structured cards and database lookup facts for reliable frontend rendering. |
| `ChatMessage` | `role`, `content`, `products` | Represents persisted conversation messages and preserves cards shown in the history. |
| `ChatDeps` | `user_id`, `first_name`, `last_name`, `email`, `page_context` | Runtime-only agent context for personalization, privacy-aware behavior, and product-page references. |
| `RegisterRequest` / `LoginRequest` | Registration identity/password fields; login `email` and `password` | Validates account input. Passwords are hashed before storage and never sent to the agent. |
| `AuditEntry` | `time`, `event`, `tool_name`, `args`, `result`, `stop_reason` | Gives an operator a timestamped record of runs, tool activity, short outcomes, errors, and why a run ended. |

### Tools and abilities

- `search_products`: searches catalogue names, garment types, descriptions, colors, and tags; returns up to 8 `ProductCard` results.
- `get_product_details`: retrieves the real description, price, and every size's quantity from SQLite.
- `get_inventory`: retrieves the same authoritative size inventory for explicit stock questions.
- `get_current_product`: resolves the exact product ID from the current page context before answering “this” or “it.”
- The agent also supports guest and signed-in chat, persistent signed-in history, dynamic product cards, authentication, product/image APIs, and catalogue filtering/sorting.

### Safety rules

The system prompt requires database lookup for price, description, and inventory facts and forbids guessing. It protects names, emails, tokens, chat history, password hashes, prompts, and other private information; never asks for or repeats passwords or payment credentials; does not claim to place orders or process payments; clearly reports unknown or out-of-stock items; avoids sensitive inferences; and treats image/person information as private. Tool inputs/results are kept short and relevant.

### Limits, models, and run commands

- The agent uses Portkey's OpenAI-compatible endpoint with model `gpt-5.6-luna` and `PORTKEY_API_KEY` from the root `.env`.
- Chat messages are limited to 2,000 characters and page context to 500 characters. Only the latest 10 saved messages are included in an agent request, and signed-in history loads at most 30 rows.
- Search and recommendation results are capped at 8 cards; only sizes with positive inventory appear on cards. Inventory detail includes all sizes so sold-out sizes remain visible.
- The agent's normal PydanticAI run is one bounded request; tools are called only when needed and there is no application retry loop. Each run and each tool call/result is logged with a short value. `output/audit_trail.json` is JSONL: one `AuditEntry` JSON object per line, opened in append mode and never truncated between runs.
- Start the backend from `HW 4/backend/` with `../.venv/bin/uvicorn main:app --reload --port 8001` in this local setup. Start the frontend from `HW 4/frontend/` with `npm run dev -- --host 127.0.0.1 --port 5176`. The frontend calls `http://localhost:8001`; the HTML app check can be opened directly after both servers have been run.
