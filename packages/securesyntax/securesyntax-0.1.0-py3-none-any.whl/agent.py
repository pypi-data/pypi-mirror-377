import os
import json
from colorama import Fore, init
from google import genai

CONFIG_FILE = os.path.expanduser("~/.securesyntax_config.json")

init(autoreset=True)

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

def suggest_fix(file):
    with open(file, "r", encoding="utf-8") as f:
        code_content = f.read()

    prompt = (
        "Analyze the following code. If issues exist, return the FULL corrected version "
        "of the file ONLY (no explanations). If the code is fine, respond with: NO_FIX_NEEDED."
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt, code_content],
        )
        output = getattr(response, "text", None) or str(response)
    except Exception as e:
        return f"{Fore.RED}[ERROR]: {Fore.WHITE}Fix request failed ({e})."

    return output.strip()

def apply_fixes():
    dir = os.getcwd()
    code_files = get_files(dir)

    for file in code_files:
        print(f"\n{Fore.YELLOW}Analyzing for fixes: {Fore.BLUE}{file} ...")
        suggestion = suggest_fix(file)

        if suggestion == "NO_FIX_NEEDED":
            print(f"{Fore.GREEN}[GOOD]: {Fore.WHITE}{file} requires no fixes.")
            continue

        print(f"{Fore.CYAN}[FIX SUGGESTED]: {Fore.WHITE}A fix is available for {file}")
        choice = input(f"{Fore.MAGENTA}Apply fix to {file}? (y/n): {Fore.WHITE}")

        if choice.lower() == "y":
            with open(file, "w", encoding="utf-8") as f:
                f.write(suggestion)
            print(f"{Fore.GREEN}[APPLIED]: {Fore.WHITE}Fix applied to {file}")
        else:
            print(f"{Fore.YELLOW}[SKIPPED]: {Fore.WHITE}No changes made to {file}")

if __name__ == "__main__":
    apply_fixes()
