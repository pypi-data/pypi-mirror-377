# genos/main.py

import os
from .orchestrator import MultiAgentOrchestrator
from .utils import get_multiline_input
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
import pyfiglet


def main():
    """Main CLI entrypoint for genos"""
    # Set API keys in environment if not present
    if not os.environ.get("GROQ_API_KEY"):
        groq_api_key = input("Enter your GROQ API Key: ").strip()
        if not groq_api_key:
            print("❌ GROQ API Key is required. Exiting.")
            return
        os.environ["GROQ_API_KEY"] = groq_api_key  

    if not os.environ.get("TAVILY_API_KEY"):
        tavily_api_key = input("Enter your Tavily API Key: ").strip()
        if not tavily_api_key:
            print("❌ Tavily API Key is required. Exiting.")
            return
        os.environ["TAVILY_API_KEY"] = tavily_api_key  


    # Initialize LLM + tools
    llm = ChatGroq(
        api_key=os.environ.get("GROQ_API_KEY"),
        model="deepseek-r1-distill-llama-70b",
        temperature=0.3,
    )

    tavily_search = TavilySearch(
        api_key=os.environ["TAVILY_API_KEY"],
        max_results=10,
    )


    orchestrator = MultiAgentOrchestrator(llm, tavily_search)

    banner = pyfiglet.figlet_format("Genux", font="slant")
    print(banner)
    print("Choose an input method:")
    print("1) Single line text input")
    print("2) Multi-line text input")

    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        user_input = input("Enter your request: ").strip()
    elif choice == "2":
        user_input = get_multiline_input()
    else:
        print("❌ Invalid choice. Exiting.")
        return

    if user_input:
        orchestrator.process_request(user_input)
    else:
        print("❌ No input provided. Exiting.")
