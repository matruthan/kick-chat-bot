import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
import config

async def posli_spravu():
    async with async_playwright() as p:
        # V GitHub Actions musíš použiť --no-sandbox
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        context = await browser.new_context()

        await context.add_cookies([{
            'name': 'kick_session', # Toto je kľúčové, skontroluj v prehliadači
            'value': config.KICK_SESSION_TOKEN,
            'domain': '.kick.com',
            'path': '/'
        }])

        page = await context.new_page()
        await stealth_async(page)
        
        print("Pripájam sa na Kick...")
        await page.goto(f"https://kick.com/{config.CHANNEL_NAME}/chatroom")
        
        # Počkáme na načítanie chatu (CSS selektor pre textové pole)
        try:
            await page.wait_for_selector('textarea[placeholder="Send a message..."]', timeout=10000)
            
            # Napísanie správy
            await page.fill('textarea[placeholder="Send a message..."]', "Ahoj, toto je správa od bota!")
            await page.keyboard.press("Enter")
            print("Správa odoslaná!")
        except Exception as e:
            print(f"Chyba: {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(posli_spravu())
