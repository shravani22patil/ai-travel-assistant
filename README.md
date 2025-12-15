# AI Travel Assistant

An intelligent travel assistant that decides whether to use local data or search the web, built with LangGraph and Streamlit.

## What I Built

I wanted to create something smarter than just another chatbot that searches everything. The main idea is simple: if I already know about a city, why waste time searching? But if someone asks about a random small town, then yeah, search for it.

### How It Decides

I set up the agent to check a local database first. Right now it knows about three cities really well - Paris, Tokyo, and New York. I picked these because they're popular and have lots to talk about.

When you ask about Paris:
- Agent checks: "Do I know this city?"
- Finds it in the database
- Grabs the info instantly (no API calls needed)
- Then fetches weather and photos separately

When you ask about something like "Snohomish" (a small town):
- Agent checks: "Do I know this?"
- Nope, not in database
- Falls back to web search
- Gets what it can find
- Still grabs weather and photos

The whole point is efficiency. Why search when you already know? This saves time and API costs in a real system.

## The Main Components

### How State Works

I'm using LangGraph's state system to keep track of everything as it flows through the agent. It's basically a dictionary that gets passed around with:
- What the user asked
- Which city they want
- Whether to use database or web
- The actual data (summary, weather, images)

Pretty straightforward but it works well.

### The Parallel Thing

This was a fun optimization. Weather and images are completely independent - one doesn't need the other. So why fetch them one after another? I set them up to run at the same time using asyncio. 

Before: Wait for weather (1 sec) → Wait for images (1 sec) = 2 seconds total
After: Both run together = 1 second total

Easy win.

### Clean Output

I made sure the final output is proper JSON instead of just dumping text. This way the Streamlit UI can actually do something useful with it - make charts, show galleries, format nicely. Nobody wants to read a wall of unformatted text.

## How the Flow Works
```
Someone asks about a city
    ↓
Extract which city they mean
    ↓
Check: Do we have this in the database?
    ↓
    ├─ YES → Grab from database (fast)
    │
    └─ NO  → Search the web (slower)
    ↓
Either way, now fetch weather + images (at the same time)
    ↓
Combine everything into nice JSON
    ↓
Show it in the UI with charts and images
```

That's basically it. The key decision point is that database check in the middle.

## Technical Stuff

### About the Routing

The routing logic is actually pretty simple:
```python
if city in known_cities:
    return "database"
else:
    return "web"
```

I thought about making it fancier with fuzzy matching or something, but honestly this works fine. Keep it simple.

### Why I Used Mocks

Look, I don't have API keys for every service, and I didn't want the demo to break if an API goes down or hits rate limits. So I made mock functions that return realistic-looking data.

The mocks follow the exact same structure as real APIs would. So swapping in real OpenWeatherMap or Unsplash calls later is literally just changing the function implementation. The rest of the code doesn't care.

Weather mock: generates random but reasonable temperatures
Image mock: returns placeholder URLs that actually load
Search mock: returns a basic template response

Works great for demonstrating the concept.

### What I'm Using

- **LangGraph** - for the agent flow and state management
- **Streamlit** - UI because it's quick to build
- **Plotly** - makes nice looking charts for the weather
- **ChromaDB concept** - I say concept because I'm just using a dict right now, but it's structured like a vector store would be

## Running This Thing

### Setup
```bash
pip install -r requirements.txt
```

### Start It Up
```bash
streamlit run app.py
```

Browser should open automatically to localhost:8501.

### Test the Database Path
Try these cities - they're in the local database:
- Paris
- Tokyo  
- New York

You'll see "Retrieved from database (fast path)" at the top.

### Test the Web Search Path
Try literally any other city:
- London
- Mumbai
- Your hometown
- Whatever

You'll see "Retrieved from web search" instead.

## Stuff I Had to Figure Out

### The Tool Execution Thing

The assignment mentioned building tool execution manually instead of using the prebuilt stuff. I did that to show I actually understand what's happening under the hood, not just calling framework magic methods.

Basically when the LLM wants to call a tool, it returns a structured request. My code parses that, figures out which function to call, executes it, and formats the response back. It's more work but you learn what's actually going on.

### Parallel Is Better

I mean this one was pretty obvious once I thought about it. Weather and images don't depend on each other at all. Fetching them one by one was just wasting time. asyncio.gather() makes them run simultaneously and wait for both to finish.

In a real app with actual API latency, this would be way more noticeable. Even in the mock version it's slightly faster.

### Why Mock Everything?

A few reasons:
1. Don't want to leak API keys in the repo
2. Don't want the demo to break if an API is down
3. Rate limits are annoying during development
4. Mocks are faster and more predictable

The mock functions have the exact same signatures as real API calls would. When you're ready for production, just swap the implementation. The agent doesn't know or care.

## Problems I Ran Into

### Import Hell

Streamlit does this hot-reload thing which is cool but it kept messing up my imports. Sometimes app.py couldn't find main.py even though they're in the same folder. 

Fixed it by explicitly adding the current directory to sys.path. Not elegant but it works.

### Images Not Loading

Originally used Unsplash's URL API but it was unreliable. Sometimes worked, sometimes didn't. Probably rate limiting or something.

Switched to placeholder.com URLs which are way more reliable for a demo. In production you'd use a proper image API with auth.

### The State Type Thing

LangGraph wants you to use TypedDict for state, and it actually matters. I tried just using a regular dict at first and kept getting weird errors. Once I properly typed everything it worked fine.

Lesson: just follow their type hints, it'll save you debugging time.

## What I'd Add With More Time

- Real API connections (OpenWeather, Unsplash, Tavily) instead of mocks
- Actual conversation memory with the LangGraph checkpointer
- More cities in the database
- Cache layer so we don't re-fetch the same weather multiple times
- Better natural language understanding for the queries
- Maybe some error recovery if APIs fail

## Files In Here
```
ai-travel-assistant/
├── main.py              # The agent brain, all the LangGraph stuff
├── app.py               # Streamlit UI code
├── requirements.txt     # What to pip install
├── graph.png           # Diagram of how the agent flows
└── README.md           # You're reading it
```

## Assignment Requirements Check

Just to make sure I hit everything:

✅ **Smart Routing** - Checks database before searching web  
✅ **Clean Output** - Returns JSON with separate fields for summary, weather array, images  
✅ **Parallel Stuff** - Weather and images fetch at the same time  
✅ **Good Code** - Split into functions, not one giant blob  
✅ **Works** - Actually runs and shows stuff in a browser  

## Quick Note

This is meant to show I understand how to build an agent that makes decisions. The APIs are mocked but they're structured exactly like real ones, so connecting actual services is straightforward.

The focus here is on the decision-making architecture and the agent flow, not on API integration complexity. Anyone can call an API - the interesting part is deciding WHICH API to call and WHEN.

---

Built for the AI Engineer internship challenge, December 2024.
