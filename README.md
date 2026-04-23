# Socials Manager - Image Chatbot

A Streamlit-based multi-turn conversation chatbot with password protection that uses OpenAI's Responses API to generate images and respond with text. Users can chat with the bot, request image generations, download images, and view conversation history stored in SQLite.

## Features

- Password-protected access with username logging
- Multi-turn conversation with AI assistant
- Image generation using OpenAI's Responses API with image_generation tool
- Instagram-ready images with clean, minimalist default theme
- Download generated images
- Conversation history stored in SQLite database with user attribution
- Chat interface with message history
- Sidebar for viewing conversation history

## Setup

1. Install dependencies

2. Set your OpenAI API key and password in `.streamlit/secrets.toml`:
   ```
   OPENAI_API_KEY = "your-api-key-here"
   PASSWORD = "your-password-here"
   ```

## Running the App

```bash
streamlit run main.py
```

## Usage

1. Enter your username and the password to log in.
2. Start chatting with the bot using the chat input at the bottom.
3. The bot can respond with text or generate images based on your requests.
4. Images are generated with Instagram-ready quality and resolution, using a clean minimalist theme by default (override by specifying in your prompt).
5. Download any generated images using the download button.
6. View conversation history in the sidebar, showing recent interactions from all users.