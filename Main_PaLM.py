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
embedding_models = [m for m in palm.list_models() if 'embedText' in m.supported_generation_methods]
embedding_model = embedding_models[0].name

class Memory:
    def __init__(self):
        self.prompts = set()
        self.questions = {}
        self.answers = {}
        self.context = []

    def update_prompt(self, t):
        self.prompts.add(t)
        self.context.extend([('', t)])

    def update_question(self, q, a):
        self.questions[q] = a
        self.context.extend([(q, a)])

def is_similar(text1, text2, threshold=0.5):
    embedding1 = palm.generate_embeddings(model=embedding_model, text=text1)['embedding']
    embedding2 = palm.generate_embeddings(model=embedding_model, text=text2)['embedding']
    similarity = np.dot(embedding1, embedding2)
    return similarity >= threshold

def generate_text(prompt):
    completion = palm.generate_text(model=model, prompt=prompt, temperature=0.8, max_output_tokens=500)
    return completion.result.strip() if completion.result else None

def generate_item(prompt, context):
    for _ in range(5):
        generated_text = generate_text(f"{prompt} {context}")
        if generated_text and is_similar(prompt, generated_text):
            return generated_text
    return None

def main():
    memory = Memory()
    while True:
        prompt = input("Enter your prompt or type 'exit' to quit: ")
        if prompt.lower() == 'exit': break
        memory.update_prompt(prompt)
        context = " ".join([a for _, a in memory.context[-5:]])
        num_iterations = int(input("Enter the number of iterations: "))
        for _ in range(num_iterations):
            question = generate_item(prompt, context)
            if question not in memory.questions:
                answer = generate_item(question, context)
                if answer: memory.update_question(question, answer)
        for q, a in memory.questions.items():
            print(f"Question: {q}\nAnswer: {a}\n")
    print("Goodbye!")

if __name__ == "__main__":
    main()