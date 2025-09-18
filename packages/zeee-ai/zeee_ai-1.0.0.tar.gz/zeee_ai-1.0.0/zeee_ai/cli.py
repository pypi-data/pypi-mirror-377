import os
import re
import getpass
import ollama
from datetime import datetime
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.completion import Completer, Completion

VERSION = "ZeeE AI v1.0.092025"
DEVELOPER = "Muhammad Aziz ur Rehman (AzizHorea)"
USERNAME = getpass.getuser()
INSTRUCTIONS_FILE = "instructions.txt"
HISTORY_FILE = "history.txt"

ABOUT_TEXT = f"""
ZeeE AI is developed by {DEVELOPER}, an IT Professional with 12+ years of experience.

🌐 Online Profiles:
- LinkedIn:   https://linkedin.com/in/azizhorea
- Facebook:   https://facebook.com/aziz.horea
- Instagram:  https://instagram.com/azizhorea
- Fiverr:     https://fiverr.com/azizhorea
- Upwork:     https://www.upwork.com/freelancers/azizhorea
- GitHub:     https://github.com/AzizHorea
"""

HELP_TEXT = """
Available Commands:
/help         Show this help message
/exit         Exit the assistant
/version      Show ZeeE AI version
/developer    Show developer name
/instructions Show current remembered instructions
/history      Show conversation history
/about        About the developer
"""

ASCII_ART = """
                  ZZZZZZZZZZZZZZZZZZZ                                      EEEEEEEEEEEEEEEEEEEEEE                    AAA               IIIIIIIIII
>>>>>>>           Z:::::::::::::::::Z                                      E::::::::::::::::::::E                   A:::A              I::::::::I
 >:::::>          Z:::::::::::::::::Z                                      E::::::::::::::::::::E                  A:::::A             I::::::::I
  >:::::>         Z:::ZZZZZZZZ:::::Z                                       EE::::::EEEEEEEEE::::E                 A:::::::A            II::::::II
   >:::::>        ZZZZZ     Z:::::Z      eeeeeeeeeeee        eeeeeeeeeeee    E:::::E       EEEEEE                A:::::::::A             I::::I  
    >:::::>               Z:::::Z      ee::::::::::::ee    ee::::::::::::ee  E:::::E                            A:::::A:::::A            I::::I  
     >:::::>             Z:::::Z      e::::::eeeee:::::ee e::::::eeeee:::::eeE::::::EEEEEEEEEE                 A:::::A A:::::A           I::::I  
      >:::::>           Z:::::Z      e::::::e     e:::::ee::::::e     e:::::eE:::::::::::::::E                A:::::A   A:::::A          I::::I  
     >:::::>           Z:::::Z       e:::::::eeeee::::::ee:::::::eeeee::::::eE:::::::::::::::E               A:::::A     A:::::A         I::::I  
    >:::::>           Z:::::Z        e:::::::::::::::::e e:::::::::::::::::e E::::::EEEEEEEEEE              A:::::AAAAAAAAA:::::A        I::::I  
   >:::::>           Z:::::Z         e::::::eeeeeeeeeee  e::::::eeeeeeeeeee  E:::::E                       A:::::::::::::::::::::A       I::::I  
  >:::::>         ZZZ:::::Z     ZZZZZe:::::::e           e:::::::e           E:::::E       EEEEEE         A:::::AAAAAAAAAAAAA:::::A      I::::I  
 >:::::>          Z::::::ZZZZZZZZ:::Ze::::::::e          e::::::::e        EE::::::EEEEEEEE:::::E        A:::::A             A:::::A   II::::::II
>>>>>>>           Z:::::::::::::::::Z e::::::::eeeeeeee   e::::::::eeeeeeeeE::::::::::::::::::::E       A:::::A               A:::::A  I::::::::I
                  Z:::::::::::::::::Z  ee:::::::::::::e    ee:::::::::::::eE::::::::::::::::::::E      A:::::A                 A:::::A I::::::::I
                  ZZZZZZZZZZZZZZZZZZZ    eeeeeeeeeeeeee      eeeeeeeeeeeeeeEEEEEEEEEEEEEEEEEEEEEE     AAAAAAA                   AAAAAAAIIIIIIIIII
"""

# -------- COLOR FUNCTIONS --------
def hex_to_rgb(hex_color): return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
def interpolate_color(c1, c2, f): return tuple(int(c1[i] + (c2[i] - c1[i]) * f) for i in range(3))
def gradient_colors(width):
    stops = [(0.0, "#03001e"), (0.33, "#7303c0"), (0.66, "#ec38bc"), (1.0, "#fdeff9")]
    stops_rgb = [(p, hex_to_rgb(c)) for p, c in stops]
    colors = []
    for i in range(width):
        pos = i / max(width - 1, 1)
        for j in range(len(stops_rgb) - 1):
            if stops_rgb[j][0] <= pos <= stops_rgb[j+1][0]:
                f = (pos - stops_rgb[j][0]) / (stops_rgb[j+1][0] - stops_rgb[j][0])
                colors.append(interpolate_color(stops_rgb[j][1], stops_rgb[j+1][1], f))
                break
    return colors

def colorize_ascii_art(ascii_art):
    lines = ascii_art.strip('\n').split('\n')
    max_width = max(len(line) for line in lines)
    colors = gradient_colors(max_width)
    return "\n".join(
        "".join(f"\x1b[38;2;{*colors[i],}m{ch}" for i, ch in enumerate(line.ljust(max_width))) + "\x1b[0m"
        for line in lines
    )

# -------- AUTOCOMPLETE FILE/FOLDER --------
class FilePathCompleter(Completer):
    def get_completions(self, document, _):
        match = re.search(r'(/[^\\s]*)$', document.text_before_cursor)
        if not match: return
        path_prefix = match.group(1)
        base_dir = os.path.dirname(path_prefix) or "."
        prefix = os.path.basename(path_prefix)
        try:
            for entry in os.listdir(base_dir):
                if entry.startswith(prefix):
                    full = os.path.join(base_dir, entry)
                    yield Completion(entry[len(prefix):], display=entry + ('/' if os.path.isdir(full) else ''))
        except: return

# -------- FILE UTILS --------
def save_instruction(instruction):
    with open(INSTRUCTIONS_FILE, 'a', encoding='utf-8') as f:
        f.write(instruction + "\n")

def load_instructions():
    if os.path.isfile(INSTRUCTIONS_FILE):
        with open(INSTRUCTIONS_FILE, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return ""

def save_history(user_input, response):
    with open(HISTORY_FILE, 'a', encoding='utf-8') as f:
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        f.write(f"{timestamp} {USERNAME} > {user_input}\n")
        f.write(f"{timestamp} ZeeE AI > {response}\n\n")

# -------- MAIN --------
def main():
    print(colorize_ascii_art(ASCII_ART))
    print("Zero Effort, Everything Enabled".center(120))
    print("Making Things Happen | Ask, Discover, Achieve...".center(120))
    print("-" * 120)
    print(f"Hi {USERNAME}, How are you? How may I assist you?")
    print("-" * 120)
    print(f"Files in folder: {', '.join(os.listdir('.'))}")
    print("You can ask about files or mention files like `/example.txt`.")
    print("-" * 120)

    instructions = load_instructions()
    system_messages = [{"role": "system", "content": instructions}] if instructions else []

    session = PromptSession(style=Style.from_dict({'': '#ffffff bg:#000000'}), completer=FilePathCompleter())

    while True:
        try:
            user_input = session.prompt("Ask: ").strip()

            # Command Handling
            if user_input.startswith("/"):
                cmd = user_input.lower()
                if cmd == "/help": print(HELP_TEXT)
                elif cmd == "/exit": print(f"Goodbye! {USERNAME} See you soon"); break
                elif cmd == "/version": print(f"Version: {VERSION}")
                elif cmd == "/developer": print(f"Developer: {DEVELOPER}")
                elif cmd == "/about": print(ABOUT_TEXT)
                elif cmd == "/instructions": print(load_instructions() or "[No instructions yet]")
                elif cmd in ("/history", "/logs"):
                    if os.path.exists(HISTORY_FILE):
                        print(open(HISTORY_FILE).read())
                    else:
                        print("[No history yet]")
                else:
                    print("Unknown command. Type /help to see available commands.")
                continue

            # Memory instruction
            if user_input.lower().startswith("remember "):
                instruction = user_input[len("remember "):].strip()
                if instruction:
                    save_instruction(instruction)
                    system_messages.append({"role": "system", "content": instruction})
                    print("✓ Instruction remembered.")
                continue

            # AI Interaction
            messages = system_messages + [{"role": "user", "content": user_input}]
            response = ollama.chat(model="llama3.2:1b", messages=messages)['message']['content']

            # Replace AI name
            if "I'm an artificial intelligence model known as Llama" in response:
                response = "I'm an artificial intelligence model known as ZeeE AI. ZeeE AI stands for \"Zero Effort, Everything Enabled AI\". I'm developed by AzizHorea."

            print(">ZeeE AI:", response.strip())
            save_history(user_input, response.strip())

        except (KeyboardInterrupt, EOFError):
            print(f"\nGoodbye! {USERNAME} See you soon")
            break

if __name__ == "__main__":
    main()
 
