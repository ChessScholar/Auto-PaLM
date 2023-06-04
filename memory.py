# memory.py
import os
import json
import re
import time
import numpy as np
import google.generativeai as palm

class Memory:
    def __init__(self):
        self.prompts = set()
        self.questions = {}
        self.answers = {}
        self.context = []

    def get_embedding(self, text):
        embedding_models = [m for m in palm.list_models() if 'embedText' in m.supported_generation_methods]
        embedding_model = embedding_models[0].name
        embedding = palm.generate_embeddings(model=embedding_model, text=text)['embedding']
        return (text, embedding)

    def update_prompt(self, t):
        self.prompts.add(t)
        _, t_embedding = self.get_embedding(t)
        self.context.append(("", t_embedding))

    def update_question(self, q, a):
        self.questions[q] = a
        self.answers[q] = a
        _, a_embedding = self.get_embedding(a)
        self.context.append((q, a_embedding))

    def filter_context(self, prompt_embedding, threshold=0.1):
        self.context = list(filter(lambda item: np.dot(item[1], prompt_embedding) >= threshold, self.context))
        return self.context

    def cosine_similarity(self, a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))