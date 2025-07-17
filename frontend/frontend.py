import streamlit as st
import requests
import time
import json
from typing import Dict, Any

st.title("Neurologix Smart Search Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Query the backend API
    def query_backend(question: str) -> Dict[str, Any]:
        """Send query to backend API and return response"""
        try:
            response = requests.post(
                "http://localhost:8000/api/v1/query",
                json={"question": question},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to connect to backend: {str(e)}")
            return {
                "answer": "Sorry, I'm having trouble processing your request right now. Please try again later.",
                "confidence": 0.0,
                "source_modules": [],
                "metadata": {}
            }

    # Streamed response generator
    def response_generator(backend_response: Dict[str, Any]):
        """Generate streaming response from backend data"""
        answer = backend_response.get("answer", "No response available")
        confidence = backend_response.get("confidence", 0.0)
        modules = backend_response.get("source_modules", [])
        
        # Stream the main answer
        for word in answer.split():
            yield word + " "
            time.sleep(0.03)
        
        yield "\n\n"
        
        # Add metadata information
        if confidence > 0:
            yield f"**Confidence:** {confidence:.1%}\n"
        if modules:
            yield f"**Data Sources:** {', '.join(modules)}\n"

    # Get backend response
    backend_response = query_backend(prompt)
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        response = st.write_stream(response_generator(backend_response))
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})