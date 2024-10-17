import openai
import argparse
import json
import os
from datetime import datetime
from openai import OpenAI

# Get the current working directory (PWD)
PWD = os.path.dirname(os.path.abspath(__file__))

# Constants for file paths, now using the absolute path
CONVERSATIONS_DIR = os.path.join(PWD, "conversations")
CONTEXT_FILE = os.path.join(PWD, "context.json")
CONFIG_FILE = os.path.join(PWD, "config.json")

# Initialize directories and files for conversation history
if not os.path.exists(CONVERSATIONS_DIR):
    os.makedirs(CONVERSATIONS_DIR)

# Function to load API key from config.json
def load_api_key():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            return config.get("openai_api_key")
    raise FileNotFoundError(f"Config file '{CONFIG_FILE}' not found. Please create it with your OpenAI API key.")

# Load previous context (conversation history)
def load_context():
    if os.path.exists(CONTEXT_FILE):
        with open(CONTEXT_FILE, 'r') as f:
            return json.load(f)
    return []

# Save context after each conversation
def save_context(context):
    with open(CONTEXT_FILE, 'w') as f:
        json.dump(context, f, indent=4)

# Function to save conversation
def save_conversation(conversation):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"conversation_{timestamp}.json"
    file_path = os.path.join(CONVERSATIONS_DIR, file_name)

    with open(file_path, 'w') as f:
        json.dump(conversation, f, indent=4)
    
    print(f"Conversation saved as {file_name}")

# Function to interact with OpenAI API
def get_openai_response(client, messages, model):
    response = client.chat.completions.create(
        model=model,
        messages=messages
    )
    return response.choices[0].message.content.strip()
# response['choices'][0]['message']['content']

# CLI interface for interactive chat session
def main(client, args):
    print("Welcome to the chatbot CLI. Type 'exit' to end the session.")
    
    # Load context from previous sessions
    context = load_context()

    # Create a list to hold the current conversation
    conversation = []

    while True:
        # Get user input from CLI
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break

        # Add the user input to the conversation
        conversation.append({"role": "user", "content": user_input})
        
        # Add to the context for the API call
        context.append({"role": "user", "content": user_input})

        # Call OpenAI API with the conversation context
        try:
            response = get_openai_response(client, context, args.model)
            print(f"Bot: {response}")
            
            # Add the bot response to the conversation and context
            conversation.append({"role": "assistant", "content": response})
            context.append({"role": "assistant", "content": response})
        except Exception as e:
            print(f"Error: {e}")
            break

    # Save the current conversation
    save_conversation(conversation)

    # Save the updated context
    save_context(context)

if __name__ == "__main__":
    # Argument parser setup
    parser = argparse.ArgumentParser(description="Chatbot CLI using OpenAI API.")
    
    parser.add_argument(
        '--model', 
        type=str, 
        default="gpt-3.5-turbo", 
        help="Specify the OpenAI model to use (default: gpt-3.5-turbo)"
    )
    
    # Load the API key from the config.json file securely
    api_key = load_api_key()

    parser.add_argument(
        '--api_key', 
        type=str, 
        default=api_key, 
        help="OpenAI API key (loaded from config.json)"
    )

    args = parser.parse_args()

    client = OpenAI(
        # defaults to os.environ.get("OPENAI_API_KEY")
        api_key=args.api_key,
    )

    

    main(client, args)
