
import os
import sys
from openai import OpenAI
from dotenv import load_dotenv
from prompts import system_prompt
from file_functions import get_conversation_filename, save_conversation, create_conversation_data
from pathlib import Path
from datetime import datetime


def main():


    load_dotenv()
    client = OpenAI(
        api_key=os.environ.get('OPENAI_API_KEY'),
        base_url="https://api.deepseek.com")

    model = os.environ.get('DEFAULT_MODEL')

    messages =[
        {"role": "system", "content": system_prompt}
    ]

    total_tokens_used = 0

    conversation_file, timestamp = get_conversation_filename()

    try:
        while True:
            user_prompt = input("You: ")

            if user_prompt.lower() in ["clear"]:
                save_conversation(conversation_file, create_conversation_data(messages, timestamp, system_prompt, total_tokens_used))

                messages =[
                    {"role": "system", "content": system_prompt}
                ]
                conversation_file, timestamp = get_conversation_filename()
                print("Conversation saved and cleared. Starting fresh!")
                continue    
            elif user_prompt.lower() in ["exit", "quit"]:
                save_conversation(conversation_file, create_conversation_data(messages, timestamp, system_prompt, total_tokens_used))
                break
            elif user_prompt.lower() in ["help", "/help"]:
                print("Commands: clear, exit, quit")
                continue
            elif user_prompt.lower().startswith("system "):
                parts = user_prompt.split()
                allowed_models = ["deepseek-v4-pro", "deepseek-v4-flash"]
                if parts[1] in allowed_models:
                    model = parts[1]
                    print(f"{model} is set as a reasoning model")
                    continue
                else:
                    print(f"Not a valid reasoning model")
                    continue

            elif not user_prompt.strip():
                continue
            else:
                messages.append({"role": "user", "content": user_prompt})

            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    stream=False,
                    reasoning_effort="high",
                    extra_body={"thinking": {"type": "enabled"}}
                )
            except Exception as e:
                print(f"Error : {e}")
                break

            print(response.choices[0].message.content)

            print(f"Prompt tokens: {response.usage.prompt_tokens}")
            print(f"Completion tokens: {response.usage.completion_tokens}")
            print(f"Total tokens: {response.usage.total_tokens}")

            assistant_reply = response.choices[0].message.content

            messages.append({"role": "assistant", "content": assistant_reply})

            total_tokens_used += response.usage.total_tokens

            save_conversation(conversation_file, create_conversation_data(messages, timestamp, system_prompt, total_tokens_used))

    except KeyboardInterrupt:
        save_conversation(conversation_file, create_conversation_data(messages, timestamp, system_prompt, total_tokens_used))
        
        print("\nGoodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()
