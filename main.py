
import os
import sys
from openai import OpenAI
from dotenv import load_dotenv
from prompts import system_prompt
from functions import get_conversation_filename, save_conversation, create_conversation_data
from pathlib import Path
from datetime import datetime


def main():


    load_dotenv()
    client = OpenAI(
        api_key=os.environ.get('OPENAI_API_KEY'),
        base_url="https://api.deepseek.com")

    messages =[
        {"role": "system", "content": system_prompt}
    ]

    conversation_file, timestamp = get_conversation_filename()

    try:
        while True:
            user_prompt = input("You: ")

            if user_prompt.lower() in ["clear"]:
                save_conversation(conversation_file, create_conversation_data(messages, timestamp, system_prompt))

                messages =[
                    {"role": "system", "content": system_prompt}
                ]
                conversation_file, timestamp = get_conversation_filename()
                print("Conversation saved and cleared. Starting fresh!")
                continue    
            elif user_prompt.lower() in ["exit", "quit"]:
                save_conversation(conversation_file, create_conversation_data(messages, timestamp, system_prompt))
                break
            elif user_prompt.lower() in ["help", "/help"]:
                print("Commands: clear, exit, quit")
                continue
            elif not user_prompt.strip():
                continue
            else:
                messages.append({"role": "user", "content": user_prompt})

            try:
                response = client.chat.completions.create(
                    model="deepseek-v4-pro",
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

            save_conversation(conversation_file, create_conversation_data(messages, timestamp, system_prompt))

    except KeyboardInterrupt:
        save_conversation(conversation_file, save_conversation(conversation_file, create_conversation_data(messages, timestamp, system_prompt))
)
        
        print("\nGoodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()
