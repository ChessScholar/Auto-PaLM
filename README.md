Updated June 18, 2023

_Please note that I'm solo on this project at the moment and will always welcome help. I'm still learning programming language and jargon. Thank you for your understanding and patience!_

**# Changes, patch-2**
* Removed multi-file for now. Everything is condensed into one main.py file. I'm currently working on patch-3 already where all the logic is separated into different files (and some new toys).

- Memories:
	- Logic for creating new folders called "memories". Memories are saved as .json files "long_term". You can pick an old memory and continue working from there. 
	- Memories will save to file all tasks created, the output of the Chat mode, and identify and save code snippets (currently only Python snippets).

- Code snippets:
  - If a code snippet is successfully found, it will note in the terminal.
  - If code snippet is successfully found, it will attempt to run the snippet from the terminal. Error messages are ignored at hte moment (implementing error checks).
 
- Tasks and Subtasks:
	- Chat model creates a task list based on the user's prompt. Currently only able to take an initial prompt and create Tasks for it. If a task is too vauge, it will create subtasks. The tasks are sent to the Text model with some context. The Text model will answer and give back to the Chat model. The Chat model will move on to the next task.

 - Normal work:
   - I'm specializing the Chat to work on auto-coding. But it is capable of doing other tasks as well. Have fun with it and let me know if you have suggestions or ideas to improve!


# Auto-PaLM

Auto-PaLM is a Python-based AI program created with the help of GPT-4 and other LLMs. This was started from scratch. The program stores and manages the generated content in a memory system, allowing for context-aware responses and the ability to filter, archive, and retrieve information based on user input.

## Features

- Generate questions and answers based on user-defined prompts
- Store and manage generated content in a memory system
- Filter and archive memory based on user-defined thresholds
- Save and load memory settings for easy retrieval and customization
- Detect and save code snippets from generated content

## Usage

1. Install the required dependencies:
```
pip install -r requirements.txt
```

2. Run the `main.py` script to start the Auto-PaLM program:
```
python main.py
```

3. Follow the on-screen prompts to set goals, enter prompts, and generate questions and answers.

## Functions

- `set_clear_goals()`: Allows users to define goals for the AI system.
- `generate_text(prompt)`: Generates text based on the given prompt.
- `process_answer(question, answer, memory)`: Processes the answer, detects code snippets, and updates the memory.
- `filter_memory(memory, prompt_embedding, threshold)`: Filters the memory based on the relevancy of the given prompt.

## User Input

Users can interact with the program by entering the following commands:

- Enter a prompt: Users can input a prompt for the AI to generate questions and answers based on the prompt.
- `exit`: Exits the program.
- `clear memory`: Clears the memory of the program.
- Enter the number of iterations: Users can input the number of iterations for generating questions and answers. Default is 1.

## Memory Settings

- `num_prompts`: The number of prompts to remember.
- `filter_context_threshold`: The threshold for filtering context based on relevancy (between 0 and 1).
- `archive_memory_threshold`: The threshold for archiving memory (between 0 and 1).
- `filter_memory_threshold`: The threshold for filtering memory based on relevancy (between 0 and 1).

## Contributing

I welcome contributions to improve the Auto-PaLM program. Please feel free to submit suggestions and issues to discuss potential improvements or report bugs, and even help me understand terms and the correct process of open-source projects. 🙂

## License

MIT License

Copyright (c) 2023 ChessScholar

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## A Special Thank You

This project, Auto-PaLM, was greatly inspired by [Auto-GPT: An Autonomous GPT-4 Experiment](https://github.com/Significant-Gravitas/Auto-GPT) by Significant Gravitas. Auto-GPT showcased the capabilities of the GPT-4 language model and served as one of the first examples of an autonomous AI application. I deeply appreciate the work and innovation demonstrated by Auto-GPT and its contributors, as it has truly been a driving force and motivation for the development of Auto-PaLM.

I'm so excited to see how both Auto-PaLM and Auto-GPT will continue to push the boundaries of what is possible with AI in the future!
