#Basic Agent
import os
from google.adk.agents import Agent
from dotenv import load_dotenv
import yfinance as yf

# Load environment variables from .env file
load_dotenv()

# Retrieve the Google API key from the environment
google_api_key = os.getenv("GOOGLE_API_KEY")


# Initialize the basic agent 
root_agent = Agent(
    model='gemini-2.0-flash-001',
    name='basic_agent',
    description='A helpful assistant for user questions.',
    instruction="""you are a helpful stock market assistant. Be concise. If you dont know something, say so.""",
)
# run on the terminal as administration mode:  adk run app





# Initialize the basic agent with tool
from google.adk.agents import Agent
import yfinance as yf

def get_stock_price(ticker: str):
    stock = yf.Ticker(ticker)
    price = stock.info.get("currentPrice", "Price not available")
    return {"price": price, "ticker": ticker}

root_agent = Agent(
    model='gemini-2.0-flash-001',
    name='basic_agent_with_tool',
    description='A helpful stock market assistant with tools.',
    instruction="""you are a helpful stock market assistant. Always use the get_stock_price tool.Include the ticker symbol in your         response.""",
    tools=[get_stock_price]
)
# run on the terminal as administration mode:  adk web






# Agent with State
from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
import yfinance as yf


def get_stock_price(ticker: str, tool_context: ToolContext):
    stock = yf.Ticker(ticker)
    price = stock.info.get("currentPrice", "Price not available")
    
    # Initialize recent_searches if it doesn't exist
    if "recent_searches" not in tool_context.state:
        tool_context.state["recent_searches"] = []
        
    recent_searches = tool_context.state["recent_searches"]
    if ticker not in recent_searches:
        recent_searches.append(ticker)
        tool_context.state["recent_searches"] = recent_searches
    
    return {"price": price, "ticker": ticker}


root_agent = Agent(
    name="stateful_agent",
    model="gemini-2.0-flash",
    description="An agent that remembers recent searches",
    instruction="""
    You are a stock price assistant. Use the get_stock_price tool. I'll remember your previous searches and can tell you about them if you ask.
    """,
    tools=[get_stock_price],
)






# Multi-Tool Agent
from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
import yfinance as yf


def get_stock_price(ticker: str, tool_context: ToolContext):
    stock = yf.Ticker(ticker)
    price = stock.info.get("currentPrice", "Price not available")
    
    # Initialize recent_searches if it doesn't exist
    if "recent_searches" not in tool_context.state:
        tool_context.state["recent_searches"] = []
        
    recent_searches = tool_context.state["recent_searches"]
    if ticker not in recent_searches:
        recent_searches.append(ticker)
        tool_context.state["recent_searches"] = recent_searches
    
    return {"price": price, "ticker": ticker}


def get_stock_info(ticker: str):
    stock = yf.Ticker(ticker)
    company_name = stock.info.get("shortName", "Name not available")
    sector = stock.info.get("sector", "Sector not available")
    return {
        "ticker": ticker,
        "company_name": company_name,
        "sector": sector
    }
root_agent = Agent(
    name="multi_tool_agent",
    model="gemini-2.0-flash",
    description="An agent with multiple stock information tools",
    instruction="""
    You are a stock information assistant. You have two tools:
    - get_stock_price: For prices
    - get_stock_info: For company name and sector
    """,
    tools=[get_stock_price, get_stock_info],
)





# Structured Output Agent
from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field
import yfinance as yf

class StockAnalysis(BaseModel):
    ticker: str = Field(description="Stock symbol")
    recommendation: str = Field(description="Buy or Sell recommendation")


def get_stock_data_for_prompt(ticker):
    stock = yf.Ticker(ticker)
    price = stock.info.get("currentPrice", 0)
    target_price = stock.info.get("targetMeanPrice", 0)
    return price, target_price


root_agent = LlmAgent(
    name="structured_agent",
    model="gemini-2.0-flash",
    description="An agent with structured output",
    instruction="""
    You are a stock advisor. Analyze the stock ticker provided by the user.
    Return Buy or Sell recommendation in JSON format.
    
    For each ticker, look at the price and target price to make a decision.
    If target price > current price: recommend Buy
    Otherwise: recommend Sell
    """,
    output_schema=StockAnalysis,
    output_key="stock_analysis"
)







# Callback Agent
from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.base_tool import BaseTool
import yfinance as yf
from typing import Dict, Any, Optional

def get_stock_data(ticker: str, tool_context: ToolContext):
    stock = yf.Ticker(ticker)
    price = stock.info.get("currentPrice", 0)
    
    # Initialize tool_usage in state if it doesn't exist
    if "tool_usage" not in tool_context.state:
        tool_context.state["tool_usage"] = {}
    
    return {
        "ticker": ticker,
        "price": price
    }


def before_tool_callback(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext) -> Optional[Dict]:
    # Initialize tool_usage if it doesn't exist
    if "tool_usage" not in tool_context.state:
        tool_context.state["tool_usage"] = {}
        
    # Track tool usage count
    tool_usage = tool_context.state["tool_usage"]
    tool_name = tool.name
    tool_usage[tool_name] = tool_usage.get(tool_name, 0) + 1
    tool_context.state["tool_usage"] = tool_usage
    
    print(f"[LOG] Running tool: {tool_name}")
    return None


def after_tool_callback(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Dict) -> Optional[Dict]:
    print(f"[LOG] Tool {tool.name} completed")
    return None

# Initialize state before creating the agent
initial_state = {"tool_usage": {}}

root_agent = Agent(
    name="callback_agent",
    model="gemini-2.0-flash",
    description="An agent with callbacks",
    instruction="""
    You are a stock assistant. Use get_stock_data tool to check stock prices.
    This agent keeps track of how many times tools have been used.
    """,
    tools=[get_stock_data],
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
)

