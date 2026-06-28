from config import KICK_SESSION_TOKEN
CHANNEL_NAME = 'MGFitman'
import re # Pridaj tento import
# ... (zvyšok kódu)
# =====================================================================
# VŠETKO POD TÝMTO RIADKOM STAČÍ SKOPÍROVAŤ A UŽ TO NIKDY NEMUSÍŠ MENIŤ
# =====================================================================import os
import os
import sys

os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(os.getcwd(), ".playwright")

import time
import asyncio
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
from playwright.async_api import async_playwright
from playwright_stealth import Stealth  # NOVÝ SPÔSOB IMPORTOVANIA

# --- FAKE WEBSERVER PRE RENDER WEB SERVICE ---
def run_fake_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    print(f"Fake server beží na porte {port} pre spokojnosť Renderu...")
    server.serve_forever()

threading.Thread(target=run_fake_server, daemon=True).start()
# ---------------------------------------------

async def posli_spravu():
    print("Spúšťam prehliadač cez Playwright so Stealth maskovaním...")
    async with async_playwright() as p:
        # Pridáme špeciálny argument, ktorý vypne detekciu automatizácie
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        # Nastavíme User-Agent, aby sme sa tvárili ako reálny človek na Windowse
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        
        # Aplikujeme Stealth maskovanie na celý prehliadač (nová metóda)
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
        
        print("Čakám 12 sekúnd na prekonanie Cloudflare, overenie followu a načítanie chatu...")
        await asyncio.sleep(12)
        
        try:
            print("Hľadám políčko na písanie správy...")
            
            chat_input = page.locator('div[contenteditable="true"], [placeholder*="message"], #message-input')
            
            await chat_input.first.wait_for(state="visible", timeout=15000)
            
            print("Políčko nájdené, klikám...")
            await chat_input.first.click()
            await asyncio.sleep(1)
            
            print("Píšem text správy...")
            await chat_input.first.type("xd", delay=150)
            await asyncio.sleep(1)
            
            print("Odosielam (Enter)...")
            await chat_input.first.press("Enter")
            print("BINGO! Správa 'xd' bola úspešne odoslaná do chatu.")
            await asyncio.sleep(3)
            
        except Exception as e:
            print(f"Chyba pri hľadaní chatu alebo posielaní: {e}")
            await page.screenshot(path="screenshot.png")
            print("Snímka obrazovky uložená ako screenshot.png")
            
        await browser.close()

async def main():
    print("Bot úspešne naštartovaný na Renderi a beží nonstop...")
    while True:
        try:
            await posli_spravu()
        except Exception as e:
            print(f"Neočakávaná chyba v hlavnej slučke: {e}")
        
        print("Čakám 10 minút pred ďalšou správou...")
        await asyncio.sleep(600)

if __name__ == "__main__":
    asyncio.run(main())
