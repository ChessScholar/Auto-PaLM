import os
import json
import re
import subprocess
from dotenv import load_dotenv
import google.generativeai as palm

load_dotenv()
palm.configure(api_key=os.environ['API_KEY'])

class MemSys:
    def __init__(self, mem_name="default"):
        self.mem_name = mem_name
        self.mem_fldr = os.path.join("memories", mem_name)
        self.json_fldr = os.path.join(self.mem_fldr, "json_files")
        self.mem_file = os.path.join(self.json_fldr, "long_term.json")
        self.mem = {"initial_prompt": "", "tasks": [], "subts": [], "code_snips": []}
        self.load_mem()

    def create_mem(self, mem_name):
        self.mem_name = mem_name
        self.mem_fldr = os.path.join("memories", mem_name)
        self.json_fldr = os.path.join(self.mem_fldr, "json_files")
        self.mem_file = os.path.join(self.json_fldr, "long_term.json")

        if not os.path.exists(self.mem_fldr):
            os.makedirs(self.mem_fldr)
            os.makedirs(self.json_fldr)

        self.save_mem()

    def load_mem(self):
        if os.path.exists(self.mem_file):
            with open(self.mem_file, "r") as f:
                self.mem = json.load(f)

    def save_mem(self):
        with open(self.mem_file, "w") as f:
            json.dump(self.mem, f, indent=2)

    def upd_mem(self, key, value):
        self.mem[key] = value
        self.save_mem()

    def select_mem(self):
        memories = [d for d in os.listdir("memories") if os.path.isdir(os.path.join("memories", d))]
        print("Available memories:")
        for i, mem in enumerate(memories):
            print(f"{i + 1}. {mem}")

        print(f"{len(memories) + 1}. Create a new mememory")
        choice = int(input("Select a memory or create a new one: ")) - 1

        if choice < len(memories):
            mem_name = memories[choice]
        else:
            mem_name = input("Enter a name for the new mem: ")

        return mem_name

class TaskGenerator:
    def gen_ts(self, main_task):
        prompt = f"What are the main steps in creating a {main_task}?"
        tasks = palm.generate_text(prompt=prompt, temperature=0.0, max_output_tokens=800).result.split("\n")
        return tasks

    def gen_subts(self, task):
        prompt = f"What are the main steps in completing the task: '{task}'?"
        subts = palm.generate_text(prompt=prompt, temperature=0.0, max_output_tokens=800).result.split("\n")
        return subts

class CodeExecution:
    def test_code_snip(self, code_snip, language, timeout=7):
        try:
            if language == "python":
                result = subprocess.run(["python", "-c", code_snip], capture_output=True, text=True, check=True, timeout=timeout)
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
        content = palm.chat(messages=messages, temperature=0.6, candidate_count=3, top_p=0.9).last
        return content

    def extract_code_snip(content):
        code_snip = re.search(r'```python(.+?)```', content, re.DOTALL)
        if code_snip:
            code_snip = code_snip.group(1).strip()
            return code_snip
        return None

def main():
    initial_prompt = "Create the game 'pong' using the programming language: Python."
    task_gen = TaskGenerator()
    mem_sys = MemSys()
    mem_name = mem_sys.select_mem()

    if not os.path.exists(mem_sys.mem_file):
        mem_sys.create_mem(mem_name)
        
    mem_sys.upd_mem("initial_prompt", initial_prompt)

    tasks = task_gen.gen_ts(initial_prompt)
    mem_sys.upd_mem("tasks", tasks)

    for i, task in enumerate(tasks):
        if not task.strip():
            continue
        print(f"Task {i + 1}: {task}")

        subts = task_gen.gen_subts(task)
        mem_sys.upd_mem(f"subts_{i + 1}", subts)

        for j, subt in enumerate(subts):
            if not subt.strip():
                continue
            print(f"  Subtask {i + 1}.{j + 1}: {subt}")

            content = CodeExecution.process_task(subt)

            if content is None:
                print("Error: Chat model returned None")
                continue

            print(f"[Chat Model] {content}")

            code_snip = CodeExecution.extract_code_snip(content)

            if code_snip:
                print(f"\nExtracted code snip:\n{code_snip}\n")
                test_status, test_message = CodeExecution().test_code_snip(code_snip, "python")
                if test_status:
                    print(f"\nTask completed successfully:\n")
                    print(code_snip)
                else:
                    print(f"\nError occurred while testing the code snip:\n{test_message}\n")

                mem_sys.upd_mem(f"code_snip_{i + 1}_{j + 1}", code_snip)

if __name__ == "__main__":
    main()



# subt = subtask
# fldr = folder
# mem = memory
# mem_sys = memory system
# upd = update
# snip = snippet
# gen = generate
# ts = task
# gen_ts = generate tasks
# gen_subts = generate subtasks
# mem_name = memory name
# mem_fldr = memory folder
# json_fldr = json folder
# mem_file = memory file
