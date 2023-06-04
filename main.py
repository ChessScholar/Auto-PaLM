# main.py
import os
import logging
import json
import re
import time
import numpy as np
import google.generativeai as palm
from concurrent.futures import ThreadPoolExecutor
from goal_setting import set_clear_goals
from memory import Memory
from saved_memory import (save_memory, load_memory, archive_memory,
                          detect_code_snippet, save_snippets_to_file, filter_memory)
from welcome_screen import welcome_prompt, save_api_key

def load_api_key():
    with open("api_key.txt", "r") as f:
        return f.read().strip()

api_key, num_prompts, memory_path, filter_context_threshold, archive_memory_threshold, filter_memory_threshold = welcome_prompt()
save_api_key(api_key)
palm.configure(api_key=load_api_key())

# Load the memory from the .json file
memory = load_memory(memory_path)

# Get the embedding of the current prompt
prompt = "Enter your current prompt here"
_, prompt_embedding = memory.get_embedding(prompt)

# Filter the memory based on relevancy
filtered_memory = filter_memory(memory, prompt_embedding, threshold=filter_memory_threshold)

# Save the filtered memory back to the .json file
save_memory(filtered_memory, memory_path)
models = [m for m in palm.list_models() if 'generateText' in m.supported_generation_methods]
model = models[0].name

max_iterations_per_minute = 30
iteration_count = 0
start_time = time.time()

def generate_text(prompt):
    global iteration_count, start_time
    iteration_count += 1
    if iteration_count > max_iterations_per_minute:
        elapsed_time = time.time() - start_time
        if elapsed_time < 60:
            print("You have reached the 30 prompts/iterations per minute quota. The AI is waiting for the timer.")
            time.sleep(60 - elapsed_time)
        start_time = time.time()
        iteration_count = 1

    completion = palm.generate_text(model=model, prompt=prompt,
                                    temperature=0.5, max_output_tokens=1000)
    return completion.result.strip() if completion.result else None

def process_answer(question, answer, memory):
    snippets = detect_code_snippet(answer)
    if snippets:
        save_snippets_to_file(snippets, memory_path)
    memory.update_question(question, answer)

def AI():
    goals = set_clear_goals()
    print("\nGoals set:")
    for goal in goals:
        print(f"- {goal}")

    # Load the memory from the .json file
    memory = load_memory(memory_path)

    prev_prompt = None
    while True:
        prompt = input("Enter your prompt or type 'exit' to quit: ")
        if prompt.lower() == 'exit':
            break
        elif prompt.lower() == 'clear memory':
            memory = Memory()
            save_memory(memory, memory_path)
            print("Memory cleared.")
            continue

        if not prompt.strip():
            if prev_prompt:
                prompt = prev_prompt
                print(f"Using previous prompt: {prompt}")
            else:
                print("Please enter a valid prompt.")
                continue
        else:
            prev_prompt = prompt

        # vital: Updating memory with the new prompt
        memory.update_prompt(prompt)
        _, prompt_embedding = memory.get_embedding(prompt)

        filtered_context = memory.filter_context(prompt_embedding, threshold=filter_context_threshold)
        archive_memory(memory_path, threshold=archive_memory_threshold)
        save_memory(memory, memory_path, num_prompts=num_prompts)

        try:
            num_iterations = int(input("Enter the number of iterations: "))
        except ValueError:
            print("Using default (1) iteration.")
            num_iterations = 1

        for _ in range(num_iterations):
            question = generate_text(f"What is a question about {prompt}?")
            if question not in memory.questions:
                answer = generate_text(question)
                if answer:
                    process_answer(question, answer, memory)
                    # Print the generated question and answer for each iteration
                    print(f"\nIteration {_+1}:")
                    print(f"Question: {question}\nAnswer: {answer}\n")

        for q, a in memory.questions.items():
            print(f"Question: {q}\nAnswer: {a}\n")

    print("Goodbye!")


if __name__ == "__main__":
    AI()