Updated June 5, 2023

Please note that I'm solo on this project at the moment and will always welcome help. I'm still learning programming language and jargon. Thank you for your understanding and patience!

Current tasks:
- Correctly switching to google.generativeai functions instead of the mock-up functions provided by GPT-4 in its baby stages.

- Refactoring all files to be easier to understand what each function does, and new files to shorten some of the larger ones.

- Allowing users to choose between API outputs (text or chat) at start-up.

- Making examples of how to use the program. 

- Not rewriting all of readme.md on my phone, but when I have time at home 😅.




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

I welcome contributions to improve the Auto-PaLM program. Please feel free to submit pull requests or open issues to discuss potential improvements or report bugs.

## License

(no clue?!) if anyone has experience with this, please help! I want this to be openly accessable to everyone to copy, modify, edit, etc.

## A Special Thank You

This project, Auto-PaLM, was greatly inspired by [Auto-GPT: An Autonomous GPT-4 Experiment](https://github.com/Significant-Gravitas/Auto-GPT) by Significant Gravitas. Auto-GPT showcased the capabilities of the GPT-4 language model and served as one of the first examples of an autonomous AI application. I deeply appreciate the work and innovation demonstrated by Auto-GPT and its contributors, as it has truly been a driving force and motivation for the development of Auto-PaLM.

I'm so excited to see how both Auto-PaLM and Auto-GPT will continue to push the boundaries of what is possible with AI in the future!
