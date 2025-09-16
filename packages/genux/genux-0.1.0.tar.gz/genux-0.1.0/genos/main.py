# genos/main.py

import os
from .orchestrator import MultiAgentOrchestrator
from .utils import get_multiline_input
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults


def main():
    """Main CLI entrypoint for genos"""
    if not os.environ.get("GROQ_API_KEY"):
        print("❌ Error: GROQ_API_KEY environment variable not set")
        return

    if not os.environ.get("TAVILY_API_KEY"):
        print("❌ Error: TAVILY_API_KEY environment variable not set")
        return

    # Initialize LLM + tools
    llm = ChatGroq(
        api_key=os.environ.get("GROQ_API_KEY"),
        model="deepseek-r1-distill-llama-70b",
        temperature=0.3,
    )

    tavily_search = TavilySearchResults(
        api_key=os.environ.get("TAVILY_API_KEY"),
        max_results=10,
    )

    orchestrator = MultiAgentOrchestrator(llm, tavily_search)

    print("🎯 Welcome to the Multi-Agent Linux Command System!")
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
