"""
AI TRAVEL ASSISTANT - STREAMLIT UI
===================================

Run this file with:
    streamlit run app.py

This creates the interactive web interface for the travel assistant.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import asyncio
import sys

# Import the agent
try:
    from main import TravelAgent, city_db
except ImportError:
    st.error("⚠️ Could not import main.py. Make sure both files are in the same directory.")
    st.stop()

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="AI Travel Assistant",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .city-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .stat-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 5px;
        text-align: center;
    }
    .stImage {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# INITIALIZE SESSION STATE
# ============================================================================

if 'agent' not in st.session_state:
    st.session_state.agent = TravelAgent()
    
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

if 'current_result' not in st.session_state:
    st.session_state.current_result = None

if 'thread_id' not in st.session_state:
    st.session_state.thread_id = f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_weather_chart(weather_data):
    """Create interactive weather forecast chart using Plotly"""
    if not weather_data:
        return None
    
    df = pd.DataFrame(weather_data)
    
    # Create figure
    fig = go.Figure()
    
    # Add temperature line
    fig.add_trace(go.Scatter(
        x=df['day'],
        y=df['temperature'],
        mode='lines+markers',
        name='Temperature',
        line=dict(color='#FF6B6B', width=3),
        marker=dict(size=10),
        hovertemplate='<b>%{x}</b><br>Temperature: %{y}°C<extra></extra>'
    ))
    
    # Update layout
    fig.update_layout(
        title="5-Day Weather Forecast",
        xaxis_title="Day",
        yaxis_title="Temperature (°C)",
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        height=400
    )
    
    # Add grid
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    
    return fig

def create_weather_table(weather_data):
    """Create detailed weather table"""
    if not weather_data:
        return None
    
    df = pd.DataFrame(weather_data)
    
    # Format for display
    display_df = df[['day', 'temperature', 'condition', 'humidity', 'wind_speed']].copy()
    display_df.columns = ['Day', 'Temp (°C)', 'Condition', 'Humidity (%)', 'Wind (km/h)']
    
    return display_df

def display_image_gallery(image_urls):
    """Display images in a nice gallery layout"""
    if not image_urls:
        st.info("📸 No images available")
        return
    
    st.write(f"Loading {len(image_urls)} images...")
    
    # Create columns for images
    cols = st.columns(3)
    
    for idx, url in enumerate(image_urls[:6]):  # Limit to 6 images
        with cols[idx % 3]:
            try:
                st.write(f"Image {idx + 1}:")
                st.image(url, use_container_width=True)
            except Exception as e:
                st.error(f"Failed to load: {str(e)}")
                # Fallback: Show colored box
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    height: 200px;
                    border-radius: 10px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 24px;
                ">
                    📸 Photo {idx + 1}
                </div>
                """, unsafe_allow_html=True)

def process_query(user_input):
    """Process user query through the agent"""
    with st.spinner('🤔 AI Agent is thinking...'):
        try:
            result = st.session_state.agent.process(
                user_input, 
                thread_id=st.session_state.thread_id
            )
            return result
        except Exception as e:
            return {
                "error": str(e),
                "city": user_input,
                "city_summary": "",
                "weather_forecast": [],
                "image_urls": []
            }

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("### 🌍 AI Travel Assistant")
    st.markdown("---")
    
    st.markdown("#### 📋 Features")
    st.markdown("""
    - ✓ Intelligent routing (DB vs Web)
    - ✓ Real-time weather data
    - ✓ Beautiful image galleries
    - ✓ Interactive visualizations
    - ✓ Conversation memory
    """)
    
    st.markdown("---")
    
    st.markdown("#### 🏙️ Pre-loaded Cities")
    st.markdown("""
    - **Paris** 🇫🇷
    - **Tokyo** 🇯🇵
    - **New York** 🇺🇸
    """)
    
    st.markdown("*Try other cities for web search!*")
    
    st.markdown("---")
    
    st.markdown("#### 💡 Try These")
    example_queries = [
        "Paris",
        "Tokyo",
        "New York",
        "London",
        "Sydney"
    ]
    
    for query in example_queries:
        if st.button(query, key=f"example_{query}"):
            st.session_state.example_query = query
    
    st.markdown("---")
    
    if st.button("🗑️ Clear History"):
        st.session_state.conversation_history = []
        st.session_state.current_result = None
        st.rerun()
    
    st.markdown("---")
    st.markdown("#### 📊 Statistics")
    st.metric("Queries", len(st.session_state.conversation_history))

# ============================================================================
# MAIN CONTENT
# ============================================================================

# Header
st.markdown('<p class="main-header">🌍 AI Travel Assistant</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Discover cities with intelligent AI-powered insights</p>', unsafe_allow_html=True)

# Input section
col1, col2 = st.columns([4, 1])

with col1:
    # Check if there's an example query
    default_value = ""
    if hasattr(st.session_state, 'example_query'):
        default_value = st.session_state.example_query
        delattr(st.session_state, 'example_query')
    
    user_input = st.text_input(
        "Which city would you like to explore?",
        value=default_value,
        placeholder="E.g., Paris, Tokyo, or any city name...",
        label_visibility="collapsed"
    )

with col2:
    explore_button = st.button("🔍 Explore", type="primary", use_container_width=True)

# Process query
if explore_button and user_input:
    # Process the query
    result = process_query(user_input)
    
    # Store in session state
    st.session_state.current_result = result
    st.session_state.conversation_history.append({
        "query": user_input,
        "result": result,
        "timestamp": datetime.now()
    })

# Display results
if st.session_state.current_result:
    result = st.session_state.current_result
    
    # Check for errors
    if result.get("error"):
        st.error(f"❌ Error: {result['error']}")
        st.info("💡 Try rephrasing your query or check your API configuration.")
    else:
        # Success! Display everything
        
        # City Summary Section
        st.markdown("---")
        st.markdown("## 📝 City Information")
        
        # Check routing decision
        city = result.get("city", "Unknown")
        if city_db.has_city(city):
            st.success(f"✓ Retrieved from database (fast path)")
        else:
            st.info(f"🔍 Retrieved from web search")
        
        # Display summary
        if result.get("city_summary"):
            st.markdown(result["city_summary"])
        else:
            st.warning("No summary available")
        
        # Weather Section
        st.markdown("---")
        st.markdown("## 🌤️ Weather Forecast")
        
        weather_data = result.get("weather_forecast", [])
        
        if weather_data:
            # Create two columns
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Interactive chart
                fig = create_weather_chart(weather_data)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Could not create weather chart")
            
            with col2:
                # Weather stats
                st.markdown("### 📊 Quick Stats")
                
                if weather_data:
                    avg_temp = sum(d['temperature'] for d in weather_data) / len(weather_data)
                    max_temp = max(d['temperature'] for d in weather_data)
                    min_temp = min(d['temperature'] for d in weather_data)
                    
                    st.metric("Average Temp", f"{avg_temp:.1f}°C")
                    st.metric("High", f"{max_temp}°C")
                    st.metric("Low", f"{min_temp}°C")
            
            # Detailed table
            st.markdown("### 📋 Detailed Forecast")
            weather_table = create_weather_table(weather_data)
            if weather_table is not None:
                st.dataframe(weather_table, use_container_width=True, hide_index=True)
        else:
            st.warning("No weather data available")
         
      # Image Gallery Section
    st.markdown("---")
    st.markdown("## 📸 Photo Gallery")

    image_urls = result.get("image_urls", [])

       # DEBUG: Show what we got
    st.write(f"**Debug:** Got {len(image_urls)} image URLs")
    st.write("**URLs:**", image_urls)

    if image_urls:
        st.write("Displaying images...")
        display_image_gallery(image_urls)
    else:
        st.warning("No images available")
        
        # Additional Info
        st.markdown("---")
        st.markdown("### ℹ️ Information")
        
        info_col1, info_col2, info_col3 = st.columns(3)
        
        with info_col1:
            st.markdown("**Data Sources**")
            st.markdown("- City Database")
            st.markdown("- Weather API")
            st.markdown("- Image API")
        
        with info_col2:
            st.markdown("**Last Updated**")
            st.markdown(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        with info_col3:
            st.markdown("**AI Model**")
            st.markdown("GPT-4o / Claude 3.5")

# ============================================================================
# CONVERSATION HISTORY
# ============================================================================

if st.session_state.conversation_history:
    with st.expander("📜 Conversation History", expanded=False):
        for idx, conv in enumerate(reversed(st.session_state.conversation_history[-5:])):
            st.markdown(f"**{idx + 1}. {conv['query']}** - {conv['timestamp'].strftime('%H:%M:%S')}")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>🤖 Powered by LangGraph + Streamlit + OpenAI</p>
    <p>Built with ❤️ for AI Engineering Assignment</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# DEBUG INFO (Optional)
# ============================================================================

if st.checkbox("🔧 Show Debug Info", value=False):
    st.markdown("### Debug Information")
    
    st.json({
        "thread_id": st.session_state.thread_id,
        "queries_count": len(st.session_state.conversation_history),
        "current_result_available": st.session_state.current_result is not None,
        "agent_initialized": st.session_state.agent is not None
    })
    
    if st.session_state.current_result:
        st.markdown("### Current Result (Raw)")
        st.json(st.session_state.current_result)