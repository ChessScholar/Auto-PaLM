import logging
import google.generativeai as palm
import numpy as np
import random
import json
import os
import re
import time

palm.configure(api_key='Your_PaLM_API_KEY')

models = [m for m in palm.list_models() if 'generateText' in m.supported_generation_methods]
model = models[0].name
print(model)

embedding_models = [m for m in palm.list_models() if 'embedText' in m.supported_generation_methods]
embedding_model = embedding_models[0].name
print(embedding_model)

class Memory:
    def __init__(self):
        self.questions = set()
        self.answers = {}
        self.facts = set()
        self.user_prompts = []

    def add_user_prompt(self, user_prompt):
        self.user_prompts.append(user_prompt)

    def add_question(self, question, answer):
        self.questions.add(question)
        self.answers[question] = answer

    def add_fact(self, fact):
        self.facts.add(fact)

    def get_fact_prompt(self, prompt, max_length=300):
        facts = " ".join(self.facts)[:max_length].strip()
        return f"{prompt} {facts}".strip()

def is_similar(text1, text2, threshold=0.5):
    embedding1 = palm.generate_embeddings(model=embedding_model, text=text1)['embedding']
    embedding2 = palm.generate_embeddings(model=embedding_model, text=text2)['embedding']

    similarity = np.dot(embedding1, embedding2)
    return similarity >= threshold

def save_code(code, language, memory_path):
    extension_mapping = {
        'python': '.py'
        # Add other languages and their file extensions here
    }

    code_subdirectory = os.path.join(memory_path, "code")
    if not os.path.exists(code_subdirectory):
        os.makedirs(code_subdirectory)

    file_name = f"generated_code_{language.lower()}_{int(time.time())}{extension_mapping[language.lower()]}"
    file_path = os.path.join(code_subdirectory, file_name)

    with open(file_path, 'w') as code_file:
        code_file.write(code)

def generate_text(prompt, max_output_tokens=1000, memory_path=None):
    completion = palm.generate_text(model=model, prompt=prompt, temperature=0.8, max_output_tokens=max_output_tokens)
    result = completion.result
    if result:
        result = result.strip()

        # Detect Python code with a regular expression
        python_code_re = re.compile(r'\s*```\s*python\s*\n(.*?)\s*```', re.DOTALL)
        python_code_match = python_code_re.search(result)

        if python_code_match:
            python_code = python_code_match.group(1)
            if memory_path:
                save_code(python_code, 'python', memory_path)
            else:
                print("Warning: memory_path not provided, code not saved")
            print("Python code saved successfully.")
            # Remove the code block from the result to display the remaining text
            result = python_code_re.sub('', result).strip()


    return result if result else None

def generate_question(initial_prompt, memory_path):
    prompt = f"Ask questions relating to the prompt: _____ {initial_prompt}"
    attempts = 0
    max_attempts = 5

    while attempts < max_attempts:
        attempts += 1
        generated_text = generate_text(prompt, memory_path=memory_path)

        if generated_text:
            # Remove the placeholder word '_____' and any excess spaces
            complete_question = generated_text.replace('_____', '').strip()

            if is_similar(initial_prompt, complete_question):
                return complete_question
        else:
            continue

    return None

def generate_answer(question, memory_path):
    attempts = 0
    max_attempts = 5

    while attempts < max_attempts:
        attempts += 1
        generated_text = generate_text(question, memory_path=memory_path)

        if generated_text:
            generated_answer = generated_text.strip()

            if is_similar(question, generated_answer):
                return generated_answer
        else:
            continue

    return None

def save_memory(memory, memory_path):
    file_name = os.path.join(memory_path, "memory.json")
    with open(file_name, 'w') as f:
        json.dump({
            'questions': list(memory.questions),
            'answers': memory.answers,
            'facts': list(memory.facts),
            'user_prompts': memory.user_prompts,
        }, f, indent=4, ensure_ascii=False)

def load_memory(memory_path):
    memory_file = os.path.join(memory_path, "memory.json")
    try:
        with open(memory_file, 'r') as f:
            data = json.load(f)
            memory_obj = Memory()
            memory_obj.questions = set(data['questions'])
            memory_obj.answers = data['answers']
            memory_obj.facts = set(data['facts'])

            try:
                memory_obj.user_prompts = data['user_prompts']
            except KeyError:
                # If the 'user_prompts' key is not found, create a new JSON file
                memory_obj.user_prompts = []
                save_memory(memory_obj, memory_path)

            return memory_obj
    except FileNotFoundError:
        return Memory()


def select_memory():
    json_directory = "json_list"
    if not os.path.exists(json_directory):
        os.makedirs(json_directory)

    memory_directories = []
    print("Available memory directories:")
    for directory in os.listdir(json_directory):
        full_path = os.path.join(json_directory, directory)
        if os.path.isdir(full_path):
            memory_directories.append(directory)
            print(f"{len(memory_directories)}: {directory}")

    while True:
        user_input = input("Input memory directory number, or type 'new' to create a new one: ")
        if user_input.isdigit() and 0 < int(user_input) <= len(memory_directories):
            return os.path.join(json_directory, memory_directories[int(user_input) - 1])
        elif user_input.lower() == 'new':
            new_memory_name = input("Enter a name for the new memory directory: ")
            new_memory_path = os.path.join(json_directory, new_memory_name)
            os.makedirs(new_memory_path)
            return new_memory_path
        else:
            print("Invalid input. Please try again.")

class Conversation:
    def __init__(self):
        self.context = []

    def update_context(self, user_message, response):
        self.context.append((user_message, response))

    def get_context(self, max_length=300):
        context_list = []
        for user_message, response in self.context[-5:]:
            context_list.append(user_message.strip())
            context_list.append(response.strip())
        return " ".join(context_list)[:max_length].strip()

def main():
    memory_path = select_memory()
    memory = load_memory(memory_path)

    conversation = Conversation()  # Create a Conversation object

    while True:
        initial_prompt = input("Enter your initial prompt or type 'exit' to quit: ")

        if initial_prompt.lower() == 'exit':
            break

        memory.add_user_prompt(initial_prompt)

        # Incorporate conversation context for generating questions and answers
        question_context = f"{initial_prompt} {conversation.get_context()}"
        num_iterations = int(input("Enter the number of iterations: "))

        for _ in range(num_iterations):
            question = generate_question(question_context, memory_path)
            if question and question not in memory.questions:
                answer_context = f"{question} {conversation.get_context()}"
                answer = generate_answer(answer_context, memory_path)
                if answer:
                    memory.add_question(question, answer)
                    memory.add_fact(answer)
                    print(f"Question: {question}\nAnswer: {answer}")
                    conversation.update_context(question, answer)
                else:
                    print("Could not generate answer.")
            else:
                print("Could not generate question.")

        save_memory(memory, memory_path)
    
    print("Goodbye!")


if __name__ == "__main__":
    main()