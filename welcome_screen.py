# welcome_screen.py
import os
import json
from saved_memory import select_memory

def welcome_prompt():
    print("Welcome to the AI Debugger Program!")

    print("\nSelect a memory directory:")
    memory_path = select_memory()

    settings_file = os.path.join(memory_path, "settings.json")
    settings = {}  # Initialize the settings variable as an empty dictionary
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as f:
            settings = json.load(f)
            print("\nCurrent saved settings:")
            for key, value in settings.items():
                print(f"- {key}: {value}")

        user_input = input("Would you like to maintain your current settings? (y/n): ")
        if user_input.lower() == 'y':
            return settings['api_key'], settings['num_prompts'], memory_path, settings['filter_context_threshold'], settings['archive_memory_threshold'], settings['filter_memory_threshold']

    print("\nAdjustable Variables:")
    print("- API Key: The key to access the generative AI API (cannot change).")
    print("- Memory: The number of prompts to remember.")
    print("- Filter Context Threshold: (Larger value = more random) Between 0 and 1. ")
    print("- Archive Memory Threshold: (Larger value = more random) Between 0 and 1. ")
    print("- Filter Memory Threshold: (Larger value = more random) Between 0 and 1. ")

    if os.path.exists("api_key.txt"):
        print("Saved API Key Accepted")
        with open("api_key.txt", "r") as f:
            api_key = f.read().strip()
    else:
        api_key = input("Enter your API key: ")
        save_api_key(api_key)

    num_prompts = get_user_input("Enter the number of prompts to remember (default: 1): ", default_value=settings.get('num_prompts', 1), is_int=True)
    filter_context_threshold = get_user_input("Enter the filter context threshold (default: 0.1): ", default_value=settings.get('filter_context_threshold', 0.1))
    archive_memory_threshold = get_user_input("Enter the archive memory threshold (default: 0.5): ", default_value=settings.get('archive_memory_threshold', 0.5))
    filter_memory_threshold = get_user_input("Enter the filter memory threshold (default: 0.5): ", default_value=settings.get('filter_memory_threshold', 0.5))

    settings = {
        'api_key': api_key,
        'num_prompts': num_prompts,
        'filter_context_threshold': filter_context_threshold,
        'archive_memory_threshold': archive_memory_threshold,
        'filter_memory_threshold': filter_memory_threshold
    }

    with open(settings_file, 'w') as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)

    return api_key, num_prompts, memory_path, filter_context_threshold, archive_memory_threshold, filter_memory_threshold

def get_user_input(prompt, default_value=None, is_int=False):
    while True:
        user_input = input(prompt)
        if user_input:
            try:
                value = float(user_input)
                return int(value) if is_int else value
            except ValueError:
                print("Invalid input. Please enter a valid number or press enter to use the default value.")
        elif default_value is not None:
            return default_value
        else:
            print("Invalid input. Please enter a valid number.")

def save_api_key(api_key):
    with open("api_key.txt", "w") as f:
        f.write(api_key)


if __name__ == "__main__":
    api_key, num_prompts, memory_path, filter_context_threshold, archive_memory_threshold, filter_memory_threshold = welcome_prompt()
    save_api_key(api_key)
    print("\nSettings saved. You may now run the 'main.py' file.")