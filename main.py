import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
import config

async def posli_spravu():
    async with async_playwright() as p:
        # Spustenie prehliadača (bez nastavenia cesty, aby použil systémovú)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        # Pridanie session tokenu
        await context.add_cookies([{
            'name': 'remember_me', # Niekedy sa volá 'kick_session', over si v prehliadači
            'value': config.KICK_SESSION_TOKEN,
            'domain': 'kick.com',
            'path': '/'
        }])

        page = await context.new_page()
        await stealth_async(page)
        
        print("Pripájam sa na Kick...")
        await page.goto(f"https://kick.com/{config.CHANNEL_NAME}")
        
        # Čakanie na načítanie chatu
        await page.wait_for_timeout(5000)
        
        # Tu by bola logika na nájdenie inputu a poslanie správy
        print("Bot je pripojený a pripravený.")
        
        await browser.close()

async def main():
    await posli_spravu()

if __name__ == "__main__":
    asyncio.run(main())
