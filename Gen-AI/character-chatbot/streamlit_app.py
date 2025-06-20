import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import textwrap # For formatting output

# --- Configuration ---
# Load API key from environment variable
load_dotenv()

try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
except KeyError:
    st.error("Error: GOOGLE_API_KEY environment variable not set.")
    st.info("Please set it before running the app (e.g., in your terminal: export GOOGLE_API_KEY='YOUR_API_KEY' or set GOOGLE_API_KEY=...).")
    st.stop() # Stop the app if API key is not set

# Define characters and their initial "system instructions"
CHARACTERS = {
    "Einstein": {
        "persona": "You are Albert Einstein. Respond as if you are the brilliant physicist, thoughtful, sometimes whimsical, and always curious about the universe. Use scientific analogies where appropriate, but explain them simply. You appreciate deep questions and can be a bit philosophical.",
        "start_chat": "Greetings! A pleasure to engage in discourse with a fellow seeker of knowledge. What cosmic queries do you ponder today?"
    },
    "Cleopatra": {
        "persona": "You are Cleopatra, the last pharaoh of Egypt. Respond with regal authority, a touch of wit, and an awareness of your historical context. You might allude to ancient Egypt, power, and legacy.",
        "start_chat": "Welcome, humble seeker. What wisdom or intrigue brings you before the Queen of the Nile?"
    },
    "Spider-Man": {
        "persona": "You are Spider-Man (Peter Parker). Respond with a youthful, slightly nerdy, and humorous tone. Make jokes, reference web-slinging, and always try to do the right thing. You might mention Aunt May or daily struggles.",
        "start_chat": "Hey there! Your friendly neighborhood Spider-Man is on duty. What's shakin', web-head?"
    },
    # Add more characters here!
    "Shakespeare": {
        "persona": "Thou art William Shakespeare, the Bard of Avon. Speak in eloquent, theatrical, and poetic language, full of iambic pentameter and dramatic flair. Allude to your plays and sonnets, and perhaps a touch of historical Elizabethan life.",
        "start_chat": "Hark! What muse doth grace this digital stage? Speak, good sirrah, and let thy thoughts unfold in verse!"
    }
}

# --- Streamlit App Layout and Logic ---

st.set_page_config(page_title="Imaginary Character Chatbot", layout="centered")
st.title("🎭 Imaginary Character Chatbot")
st.markdown("Have a conversation with your favorite historical figure or fictional character!")

# Session State for storing chat history and current character
# Streamlit's `st.session_state` is crucial for maintaining state across reruns
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_character" not in st.session_state:
    st.session_state.current_character = None
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None

# Sidebar for character selection and chat controls
with st.sidebar:
    st.header("Choose Your Companion")
    
    # Dropdown to select character
    character_options = ["Select a character"] + list(CHARACTERS.keys())
    selected_character_name = st.selectbox(
        "Who would you like to chat with?",
        character_options,
        key="character_selector"
    )

    # Logic to switch characters
    if selected_character_name != "Select a character" and selected_character_name != st.session_state.current_character:
        st.session_state.current_character = selected_character_name
        
        # Reset chat for a new character
        st.session_state.messages = [] 
        st.session_state.chat_session = None # Reset the Gemini chat session

        # Initialize new chat session with persona
        persona_prompt = CHARACTERS[selected_character_name]["persona"]
        model = genai.GenerativeModel(
            model_name='gemini-2.0-flash',
            system_instruction=persona_prompt
        )
        st.session_state.chat_session = model.start_chat(history=[])
        
        # Add initial greeting from character
        initial_greeting = CHARACTERS[selected_character_name]["start_chat"]
        st.session_state.messages.append({"role": "assistant", "content": initial_greeting})
        st.rerun() # Rerun to update the main chat window -- CHANGED FROM st.experimental_rerun()

    st.markdown("---")
    if st.button("Start New Chat", help="Clear the current conversation and start fresh with the selected character."):
        if st.session_state.current_character:
            st.session_state.messages = []
            
            # Re-initialize the chat session with the current character's persona
            persona_prompt = CHARACTERS[st.session_state.current_character]["persona"]
            model = genai.GenerativeModel(
                model_name='gemini-pro',
                system_instruction=persona_prompt
            )
            st.session_state.chat_session = model.start_chat(history=[])
            
            # Add initial greeting again
            initial_greeting = CHARACTERS[st.session_state.current_character]["start_chat"]
            st.session_state.messages.append({"role": "assistant", "content": initial_greeting})
            st.info(f"New chat started with {st.session_state.current_character}!")
            st.rerun() # Rerun to update the main chat window -- CHANGED FROM st.experimental_rerun()
        else:
            st.warning("Please select a character first to start a new chat.")

# --- Main Chat Display Area ---

if st.session_state.current_character:
    st.subheader(f"Conversation with {st.session_state.current_character}")

    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input for user
    user_input = st.chat_input("Say something to your character...")

    if user_input:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Generate assistant response using Gemini
        if st.session_state.chat_session:
            with st.spinner(f"{st.session_state.current_character} is thinking..."):
                try:
                    response = st.session_state.chat_session.send_message(user_input)
                    assistant_response = response.text
                except Exception as e:
                    assistant_response = f"An error occurred: {e}"
                    st.error("There was an error getting a response. Please try again.")
            
            # Add assistant message to history
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            with st.chat_message("assistant"):
                st.markdown(assistant_response)
        else:
            st.warning("Please select a character from the sidebar to start chatting.")

else:
    st.info("Please select a character from the sidebar to begin your conversation!")

st.markdown("---")
st.markdown("Powered by Google Gemini AI")