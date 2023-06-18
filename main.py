import os
import json
import re
import subprocess
from dotenv import load_dotenv
import google.generativeai as palm

load_dotenv()
palm.configure(api_key=os.environ['API_KEY'])

class SystemMemory:
    def __init__(self, memory_name="default"):
        self.memory_name = memory_name
        self.memory_folder = os.path.join("memories", memory_name)
        self.json_folder = os.path.join(self.memory_folder, "json_files")
        self.memory_file = os.path.join(self.json_folder, "long_term.json")
        self.memory = {"initial_prompt": "", "tasks": [], "subtasks": [], "code_snippets": [], "summary": ""}

    def load_or_create_memory(self, memory_name):
        self.memory_name = memory_name
        self.memory_folder = os.path.join("memories", memory_name)
        self.json_folder = os.path.join(self.memory_folder, "json_files")
        self.memory_file = os.path.join(self.json_folder, "long_term.json")

        if not os.path.exists(self.memory_folder):
            os.makedirs(self.memory_folder)
            os.makedirs(self.json_folder)
            
        # Load existing memory if available
        if os.path.exists(self.memory_file):
            with open(self.memory_file, "r") as f:
                self.memory = json.load(f)
        else:
            self.save_memory()

    def append_to_memory(self, key, value, task_num=None, subtask_num=None):
        if task_num is not None and subtask_num is not None:
            item = {"task_number": task_num, "subtask_number": subtask_num, "main_task": value, "completed": False}
        elif task_num is not None:
            item = {"task_number": task_num, "main_task": value, "completed": False}
        else:
            item = {"main_task": value, "completed": False}

        if key not in self.memory:
            self.memory[key] = []

        self.memory[key].append(item)
        self.save_memory()

    def append_code_snippet(self, key, value, task_num=None, subtasks_num=None):
        if task_num is not None and subtasks_num is not None:
            key += f"_{task_num}_{subtasks_num}"
        elif task_num is not None:
            key += f"_{task_num}"
        value_with_num = {"number": task_num if subtasks_num is None else (task_num, subtasks_num), "main_task": value}
        if key in self.memory:
            self.memory[key].append(value_with_num)
        else:
            self.memory[key] = [value_with_num]
        self.save_memory()

    def mark_completed(self, key, task_num=None, subtask_num=None):
        for item in self.memory[key]:
            if task_num is not None and subtask_num is not None and "task_number" in item and "subtask_number" in item:
               if item["task_number"] == task_num and item["subtask_number"] == subtask_num:
                    item["completed"] = True
                    break
            elif task_num is not None and "task_number" in item:
                if item["task_number"] == task_num:
                    item["completed"] = True
                    break
        self.save_memory()
        
    def save_memory(self):
        with open(self.memory_file, "w") as f:
            json.dump(self.memory, f, indent=2)

    def update_memory(self, key, value):
        self.memory[key] = value
        self.save_memory()

    def summarize_conversation(self):
        summary = f"User prompt: {self.memory['initial_prompt']}\n"
        summary += "Conversation summary:\n"
        task_counter = 1
        for task in self.memory["tasks"]:
            subtasks_text = ""
            for subtask in self.memory["subtasks"]:
                if subtask["task_number"] == task["task_number"]:
                    completed_text = " (completed)" if subtask["completed"] else ""
                    subtasks_text += f"- Subtask {subtask['subtask_number']}: {subtask['main_task']}{completed_text}\n"
            completed_text = " (completed)" if task["completed"] else ""
            summary += f"Task {task_counter}: {task['main_task']}{completed_text}\n{subtasks_text}\n"
            task_counter += 1
        return summary

    def select_memory(self):
        memories = [d for d in os.listdir("memories") if os.path.isdir(os.path.join("memories", d))]
        print("Available memories:")
        for i, memory in enumerate(memories):
            print(f"{i + 1}. {memory}")

        print(f"{len(memories) + 1}. Create a new mememory")
        choice = int(input("Select a memory or create a new one: ")) - 1

        if choice < len(memories):
            memory_name = memories[choice]
        else:
            memory_name = input("Enter a name for the new memory: ")

        return memory_name

class TaskGenerator:
    def generate_task(self, main_task):
        prompt = f"What are the main steps in creating a {main_task}?"
        tasks = palm.generate_text(prompt=prompt, temperature=0.0, max_output_tokens=800).result.split("\n")
        return tasks

    def generate_subtasks(self, task):
        prompt = f"What are the main steps in completing the task: '{task}'?"
        subtasks = palm.generate_text(prompt=prompt, temperature=0.0, max_output_tokens=800).result.split("\n")
        return subtasks

class CodeExecution:
    def test_code_snippet(self, code_snippet, language, timeout=7):
        try:
            if language == "python":
                result = subprocess.run(["python", "-c", code_snippet], capture_output=True, text=True, check=True, timeout=timeout)
                return True, result.stdout
            else:
                return False, "Unknown language."
        except subprocess.CalledProcessError as e:
            return False, e.stderr
        except subprocess.TimeoutExpired:
            return False, "Code execution timed out."
        except Exception as e:
            return False, str(e)

    def process_task(task):
        messages = [{"content": task}]
        content  = palm.chat(messages=messages, temperature=0.6, candidate_count=3, top_p=0.9).last
        return content
        
    def extract_code_snippet(content):
        code_snippet = re.search(r'```python(.+?)```', content, re.DOTALL)
        if code_snippet:
            code_snippet = code_snippet.group(1).strip()
            return code_snippet
        return None

def main():
    initial_prompt = "Create the game 'pong' using the programming language: Python."
    task_generator = TaskGenerator()
    system_memory = SystemMemory()
    memory_name = system_memory.select_memory()

    system_memory.load_or_create_memory(memory_name)
    system_memory.update_memory("initial_prompt", initial_prompt)

    tasks = task_generator.generate_task(initial_prompt)
    tasks = [task.strip() for task in tasks if task.strip() and re.match(r'^\d\.', task)]
    task_summary = ""

    # Print the full task list generated by the Chat model
    print("Full task list:")
    filtered_tasks = [task for task in tasks if task.strip() and not task.startswith("Task")]
    for i, task in enumerate(filtered_tasks):
        print(f"Task {i + 1}: {task}")
        system_memory.append_to_memory("tasks", task, task_num=i + 1)

    # Reload memory after tasks have been appended
    with open(system_memory.memory_file, "r") as f:
        system_memory.memory = json.load(f)

    saved_tasks = system_memory.memory["tasks"]

    for i, task_dict in enumerate(saved_tasks):
        task = task_dict.get("main_task")

        print(f"\nTask {i + 1}: {task}")

        if i > 0:
            system_memory.mark_completed("tasks", task_num=i)
            task_summary += f"Task {i} '{task}' was completed.\n"

        system_memory.memory[f"subtasks_{i + 1}"] = []

        subtasks = task_generator.generate_subtasks(task)
        subtasks = [subtask.strip() for subtask in subtasks if subtask.strip() and re.match(r'^\d\.', subtask)]

        for j, subtask in enumerate(subtasks):
            if not subtask.strip():
                continue

            system_memory.append_to_memory("subtasks", subtask, task_num=i + 1, subtask_num=j + 1)

            # Add the following lines to print the subtasks:
            print(f"  Subtask {i + 1}.{j + 1}: {subtask}")

        # Reload memory after subtasks have been appended
        with open(system_memory.memory_file, "r") as f:
            system_memory.memory = json.load(f)

            content = CodeExecution.process_task(subtask)

            if content is None:
                print("Error: Chat model returned None")
                continue

            print(f"[Chat Model] {content}")

            code_snippet = CodeExecution.extract_code_snippet(content)

            if code_snippet:
                print(f"\nExtracted code snippet:\n{code_snippet}\n")
                test_status, test_message = CodeExecution().test_code_snippet(code_snippet, "python")
                if test_status:
                    print(f"\nTask completed successfully:\n")
                    system_memory.mark_completed("subtasks", task_num=i + 1, subtask_num=j + 1)

                    # Add the completed task's summary here:
                    task_summary += f"  Subtask {i + 1}.{j + 1} '{subtask}' was completed.\n"
                else:
                    print(f"\nError occurred while testing the code snippet:\n{test_message}\n")
                    task_summary += f"  Subtask {i + 1}.{j + 1} '{subtask}' encountered an error: {test_message}\n"
                system_memory.append_code_snippet("code_snippets", code_snippet, task_num=i + 1, subtasks_num=j + 1)  # Change 'subtask_num' to 'subtasks_num'
                
    system_memory.update_memory("task_summary", task_summary)

    saved_summary = system_memory.memory["task_summary"]

    prompt = f"Based on the previous progress:\n{saved_summary}\nWhat should be the next step in completing the remaining subtasks?"
    next_step = palm.generate_text(prompt=prompt, temperature=0.0, max_output_tokens=800).result

    print(f"Next step: {next_step}")
    print("Summary of completed tasks and subtasks:")
    print(saved_summary)
    summary = system_memory.summarize_conversation()
    system_memory.update_memory("summary", summary)

    print("Summary of the conversation:")
    print(summary)

if __name__ == "__main__":
    main()