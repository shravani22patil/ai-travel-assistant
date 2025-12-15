import streamlit as st

st.title("🧪 Image Test")

# Test if images work at all
test_url = "https://via.placeholder.com/400x300/FF6B6B/FFFFFF?text=TestImage"

st.write("Testing if images load...")
st.write(f"URL: {test_url}")

try:
    st.image(test_url, width=400)
    st.success("✅ Images work!")
except Exception as e:
    st.error(f"❌ Images don't work: {e}")