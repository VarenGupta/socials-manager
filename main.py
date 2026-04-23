import streamlit as st
import openai
import sqlite3
import base64
from PIL import Image
import io

# Set up OpenAI
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# System prompt for image generation
SYSTEM_PROMPT = """Generate images that are Instagram-ready with high quality and appropriate resolution (suitable for social media posting).
Use a clean and minimalist theme by default, unless the user explicitly specifies otherwise.
Ensure images are visually appealing, well-composed, and professionally styled.
Focus on creating engaging content that works well on social media platforms.
Make images that are shareable, aesthetic, and optimized for online viewing."""

# Password - you can change this or put in secrets
PASSWORD = st.secrets["PASSWORD"]

# DB setup
conn = sqlite3.connect('sessions.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY,
    username TEXT,
    user_message TEXT,
    assistant_response TEXT,
    response_type TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)''')
conn.commit()

def main():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = ""

    if not st.session_state.authenticated:
        st.title("Login")
        username = st.text_input("Enter username (for logging)")
        password = st.text_input("Enter password", type="password")
        if st.button("Login"):
            if password == PASSWORD:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Wrong password")
    else:
        st.title("Image Chatbot")

        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'response_id' not in st.session_state:
            st.session_state.response_id = None

        # Display chat history
        for msg in st.session_state.messages:
            with st.chat_message(msg['role']):
                if msg['type'] == 'text':
                    st.write(msg['content'])
                elif msg['type'] == 'image':
                    st.image(base64.b64decode(msg['content']))

        # Chat input
        user_input = st.chat_input("Enter your message or image prompt...")
        if user_input:
            # Add user message
            st.session_state.messages.append({'role': 'user', 'type': 'text', 'content': user_input})
            with st.chat_message('user'):
                st.write(user_input)

            # Call Responses API
            with st.spinner("Generating response..."):
                if st.session_state.response_id:
                    response = client.responses.create(
                        model="gpt-5.4",
                        instructions=SYSTEM_PROMPT,
                        previous_response_id=st.session_state.response_id,
                        input=user_input,
                        tools=[{"type": "image_generation"}],
                    )
                else:
                    response = client.responses.create(
                        model="gpt-5.4",
                        instructions=SYSTEM_PROMPT,
                        input=user_input,
                        tools=[{"type": "image_generation"}],
                    )
                st.session_state.response_id = response.id

                # Process outputs
                for output in response.output:
                    if output.type == 'text':
                        content = output.content
                        st.session_state.messages.append({'role': 'assistant', 'type': 'text', 'content': content})
                        with st.chat_message('assistant'):
                            st.write(content)
                        # Store in DB
                        c.execute("INSERT INTO conversations (username, user_message, assistant_response, response_type) VALUES (?, ?, ?, ?)", (st.session_state.username, user_input, content, 'text'))
                    elif output.type == 'image_generation_call':
                        image_base64 = output.result
                        st.session_state.messages.append({'role': 'assistant', 'type': 'image', 'content': image_base64})
                        with st.chat_message('assistant'):
                            st.image(base64.b64decode(image_base64))
                            # Download button
                            byte_im = base64.b64decode(image_base64)
                            st.download_button(
                                label="Download Image",
                                data=byte_im,
                                file_name="generated_image.png",
                                mime="image/png"
                            )
                        # Store in DB
                        c.execute("INSERT INTO conversations (username, user_message, assistant_response, response_type) VALUES (?, ?, ?, ?)", (st.session_state.username, user_input, image_base64, 'image'))
                conn.commit()

        # Show conversation history in sidebar
        with st.sidebar:
            st.subheader("Conversation History")
            c.execute("SELECT username, user_message, assistant_response, response_type, timestamp FROM conversations ORDER BY timestamp DESC LIMIT 20")
            rows = c.fetchall()
            for row in rows:
                with st.expander(f"{row[0]}: {row[1][:50]}... - {row[4]}"):
                    if row[3] == 'text':
                        st.write(f"Assistant: {row[2]}")
                    elif row[3] == 'image':
                        st.image(base64.b64decode(row[2]))

if __name__ == "__main__":
    main()
