# HW 4 AI Prompts

This file records the prompts used while completing Homework 4. It will be updated as each problem is worked on.

## Problem 2 — Understand the Campus Customs database

**Prompt typed:** “I need you to look at the database in data 4/campus_customs.db and understand the fields of each table. At a minimum understand catalogue, inventory, and users. Create output/harness.md with each table, its fields, and one short line on why each field matters for the shop or chatbot.”

**What was lacking after the first prompt:** The database schema was not described in the request, so it had to be inspected directly, including the additional `chat_messages` table.

**Follow-up prompt (if needed):** None yet.

**Follow-up prompt:** “The virtual try-on is not working as expected; remove it and change the entire site to baby blue, Yale blue, and silver with faded Ys in the background.”

**What was lacking after the follow-up:** The original try-on preview did not provide useful enough visual realism, so it was removed and replaced with a simpler, consistent visual theme.

**Review prompt:** “Any issues or problems?”

**Answer summary:** No implementation problems remain. One verification assertion initially treated `available_sizes` as objects instead of strings; the check was corrected, and the bounded search, current-product lookup, backend compile, and frontend build all passed.

**Review prompt:** “Great any issues that need to be fixed?”

**Answer summary:** No blocking issues remain. One known limitation is that access sessions are kept in memory, so a backend restart invalidates the browser token; the user can log in again and their database history remains intact. The page context currently sends the product route pathname, which is enough to identify the route but could later be enriched with the product name/details for stronger “this” references.

**Review prompt:** “Were there any issues you ran into?”

**Answer summary:** One small search issue appeared: the database uses singular “hoodie,” while the example query used “hoodies.” I added simple plural normalization, and the query now returns 8 hoodie matches. The frontend build and backend checks pass.

**Review prompt:** “Were there any issues with the problem?”

**Answer summary:** No blocking application issues. One internal verification check initially inspected a private PydanticAI attribute that changed between versions, but the real database lookup and Python compile checks passed after using the public behavior. The tools returned accurate prices and size quantities, including out-of-stock sizes.

**Review prompt:** “Were there any issues?”

**Answer summary:** No blocking issues remained. A couple of setup checks needed correction: one frontend patch had to be reapplied, and one build command was first run from the wrong directory. Both were resolved. The current scaffold keeps sessions in memory and the frontend token in local storage, so production deployment should later move to secure HTTP-only cookies and persistent session storage.

**Review prompt:** “Were there any issues or errors you ran into?”

**Answer summary:** Two setup issues occurred: the first TypeScript build needed React type declarations and Vite CSS types, and the FastAPI test client needed `httpx2`. Both were installed/configured, and the frontend build plus API smoke tests then passed.

## Problem 3 — Campus Customs Frontend and Backend Scaffold

**Prompt typed:** “Scaffold a React + Vite + Typescript Campus Customs frontend with navigation, original Home/About wording inspired by Yale style, catalogue product cards and detail pages, a floating chat stub, and a FastAPI backend serving products and images from the database.”

**What was lacking after the first prompt:** The frontend and backend requirements had not yet been provided.

**Follow-up prompt (if needed):** None yet.

## Problem 4 — Create account and login flow

**Prompt typed:** “Build a normal create-account/login flow with first name, last name, email, password, and confirmation password for accounts; email and password for login. Store accounts in users, securely protect passwords, test the seeded user and a new account, and document authentication in harness.md.”

**What was lacking after the first prompt:** No additional requirements were missing; the existing users table and seed credentials were inspected before implementation.

**Follow-up prompt (if needed):** None yet.

## Problem 5 — Shop Chatbot Agent

**Prompt typed:** “Build the shop chatbot as a PydanticAI agent behind FastAPI, keep the agent in backend/prompts/prompt.md, backend/agent.py, backend/tools.py, and backend/models.py, expose a chat route, connect the frontend chat widget, add Campus Customs voice and safety basics, document the integration, and run it with uvicorn main:app --reload --port 8000 from backend.”

**What was lacking after the first prompt:** The chatbot route, agent file layout, and frontend/backend connection requirements had not yet been provided.

**Follow-up prompt (if needed):** None yet.

## Problem 6 — Database-backed product and inventory lookups

**Prompt typed:** “Give the agent tools to look up real product description, price, and stock by size from campus_customs.db. Do not invent prices or quantities, clearly report out-of-stock sizes, update the prompt and models, and document the tools and lookup fields in harness.md.”

**What was lacking after the first prompt:** The lookup tool names and typed response fields had not yet been defined.

**Follow-up prompt (if needed):** None yet.

## Problem 7 — Dynamic chat product cards

**Prompt typed:** “When a customer asks about a type of item, have the agent search the catalogue and return structured product matches so the website dynamically renders matching product cards. Make those cards open the existing single-item detail page, and update the prompt and harness documentation.”

**What was lacking after the first prompt:** The API-to-frontend product-card contract and interaction with the existing detail route had not yet been implemented.

**Follow-up prompt (if needed):** None yet.

## Problem 8 — Persistent signed-in chat history and page context

**Prompt typed:** “When a shopper is logged in, save chat history in the database and reload it when they return. Give the agent the shopper's name/email and current page context, while keeping guest chat non-persistent. Document storage, customer context, and page context in harness.md.”

**What was lacking after the first prompt:** The authentication token, chat history table, agent dependency shape, and page-context contract needed to be connected.

**Follow-up prompt (if needed):** None yet.

## Problem 9 — Usability Improvements

**Prompt typed:** “Choose and implement 2 front-end usability improvements and 2 agent/backend usability improvements. Write output/usability.md explaining what each adds and why it helps, and make sure all features appear in the running app.”

**What was lacking after the first prompt:** The four improvement choices had not yet been selected.

**Follow-up prompt (if needed):** None yet.

## Problem 10 — Boutique Site Design

**Prompt typed:** “Make the site feel like an upscale boutique with a graphic curly font and blue/silver palette, replace generic shapes with a moving product/Yale scenery collage, add a virtual try-on feature, make chat friendly, and document the changes in output/design.md.”

**What was lacking after the first prompt:** The original try-on preview was later judged insufficiently realistic and was removed; the final design instead emphasizes trust, rounded controls, and the blue/silver visual system.

**Follow-up prompt:** “The virtual try-on is not working as expected; remove it, change the entire site to baby blue, Yale blue, and silver with faded Ys, and round the sharp corners.”

## Problem 11 — Test the live site

**Prompt typed:** “Test the live site and document it in output/app_check.html with clear screenshots and captions for database-backed inventory/price chat, dynamic category search cards, and one Problem 9 usability feature. Put screenshots in output/app_check_images/ and link them with relative paths.”

**What was lacking after the first prompt:** The requested checks needed real browser interactions and screenshots, not only source-code verification.

**Follow-up prompt (if needed):** “Try again.”

## Problem 12 — Audit Trail and Agent Safety

**Prompt typed:** “Keep an append-only output/audit_trail.json of agent-loop activity with time, tool name, short arguments/result, and stop reason. Add safety rules to prompts/prompt.md and finish harness.md with models, tools, safety, limits, models, and run commands.”

**What was lacking after the first prompt:** The audit format, safety requirements, and complete manager-facing system summary needed to be implemented and documented.

**Follow-up prompt (if needed):** None yet.
