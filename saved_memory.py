import os
import json
import re
import time
from memory import Memory
import numpy as np

def detect_code_snippet(api_output):
    code_start_regex = re.compile(r'```\w+\s')
    # Updated regex pattern for code_end
    code_end_regex = re.compile(r'\s```(?!\S)')
    
    code_snippets = []

    code_starts = code_start_regex.finditer(api_output)
    code_ends = code_end_regex.finditer(api_output)

    for match_start, match_end in zip(code_starts, code_ends):
        start = match_start.end()
        end = match_end.start()
        snippet = api_output[start:end].strip()
        code_snippets.append(snippet)

    return code_snippets

def save_snippets_to_file(snippets, memory_path):
    codes_directory = os.path.join(memory_path, "codes")
    if not os.path.exists(codes_directory):
        os.makedirs(codes_directory)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    
    for i, snippet in enumerate(snippets, start=1):
        code_file = f"code_{timestamp}_{i}.txt"
        code_file_path = os.path.join(codes_directory, code_file)
        
        with open(code_file_path, "w") as f:
            f.write(snippet)

def save_memory(memory, memory_path, num_prompts=1, max_answers=5):
    file_name = os.path.join(memory_path, "memory.json")
    last_prompt = list(memory.prompts)[-num_prompts:]
    last_update = time.strftime("%Y-%m-%d %H:%M:%S")
    summary = []

    if memory.questions:
        last_set_questions = list(memory.questions.keys())[-1:]
        summary = [memory.questions[q] for q in last_set_questions]
        last_answers = list(memory.answers.values())[-max_answers:]
        summary.extend(last_answers)
        summary = ' '.join(summary)

    with open(file_name, 'w') as f:
        json.dump({
            'last_update': last_update,
            'last_prompt': last_prompt,
            'prompts': list(memory.prompts),
            'questions': list(memory.questions.keys()),
            'answers': memory.answers,
            'summary': summary,
            'context': [(q[0], q[1].tolist() if isinstance(q[1], np.ndarray) else q[1]) for q in memory.context],
        }, f, indent=4, ensure_ascii=False)

def load_memory(memory_path):
    memory_file = os.path.join(memory_path, "memory.json")
    if os.path.exists(memory_file):
        with open(memory_file, 'r') as f:
            memory_obj = Memory()
            try:
                data = json.load(f)
            except json.decoder.JSONDecodeError:
                print("Error loading memory file. Creating a new memory object.")
                return memory_obj

            for prompt in data.get('prompts', []):
                memory_obj.prompts.add(prompt)

            memory_obj.questions = {q: a for q, a in zip(data['questions'], data['answers'].values())}
            memory_obj.answers = {q: a for q, a in zip(data['questions'], data['answers'].values())}

            memory_obj.context = [(q, np.array(a)) for q, a in data.get('context', [])]

            return memory_obj

    return Memory()

def archive_memory(memory_path, threshold=0.5):
    archive_path = os.path.join(memory_path, "archive")
    if not os.path.exists(archive_path):
        os.makedirs(archive_path)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    archive_file_name = f"archive_{timestamp}.json"
    archive_file_path = os.path.join(archive_path, archive_file_name)

    memory_file = os.path.join(memory_path, "memory.json")
    if os.path.exists(memory_file):
        os.rename(memory_file, archive_file_path)

def select_memory():
    json_directory = "json"
    if not os.path.exists(json_directory):
        os.makedirs(json_directory)

    memory_directories = [os.path.join(json_directory, d) for d in os.listdir(json_directory) if os.path.isdir(os.path.join(json_directory, d))]
    print("Available memory directories:")
    for i, directory in enumerate(memory_directories, start=1):
        print(f"{i}: {directory}")

    while True:
        user_input = input("Input memory directory number, or type 'new' to create a new one: ")
        if user_input.isdigit() and 0 < int(user_input) <= len(memory_directories):
            return memory_directories[int(user_input) - 1]
        elif user_input.lower() == 'new':
            new_memory_name = input("Enter a name for the new memory directory: ")
            new_memory_path = os.path.join(json_directory, new_memory_name)
            os.makedirs(new_memory_path)
            return new_memory_path
        else:
            print("Invalid input. Please try again.")
            
def filter_memory(memory, prompt_embedding, threshold=0.5):
    filtered_memory = Memory()

    for question, answer_embedding in memory.context:
        if question and np.dot(answer_embedding, prompt_embedding) >= threshold:
            filtered_memory.update_question(question, memory.answers[question])

    return filtered_memory