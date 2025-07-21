from browser_use import Agent, BrowserSession
from browser_use.llm import ChatGoogle
import asyncio, os
from dotenv import load_dotenv

load_dotenv()

async def main():
    session = BrowserSession(headless=False)    
    page = await session.new_tab()    
    agent = Agent(
        task=f"""Please view my twitter feed at 'https://x.com/home', find posts on 'Artificial General Intelligence', review the post content, and reply with a thoughtful comment. Make at least 5 replies. Please note that the reply should be under 200 characters."""
        ,
        llm=ChatGoogle(model="gemini-2.5-flash"),
        page=page,                         
        generate_gif="logs/gif",
        save_conversation_path="logs/conversation",
    )
    result = await agent.run()
    print(result)
asyncio.run(main())