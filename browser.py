import asyncio
import argparse
from dotenv import load_dotenv
from browser_use import Agent
from browser_use.llm import ChatGoogle
import os
from browser_use import BrowserSession, Agent

load_dotenv()

session = BrowserSession(headless=False)

async def main():    
    ask = "Go to Google.com"
    #ask = f"Research as necessary, write an article 'superintelligence plans of Meta' in the online editor https://dillinger.io/. The editor field is of a div with id 'editor1'. The article should have 4 paragraphs with images included"    
    agent = Agent(
        task=ask,
        llm=ChatGoogle(model="gemini-2.5-pro"), 
        browser_session=session,               
        save_conversation_path="logs/conversation",        
        generate_gif="logs/gif",
        record_gif=True,
        gif_dir="logs/gif",
        keep_browser_open=True  
    )

    result = await agent.run()
    print(result)    

asyncio.run(main())