import os
import sys
import json
from colorama import init, Fore
from google import genai
from agent import suggest_fix

CONFIG_FILE = os.path.expanduser("~/.securesyntax_config.json")

init(autoreset=True)


def save_api_key(key: str):
    config = {"api_key": key}
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)
    print(f"{Fore.GREEN}[INFO]: {Fore.WHITE}API key saved successfully.")


def load_api_key():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f).get("api_key")
        except Exception:
            pass

    if os.getenv("GEMINI_API_KEY"):
        return os.getenv("GEMINI_API_KEY")

    return None


def create_client():
    api_key = load_api_key()
    if not api_key:
        raise ValueError(
            f"{Fore.RED}[ERROR]: {Fore.WHITE}No API key found! "
            "Run 'securesyntax -key <your_api_key>'"
        )
    return genai.Client(api_key=api_key)


client = None
try:
    client = create_client()
except Exception:
    pass


def get_files(dir):
    code_ext = [".py", ".js", ".java", ".c", ".cpp", ".html", ".htm", ".css", ".ts", ".jsx", ".tsx"]
    files = []
    for root, _, filenames in os.walk(dir):
        for f in filenames:
            if any(f.endswith(ext) for ext in code_ext):
                files.append(os.path.join(root, f))
    return files


def analyse_files(file):
    with open(file, "r", encoding="utf-8") as f:
        code_content = f.read()

    prompt = (
        "Can you tell me what is wrong with this code and how to fix it, "
        "also if there is a way to make the code performance better then tell it, "
        "and what is the security risks if there is any in a short response. "
        "If there are no risks or wrong things then say: 'This file is good to go!'. "
        "Don't answer other questions, just focus on problems and fixes also make your responses consistent."
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt, code_content],
        )
        output = getattr(response, "text", None) or getattr(response, "output_text", None) or str(response)
    except Exception as e:
        return f"{Fore.RED}[ERROR]: {Fore.WHITE}Request failed, please try again later ({e})."

    return f"{Fore.BLUE}◆ {Fore.MAGENTA}[SecureSyntax]: {Fore.WHITE}{output}"


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "-key" and len(sys.argv) == 3:
            save_api_key(sys.argv[2])
            global client
            client = create_client()
            return
        elif sys.argv[1] == "scan":
            pass
        else:
            print(f"{Fore.RED}[ERROR]: {Fore.WHITE}Invalid usage.\n"
                  f"  - Scan project: securesyntax scan\n"
                  f"  - Save API key: securesyntax -key <your_api_key>")
            return

    if not client:
        print(f"{Fore.RED}[ERROR]: {Fore.WHITE}No API key found! "
              "Run 'securesyntax -key <your_api_key>' or set GEMINI_API_KEY.")
        return

    dir = os.getcwd()
    code_files = get_files(dir)
    if not code_files:
        print(f"{Fore.RED}[ERROR]: {Fore.WHITE}No code files found in {dir}!")
        return

    for file in code_files:
        print(f"\n{Fore.YELLOW}Analyzing: {Fore.BLUE}{file} ...")
        result = analyse_files(file)
        if "good to go" in result.lower():
            print(f"{Fore.GREEN}[GOOD]: {Fore.WHITE}{result}")
        else:
            print(result)

        
        print(f"{Fore.BLUE}◆ {Fore.MAGENTA}[SecureSyntax]: {Fore.WHITE}Checking if fixes can be applied...")
        suggestion = suggest_fix(file)

        if suggestion == "NO_FIX_NEEDED":
            print(f"{Fore.GREEN}[GOOD]: {Fore.WHITE}{file} requires no fixes.")
        elif suggestion.startswith("[ERROR]"):
            print(suggestion)
        else:
            print(f"{Fore.CYAN}[FIX SUGGESTED]: {Fore.WHITE}A fix is available for {file}")
            choice = input(f"{Fore.MAGENTA}Apply fix to {file}? (y/n): {Fore.WHITE}")
            if choice.lower() == "y":
                with open(file, "w", encoding="utf-8") as f:
                    f.write(suggestion)
                print(f"{Fore.GREEN}[APPLIED]: {Fore.WHITE}Fix applied to {file}")
            else:
                print(f"{Fore.YELLOW}[SKIPPED]: {Fore.WHITE}No changes made to {file}")


if __name__ == "__main__":
    main()
