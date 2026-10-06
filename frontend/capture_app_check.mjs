import { chromium } from "playwright";
import fs from "node:fs";

const output = "../output/app_check_images";
fs.mkdirSync(output, { recursive: true });
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });

await page.goto("http://127.0.0.1:5176/", { waitUntil: "networkidle" });
await page.getByRole("button", { name: "Chat" }).click();
await page.getByPlaceholder("Ask about the collection...").fill("What is the price and stock by size for the Basic Hoodie Big Yale?");
await page.getByRole("button", { name: "Send" }).click();
await page.waitForTimeout(12000);
await page.screenshot({ path: `${output}/inventory.png`, fullPage: true });

await page.goto("http://127.0.0.1:5176/", { waitUntil: "networkidle" });
await page.getByRole("button", { name: "Chat" }).click();
await page.getByPlaceholder("Ask about the collection...").fill("What hoodies do you have?");
await page.getByRole("button", { name: "Send" }).click();
await page.waitForTimeout(12000);
await page.screenshot({ path: `${output}/dynamic_cards.png`, fullPage: true });

await page.goto("http://127.0.0.1:5176/products", { waitUntil: "networkidle" });
await page.screenshot({ path: `${output}/usability_filters.png`, fullPage: true });
await browser.close();
