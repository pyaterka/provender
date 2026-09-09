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
    first_user_msg = ""
    for msg in messages:
        if msg.get("role") == "user":
            content = msg.get("content", "")
            if len(content) > 50:
                first_user_msg = content[:50] + "..."
            else:
                first_user_msg = content
            break
    return {
        "conversation_id": timestamp,
        "system_prompt": system_prompt,
        "messages": messages.copy(),
        "total_tokens": total_tokens,
        "last_edited": datetime.now().isoformat(),
        "metadata": {
            "message_count": len(messages),
            "first_user_message": first_user_msg,
            "has_save_name": False,
            "name": None
        }

    }

def get_conversation_files():

    """Get all conversation files sorted by date (newest first)"""

    conv_dir = Path("conversations")
    if not conv_dir.exists():
        return []
    return sorted(conv_dir.glob("*.json"), reverse=True)


def get_conversation_preview(filepath):

    """Extract preview info from a conversation file"""

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)

        # Get metadata
        conv_id = data.get("conversation_id", "Unknown")
        msg_count = len(data.get("messages", []))
        total_tokens = data.get("total_tokens", 0)

        # Get first user message
        first_msg = ""
        for msg in data.get("messages", []):
            if msg.get("role") == "user":
                content = msg.get("content", "")
                if len(content) > 60:
                    first_msg = content[:60] + "..."
                else:
                    first_msg = content
                break

        # Get custom name if set
        name = data.get("metadata", {}).get("name", None)
        if name:
            display_name = f"📌 {name}"
        else:
            display_name = conv_id

        return {
            "filepath": filepath,
            "display_name": display_name,
            "conversation_id": conv_id,
            "message_count": msg_count,
            "total_tokens": total_tokens,
            "first_message": first_msg,
            "has_name": bool(name),
            "name": name
        }
    except Exception as e:
        return {
            "filepath": filepath,
            "display_name": f"⚠️ {filepath.name}",
            "error": str(e)
        }


def load_conversation(filepath):

    """Load a conversation from file and return the messages"""

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading conversation: {e}")
        return None


def display_conversation(data, show_numbers=False):
    """
    Display a conversation in a readable format.
        
    Args:
        data: The conversation data from JSON
        show_numbers: If True, shows message numbers
    """

    if not data:
        print("❌ No conversation data to display.")
        return
    print("\n" + "="*70)
    print(f"📅 Conversation: {data.get('conversation_id', 'Unknown')}")
    print(f"🪙 Total Tokens: {data.get('total_tokens', 0)}")
    print(f"📝 Last Edited: {data.get('last_edited', 'Unknown')}")
    
    # Show custom name if exists
    metadata = data.get("metadata", {})
    if metadata.get("name"):
        print(f"📌 Name: {metadata.get('name')}")
    
    print("="*70)
    
    messages = data.get("messages", [])
    
    for i, msg in enumerate(messages, 1):
        role = msg.get("role", "unknown").upper()
        content = msg.get("content", "")
        
        if role == "SYSTEM":
            print(f"\n🤖 [SYSTEM PROMPT]:")
            print(content)
            print("-"*70)
            continue
        
        # Display user/assistant messages
        emoji = "👤" if role == "USER" else "🤖"
        if show_numbers:
            print(f"\n{emoji} [{role}] #{i}:")
        else:
            print(f"\n{emoji} [{role}]:")
        print(content)
        print("-"*70)
    
    print(f"\n💬 Total Messages: {len(messages)}")
    


