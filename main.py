
import os
from openai import OpenAI
from dotenv import load_dotenv
from prompts import system_prompt

def main():


    load_dotenv()
    client = OpenAI(
        api_key=os.environ.get('OPENAI_API_KEY'),
        base_url="https://api.deepseek.com")

    messages =[
        {"role": "system", "content": system_prompt}
    ]

    while True:

        user_prompt = input("You: ")
        if user_prompt.lower() in ["exit", "quit"]:
            break

        messages.append({"role": "user", "content": user_prompt})
        response = client.chat.completions.create(
            model="deepseek-v4-pro",
            messages=messages,
            stream=False,
            reasoning_effort="high",
            extra_body={"thinking": {"type": "enabled"}}
        )

        print(response.choices[0].message.content)

        print(f"Prompt tokens: {response.usage.prompt_tokens}")
        print(f"Completion tokens: {response.usage.completion_tokens}")
        print(f"Total tokens: {response.usage.total_tokens}")

        assistant_reply = response.choices[0].message.content

        messages.append({"role": "assistant", "content": assistant_reply})



if __name__ == "__main__":
    main()
