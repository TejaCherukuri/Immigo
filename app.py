# app.py
import streamlit as st
import requests

st.set_page_config(page_title="Immigo", layout="wide")
st.title("Immigo")
st.text("I am your amigo built to clarify any immigration questions. Shoot me!")

# Initialize chat session
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display previous chat messages
for role, message in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(message)

# Chat Interface
user_input = st.chat_input("Ask a question about Immigration System")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)

    # Call the API
    try:
        response = requests.post(
            "http://localhost:8000/query",  # update port if different
            json={"user_query": user_input}
        )
        data = response.json()
        assistant_reply = data.get("response", "Something went wrong.")
    except Exception as e:
        assistant_reply = f"Error: {e}"

    with st.chat_message("assistant"):
        st.markdown(assistant_reply)

    st.session_state.chat_history.append(("user", user_input))
    st.session_state.chat_history.append(("assistant", assistant_reply))