# Privacy Notice

We know that privacy is important to you, and it's important to us too. We want to be transparent about how we handle your data and what we do to protect it.

## How we handle your data
We **never store** code permanently. Every `/pilot` command is run in the following way:

1. We check out your code in an **isolated** Docker container
2. PR Pilot  uses GPT-4 to understand your command 
3. It reads/writes the necessary files 
4. The container is deleted

## Using LLMs to understand your code
PR Pilot uses a large language model (LLM) to understand your code and execute your commands. We use GPT-4, which is a state-of-the-art LLM developed by OpenAI. We use GPT-4 to understand your commands and execute them in an isolated environment.
Please refer to OpenAI's [privacy policy](https://openai.com/policies/privacy-policy) for more information on how they handle your data.