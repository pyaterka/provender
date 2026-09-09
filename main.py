
import os
import sys
from openai import OpenAI
from dotenv import load_dotenv
from prompts import system_prompt
from file_functions import get_conversation_filename, save_conversation, create_conversation_data, get_conversation_files, get_conversation_preview, load_conversation, display_conversation
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

    total_tokens = 0

    conversation_file, timestamp = get_conversation_filename()

    try:
        while True:
            user_prompt = input("You: ")

            if user_prompt.lower() in ["clear"]:
                save_conversation(conversation_file, create_conversation_data(messages, timestamp, system_prompt, total_tokens))

                messages =[
                    {"role": "system", "content": system_prompt}
                ]
                conversation_file, timestamp = get_conversation_filename()
                print("Conversation saved and cleared. Starting fresh!")
                continue  

            elif user_prompt.lower() in ["exit", "quit"]:
                save_conversation(conversation_file, create_conversation_data(messages, timestamp, system_prompt, total_tokens))
                break

            elif user_prompt.lower() in ["list", "/list"]:
                # Show all available conversations
                files = get_conversation_files()
                if not files:
                    print("📭 No saved conversations found.")
                    continue

                print("\n📁 Saved Conversations:")
                print("-" * 60)

                for i, file in enumerate(files, 1):
                    preview = get_conversation_preview(file)
                    if preview.get("error"):
                        print(f"{i}. ⚠️ {preview['display_name']}")
                    else:
                        print(f"{i}. {preview['display_name']}")
                        print(f"   📝 {preview['first_message']}")
                        print(f"   💬 {preview['message_count']} messages | 🪙 {preview['total_tokens']} tokens")
                        print()

                continue

            elif user_prompt.lower() == ("/recent"):

                files  = get_conversation_files()
                if not files:
                    print("📭 No saved conversations found.")
                    continue

                filepath = files[0]
                data = load_conversation(filepath) 

                if data:
                    print("\n📖 PREVIEWING MOST RECENT CONVERSATION:")
                    display_conversation(data, show_numbers=False)

                    print("\n" + "="*70)
                    choice = input("🔀 Load this conversation? (y/n): ").lower().strip()
                    if choice.lower() in ["yes", "y"]:
                        messages = data.get("messages", [])
                        total_tokens = data.get("total_tokens", 0)
                        timestamp = data.get("conversation_id")
                        conversation_file = filepath
                    
                        print(f"\n✅ Loaded conversation: {data.get('conversation_id')}")
                        print(f"   Messages: {len(messages)}")
                        print(f"   Tokens: {total_tokens}")
                        print("\n💬 You can now continue chatting!")
                    else:
                        print("✅ Kept current conversation.")
                else:
                    print("❌ Failed to load conversation.")
                continue

            elif user_prompt.lower().startswith("/load "):

                parts = user_prompt.split()
                if len(parts) < 2:
                    print("Usage: /load <number> (e.g., /load 1)")
                    continue

                try:
                    idx = int(parts[1]) - 1
                    files  = get_conversation_files()

                    if 0 <= idx < len(files):
                        filepath = files[idx]
                        data = load_conversation(filepath)

                        if data:
                            print("\n📖 PREVIEWING CONVERSATION:")
                            display_conversation(data, show_numbers=False)

                            print("\n" + "="*70)
                            choice = input("🔀 Load this conversation? (y/n): ").lower().strip()

                            if choice.lower() in ["yes", "y"]:
                                messages = data.get("messages", [])
                                total_tokens = data.get("total_tokens", 0)
                                timestamp = data.get("conversation_id")
                                conversation_file = filepath

                                print(f"\n✅ Loaded conversation: {data.get('conversation_id')}")
                                print(f"   Messages: {len(messages)}")
                                print(f"   Tokens: {total_tokens}")
                                print("\n💬 You can now continue chatting!")
                            else:
                                print("✅ Kept current conversation.")
                        else:
                            print("❌ Failed to load conversation.")
                    else:
                        print("❌ Invalid number. Use /list to see available conversations.")
                except ValueError:
                    print("❌ Please enter a valid number.")
                continue

            elif user_prompt.lower() in ["help", "/help"]:
                print("\n📖 Commands:")
                print("  clear          - Clear conversation history")
                print("  exit/quit      - Exit program")
                print("  system <model> - Switch model (e.g., system deepseek-v4-pro)")
                print("  list           - Show all saved conversations")
                print("  /load <number> - Preview and load a saved conversation")
                print("  /recent        - Preview and load the most recent conversation")
                print("  help           - Show this message")
                continue

            elif user_prompt.lower().startswith("system "):
                parts = user_prompt.split()
                if len(parts) < 2:
                    print("❌ Please specify a model. Usage: system <model>")
                    print(f"   Available: deepseek-v4-pro, deepseek-v4-flash")
                    continue
    
                allowed_models = ["deepseek-v4-pro", "deepseek-v4-flash"]
                new_model = parts[1]
    
                if new_model in allowed_models:
                    model = new_model
                    print(f"✅ Model switched to: {model}")
                else:
                    print(f"❌ Invalid model: {new_model}")
                    print(f"   Available models: {', '.join(allowed_models)}")
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

            total_tokens += response.usage.total_tokens

            save_conversation(conversation_file, create_conversation_data(messages, timestamp, system_prompt, total_tokens))

    except KeyboardInterrupt:
        save_conversation(conversation_file, create_conversation_data(messages, timestamp, system_prompt, total_tokens))
        
        print("\nGoodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()
