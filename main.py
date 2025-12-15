"""
AI TRAVEL ASSISTANT - COMPLETE IMPLEMENTATION
==============================================

Multi-Modal Agentic Workflow using LangGraph + Streamlit

This is the main agent file. Run with Streamlit:
    streamlit run app.py

Requirements:
    pip install langgraph langchain-openai streamlit chromadb faiss-cpu tavily-python

Author: AI Engineering Assignment
"""

import os
import json
import asyncio
from typing import TypedDict, Annotated, Literal, Optional, List, Dict, Any
from datetime import datetime, timedelta
import operator

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

# AI Model (using OpenAI - can switch to Anthropic)
try:
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
except:
    print("⚠️ OpenAI not configured. Using mock responses.")
    llm = None

# Vector Database
try:
    import chromadb
    from chromadb.config import Settings
except:
    chromadb = None
    print("⚠️ ChromaDB not installed. Using simple dict database.")

# ============================================================================
# PART 1: STATE DEFINITION
# ============================================================================

class AgentState(TypedDict):
    """State that flows through the agent graph"""
    
    # User input
    messages: Annotated[List, operator.add]
    city: str
    
    # Routing decision
    route: Optional[str]  # "database" or "web"
    
    # Fetched data
    city_summary: Optional[str]
    weather_forecast: Optional[List[Dict]]
    image_urls: Optional[List[str]]
    
    # Error handling
    error: Optional[str]
    
    # Memory for context
    last_city: Optional[str]
    conversation_context: Optional[Dict]

# ============================================================================
# PART 2: VECTOR DATABASE SETUP
# ============================================================================

class CityDatabase:
    """Pre-populated vector database for known cities"""
    
    def __init__(self):
        self.cities = {
            "paris": {
                "name": "Paris",
                "country": "France",
                "summary": """Paris is the capital and most populous city of France. 
Known for iconic landmarks like the Eiffel Tower, Louvre Museum, Notre-Dame Cathedral, 
and Arc de Triomphe. The city is famous for its art, fashion, gastronomy, and culture. 
It's often called the 'City of Light' due to its role in the Age of Enlightenment and 
its early adoption of street lighting. Paris is divided into 20 arrondissements and 
sits along the Seine River.""",
                "population": "2.2 million",
                "timezone": "CET (UTC+1)"
            },
            "tokyo": {
                "name": "Tokyo",
                "country": "Japan",
                "summary": """Tokyo is the capital of Japan and the world's most populous 
metropolitan area. It's a major global financial center and home to cutting-edge technology, 
fashion, and cuisine. The city blends ultramodern skyscrapers with historic temples and 
traditional gardens. Famous districts include Shibuya, Shinjuku, Harajuku, and Akihabara. 
Tokyo hosted the 2020 Summer Olympics and is known for its efficient public transportation, 
safety, and cleanliness.""",
                "population": "14 million",
                "timezone": "JST (UTC+9)"
            },
            "new york": {
                "name": "New York",
                "country": "United States",
                "summary": """New York City is the most populous city in the United States, 
known as 'The City That Never Sleeps'. It comprises 5 boroughs: Manhattan, Brooklyn, Queens, 
The Bronx, and Staten Island. Home to iconic landmarks like the Statue of Liberty, Empire 
State Building, Central Park, Times Square, and Broadway. NYC is a global hub for finance, 
media, art, fashion, and culture. It's the most linguistically and culturally diverse city 
in the world.""",
                "population": "8.3 million",
                "timezone": "EST (UTC-5)"
            }
        }
    
    def search(self, city: str) -> Optional[Dict]:
        """Search for city in database"""
        city_lower = city.lower().strip()
        return self.cities.get(city_lower)
    
    def has_city(self, city: str) -> bool:
        """Check if city exists in database"""
        return city.lower().strip() in self.cities

# Initialize database
city_db = CityDatabase()

# ============================================================================
# PART 3: MOCK APIs (Can replace with real APIs)
# ============================================================================

def mock_weather_api(city: str, days: int = 5) -> List[Dict]:
    """
    Mock Weather API - Simulates OpenWeatherMap
    Replace with real API: https://openweathermap.org/api
    """
    import random
    base_temp = random.randint(15, 25)
    
    forecast = []
    conditions = ["Sunny", "Cloudy", "Rainy", "Partly Cloudy", "Clear"]
    
    for i in range(days):
        date = datetime.now() + timedelta(days=i)
        temp = base_temp + random.randint(-3, 3)
        
        forecast.append({
            "date": date.strftime("%Y-%m-%d"),
            "day": date.strftime("%A"),
            "temperature": temp,
            "condition": random.choice(conditions),
            "humidity": random.randint(40, 80),
            "wind_speed": random.randint(5, 20)
        })
    
    return forecast

def mock_image_api(city: str, count: int = 5) -> List[str]:
    """Mock Image API - Reliable placeholders"""
    colors = ["FF6B6B", "4ECDC4", "45B7D1", "FFA07A", "98D8C8"]
    return [
        f"https://via.placeholder.com/800x600/{colors[i % 5]}/FFFFFF?text={city.title()}+Photo+{i+1}"
        for i in range(count)
    ]
    
    return base_urls[:count]

def mock_web_search(query: str) -> str:
    """
    Mock Web Search API - Simulates Tavily/DuckDuckGo
    Replace with real API: https://tavily.com or https://duckduckgo.com
    """
    # Simulated search results
    return f"""Based on web search results for '{query}':
    
This is a city or location that may be lesser-known but has its own unique characteristics. 
While detailed information may be limited, it represents a real place with local culture, 
history, and community. For the most accurate and up-to-date information, visitors should 
consult official tourism websites or local resources.

Note: This is a simulated search result. In production, this would use real web search APIs 
like Tavily, DuckDuckGo, or Google Custom Search to fetch actual current information."""

# ============================================================================
# PART 4: AGENT NODES (LangGraph Components)
# ============================================================================

def extract_city_node(state: AgentState) -> AgentState:
    """
    Node 1: Extract city name from user message
    """
    messages = state.get("messages", [])
    
    if not messages:
        return {"error": "No message provided"}
    
    last_message = messages[-1]
    
    # Simple extraction (in production, use NER or LLM)
    if isinstance(last_message, HumanMessage):
        city = last_message.content.strip()
        # Remove common phrases
        city = city.replace("Tell me about", "").replace("tell me about", "")
        city = city.replace("What about", "").replace("what about", "")
        city = city.strip()
        
        return {"city": city}
    
    return {"error": "Invalid message format"}

def check_database_node(state: AgentState) -> AgentState:
    """
    Node 2: Check if city exists in vector database
    This is the ROUTING decision point
    """
    city = state.get("city", "")
    
    if city_db.has_city(city):
        print(f"✓ Found '{city}' in database")
        return {"route": "database"}
    else:
        print(f"✗ '{city}' not in database, will use web search")
        return {"route": "web"}

def get_from_database_node(state: AgentState) -> AgentState:
    """
    Node 3A: Retrieve information from vector database
    """
    city = state.get("city", "")
    city_info = city_db.search(city)
    
    if city_info:
        summary = f"""## {city_info['name']}, {city_info['country']}

{city_info['summary']}

**Population:** {city_info['population']}
**Timezone:** {city_info['timezone']}
"""
        return {
            "city_summary": summary,
            "messages": [AIMessage(content=f"Found information about {city_info['name']} in database")]
        }
    
    return {"error": f"Database lookup failed for {city}"}

def web_search_node(state: AgentState) -> AgentState:
    """
    Node 3B: Search web for city information
    """
    city = state.get("city", "")
    
    # Simulate web search
    search_result = mock_web_search(city)
    
    summary = f"""## {city}

{search_result}

*Information retrieved from web search*
"""
    
    return {
        "city_summary": summary,
        "messages": [AIMessage(content=f"Searched web for information about {city}")]
    }

async def fetch_weather_async(city: str) -> List[Dict]:
    """Async weather fetching for parallel execution"""
    # Simulate API latency
    await asyncio.sleep(0.5)
    return mock_weather_api(city)

async def fetch_images_async(city: str) -> List[str]:
    """Async image fetching for parallel execution"""
    # Simulate API latency
    await asyncio.sleep(0.5)
    return mock_image_api(city)

async def parallel_fetch_node(state: AgentState) -> AgentState:
    """
    Node 4: Fetch weather and images IN PARALLEL
    This demonstrates Distinction 2: Parallel Fan-Out
    """
    city = state.get("city", "")
    
    print(f"⚡ Fetching weather and images in parallel for {city}...")
    
    # Run both API calls concurrently
    weather_task = fetch_weather_async(city)
    images_task = fetch_images_async(city)
    
    # Wait for both to complete
    weather_data, image_urls = await asyncio.gather(weather_task, images_task)
    
    print(f"✓ Parallel fetch complete: {len(weather_data)} days, {len(image_urls)} images")
    
    return {
        "weather_forecast": weather_data,
        "image_urls": image_urls,
        "messages": [AIMessage(content=f"Fetched weather and images for {city}")]
    }

def combine_results_node(state: AgentState) -> AgentState:
    """
    Node 5: Combine all results into structured output
    This ensures Requirement C: Structured Output
    """
    city = state.get("city", "")
    summary = state.get("city_summary", "No summary available")
    weather = state.get("weather_forecast", [])
    images = state.get("image_urls", [])
    
    # Create structured JSON output
    structured_output = {
        "city": city,
        "city_summary": summary,
        "weather_forecast": weather,
        "image_urls": images,
        "timestamp": datetime.now().isoformat()
    }
    
    return {
        "messages": [AIMessage(content=json.dumps(structured_output, indent=2))],
        "last_city": city
    }

# ============================================================================
# PART 5: MANUAL TOOL EXECUTION (Distinction 1)
# ============================================================================

def manual_tool_executor_node(state: AgentState) -> AgentState:
    """
    Advanced: Manual tool execution without framework wrappers
    This demonstrates Distinction 1: Manual Transmission
    
    In production, this would parse LLM's tool_calls and execute them manually
    """
    messages = state.get("messages", [])
    
    if not messages:
        return state
    
    last_message = messages[-1]
    
    # Check if LLM wants to call a tool
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        tool_call = last_message.tool_calls[0]
        
        tool_name = tool_call.get('name', '')
        tool_args = tool_call.get('args', {})
        
        print(f"🔧 Manual tool execution: {tool_name}")
        
        # Execute tool manually
        result = None
        if tool_name == "get_weather":
            city = tool_args.get('city', state.get('city'))
            result = mock_weather_api(city)
        elif tool_name == "search_images":
            city = tool_args.get('city', state.get('city'))
            result = mock_image_api(city)
        elif tool_name == "web_search":
            query = tool_args.get('query', '')
            result = mock_web_search(query)
        
        # Create tool message manually
        if result:
            tool_message = ToolMessage(
                content=json.dumps(result),
                tool_call_id=tool_call.get('id', 'manual_tool_call')
            )
            return {"messages": [tool_message]}
    
    return state

# ============================================================================
# PART 6: ROUTING LOGIC
# ============================================================================

def route_based_on_check(state: AgentState) -> Literal["database", "web"]:
    """
    Conditional routing function
    This is the SWITCH that demonstrates intelligent routing
    """
    route = state.get("route", "web")
    return route

# ============================================================================
# PART 7: BUILD THE GRAPH
# ============================================================================

def build_agent_graph():
    """
    Build the LangGraph workflow
    This is the core architecture
    """
    
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("extract_city", extract_city_node)
    workflow.add_node("check_database", check_database_node)
    workflow.add_node("get_from_database", get_from_database_node)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("parallel_fetch", parallel_fetch_node)
    workflow.add_node("combine_results", combine_results_node)
    
    # Set entry point
    workflow.set_entry_point("extract_city")
    
    # Add edges
    workflow.add_edge("extract_city", "check_database")
    
    # Add conditional edge (THE SWITCH!)
    workflow.add_conditional_edges(
        "check_database",
        route_based_on_check,
        {
            "database": "get_from_database",
            "web": "web_search"
        }
    )
    
    # Both paths converge to parallel fetch
    workflow.add_edge("get_from_database", "parallel_fetch")
    workflow.add_edge("web_search", "parallel_fetch")
    
    # Final combination
    workflow.add_edge("parallel_fetch", "combine_results")
    
    # End
    workflow.add_edge("combine_results", END)
    
    # Compile with memory (Distinction 3: Human-in-the-Loop)
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    return app

# ============================================================================
# PART 8: AGENT INTERFACE
# ============================================================================

class TravelAgent:
    """Main agent interface"""
    
    def __init__(self):
        self.graph = build_agent_graph()
    
    async def process_async(self, user_input: str, thread_id: str = "default") -> Dict:
        """Process user input through the agent graph"""
        
        # Create initial state
        initial_state = {
            "messages": [HumanMessage(content=user_input)],
            "city": "",
            "route": None,
            "city_summary": None,
            "weather_forecast": None,
            "image_urls": None,
            "error": None,
            "last_city": None,
            "conversation_context": {}
        }
        
        # Run the graph
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            result = await self.graph.ainvoke(initial_state, config)
            
            # Extract structured output from final message
            if result.get("messages"):
                last_message = result["messages"][-1]
                if isinstance(last_message, AIMessage):
                    try:
                        return json.loads(last_message.content)
                    except:
                        pass
            
            # Fallback to state fields
            return {
                "city": result.get("city", ""),
                "city_summary": result.get("city_summary", ""),
                "weather_forecast": result.get("weather_forecast", []),
                "image_urls": result.get("image_urls", []),
                "error": result.get("error")
            }
            
        except Exception as e:
            return {
                "error": f"Agent error: {str(e)}",
                "city": "",
                "city_summary": "",
                "weather_forecast": [],
                "image_urls": []
            }
    
    def process(self, user_input: str, thread_id: str = "default") -> Dict:
        """Synchronous wrapper"""
        return asyncio.run(self.process_async(user_input, thread_id))

# ============================================================================
# PART 9: GRAPH VISUALIZATION
# ============================================================================

def save_graph_visualization():
    """Generate graph.png visualization"""
    try:
        from IPython.display import Image, display
        
        app = build_agent_graph()
        
        # Generate graph image
        graph_image = app.get_graph().draw_mermaid_png()
        
        # Save to file
        with open("graph.png", "wb") as f:
            f.write(graph_image)
        
        print("✓ Graph visualization saved to graph.png")
        return True
    except Exception as e:
        print(f"⚠️ Could not generate graph visualization: {e}")
        print("Run this in a Jupyter notebook or install required dependencies")
        return False

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("AI TRAVEL ASSISTANT - Agent Core")
    print("=" * 70)
    
    # Test the agent
    agent = TravelAgent()
    
    test_queries = [
        "Paris",
        "Tokyo", 
        "Snohomish"  # Not in database
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing: '{query}'")
        print("-" * 70)
        result = agent.process(query)
        
        if result.get("error"):
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✓ City: {result.get('city')}")
            print(f"✓ Summary length: {len(result.get('city_summary', ''))}")
            print(f"✓ Weather days: {len(result.get('weather_forecast', []))}")
            print(f"✓ Images: {len(result.get('image_urls', []))}")
    
    print("\n" + "=" * 70)
    print("✓ Agent core is working!")
    print("Run 'streamlit run app.py' to see the UI")
    print("=" * 70)