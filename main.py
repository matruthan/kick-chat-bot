import os
import sys
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(os.getcwd(), ".playwright")

# ... SEM POKRAČUJE TVOJ DOTERAJŠÍ KÓD (import time, asyncio, atď.) ...
import time
import asyncio
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
from playwright.async_api import async_playwright

# === NASTAVENIA ===
KICK_SESSION_TOKEN = '385722478%7CtbHj70Up0mu1V6Hvx28cOKgeyuNzGCwkBdtPDjoU'  # Tvoj dlhý token s percentami
CHANNEL_NAME = 'MGFitman'

# --- FAKE WEBSERVER PRE RENDER WEB SERVICE ---
def run_fake_server():
    import os
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    print(f"Fake server beží na porte {port} pre spokojnosť Renderu...")
    server.serve_forever()

# Naštartujeme fake server v samostatnom vlákne, aby neblokoval bota
threading.Thread(target=run_fake_server, daemon=True).start()
# ---------------------------------------------

async def posli_spravu():
    print("Spúšťam prehliadač cez Playwright...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        
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
        
        await asyncio.sleep(5)
        
        try:
            print("Hľadám políčko na písanie správy...")
            chat_input = page.locator('text="Send a message"')
            if await chat_input.count() == 0:
                chat_input = page.locator('#message-input, [placeholder*="message"]')
                
            await chat_input.click()
            await chat_input.fill("xd")
            await asyncio.sleep(1)
            
            await chat_input.press("Enter")
            print("BINGO! Správa 'xd' bola úspešne odoslaná do chatu.")
            await asyncio.sleep(2)
            
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
