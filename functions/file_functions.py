from pathlib import Path
from datetime import datetime

def get_conversation_filename():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    conv_dir = Path("conversations")
    conv_dir.mkdir(exit_ok=True)
    return conv_dir / f"{timestamp}_conversation.json"
