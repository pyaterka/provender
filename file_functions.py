from pathlib import Path
from datetime import datetime
import json

def get_conversation_filename():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    conv_dir = Path("conversations")
    conv_dir.mkdir(exist_ok=True)
    return conv_dir / f"{timestamp}_conversation.json", timestamp

def save_conversation(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def create_conversation_data(messages, timestamp, system_prompt, total_tokens=0):
    return {
        "conversation_id": timestamp,
        "system_prompt": system_prompt,
        "messages": messages.copy(),
        "total_tokens": total_tokens,
        "last_edited": datetime.now().isoformat() 
    }
