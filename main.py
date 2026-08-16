import argparse
from openai import OpenAI

def main():

    parser = argparse.ArgumentParser(description="AIbot")
    parser.add_argument("userPrompt", type=str, help="Prompt to AI")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()



if __name__ == "__main__":
    main()
