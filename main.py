from config import KICK_SESSION_TOKEN
import os
import sys
import time
import asyncio
import threading
import re
from http.server import SimpleHTTPRequestHandler, HTTPServer
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

# Nastavenie ciest
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(os.getcwd(), ".playwright")

CHANNEL_NAME = 'MGFitman'

# --- FAKE WEBSERVER ---
def run_fake_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_fake_server, daemon=True).start()

async def posli_spravu():
    print("Spúšťam prehliadač so Stealth maskovaním...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        
        await Stealth().apply_stealth_async(context)
        
        await context.add_cookies([{
            'name': 'session_token',
            'value': KICK_SESSION_TOKEN,
            'domain': '.kick.com',
            'path': '/',
            'secure': True,
            'httpOnly': True
        }])
        
        page = await context.new_page()
        
        print(f"Otváram chat streamera {CHANNEL_NAME}...")
        await page.goto(f"https://kick.com/{CHANNEL_NAME}")
        
        # Shortcut na cookies
        try:
            await page.get_by_role("button", name=re.compile(r"Accept|Agree", re.I)).click(timeout=5000)
            print("Cookies odkliknuté.")
        except:
            print("Cookies lišta nebola nájdená.")
            
        print("Čakám na načítanie chatu...")
        await asyncio.sleep(12)
        
        try:
            chat_input = page.locator('div[contenteditable="true"], [placeholder*="message"], #message-input')
            await chat_input.first.wait_for(state="visible", timeout=15000)
            
            print("Políčko nájdené, píšem...")
            await chat_input.first.click()
            await chat_input.first.type("xd", delay=150)
            await chat_input.first.press("Enter")
            print("BINGO! Správa odoslaná.")
        except Exception as e:
            print(f"Chyba: {e}")
            await page.screenshot(path="screenshot.png")
            
        await browser.close()

async def main():
    while True:
        await posli_spravu()
        await asyncio.sleep(600)

if __name__ == "__main__":
    asyncio.run(main())
