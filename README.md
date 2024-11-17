⚠️ This repository is deprecated and will be archived. All prompts moved to: https://github.com/xvnpw/fabric-agent-action

# AI Threat Modeling

[![Python package](https://github.com/xvnpw/ai-threat-modeling/actions/workflows/build.yaml/badge.svg)](https://github.com/xvnpw/ai-threat-modeling/actions/workflows/build.yaml)

🤖 You can use this scripts to generate AI featured content for threat modeling and security review.

> ⚠️ This is experimental project

## Installation

```bash
git clone git@github.com:xvnpw/ai-threat-modeling.git
cd ai-threat-modeling
pip install -r requirements.txt
```

## Configuration

Use environment variables to set API keys. Without API keys you **cannot** use selected provider:

```
# OpenAI API key
# Optional. Only if want to use openai provider
# Get a key from https://platform.openai.com/account/api-keys
OPENAI_API_KEY

# Open Router API key
# Optional. Only if want to use openrouter provider
# Get a key from https://openrouter.ai/keys
OPENROUTER_API_KEY
```

## Usage

```bash
$ python ai-tm.py --help
usage: ai-tm.py [-h] [--provider {openai,openrouter}] [--inputs [INPUTS]] [--output [OUTPUT]] [-ai [ARCHITECTURE_INPUTS]] [-atmi [ARCHITECTURE_THREAT_MODEL_INPUT]] [--model MODEL]
                [--temperature TEMPERATURE] [-v VERBOSE] [-d DEBUG] [-usos USER_STORY_OUTPUT_SUFFIX] [-t TEMPLATE_DIR] [--review REVIEW] [--create-draft CREATE_DRAFT]
                {project,architecture,user-story}

AI featured threat modeling and security review

positional arguments:
  {project,architecture,user-story}
                        type of feature

options:
  -h, --help            show this help message and exit
  --provider {openai,openrouter}
                        provider of LLM API, default: openai
  --inputs [INPUTS]     file path or json array of paths to input files (depends on feature)
  --output [OUTPUT]     path to output file
  -ai [ARCHITECTURE_INPUTS], --architecture-inputs [ARCHITECTURE_INPUTS]
                        for user-story only: json array of paths to architecture files
  -atmi [ARCHITECTURE_THREAT_MODEL_INPUT], --architecture-threat-model-input [ARCHITECTURE_THREAT_MODEL_INPUT]
                        for user-story only: path to architecture threat model file
  --model MODEL         type of ChatGPT model, default: gpt-4
  --temperature TEMPERATURE
                        sampling temperature for a model, default 0.2
  -v, --verbose         turn on verbose messages, default: false
  -d, --debug           turn on debug messages, default: false
  -usos USER_STORY_OUTPUT_SUFFIX, --user-story-output-suffix USER_STORY_OUTPUT_SUFFIX
                        for user-story only: suffix that will be added to input file name to create output file, default: _SECURITY
  -t TEMPLATE_DIR, --template-dir TEMPLATE_DIR
                        path to template dir, default: ./templates
  --review              review input files using LLM, default: false
  --create-draft        create draft of input (e.g. architecture) based on files (e.g. README.md,controllers.go,swagger.yaml), default: false

Experimental. Use on your own risk
```

## Features

### Review Architecture Description for Project

```bash
$ python ai-tm.py architecture --review --inputs <path_to_project>/ARCHITECTURE.md --output ARCHITECTURE_REVIEW.md --verbose
INFO:root:review of architecture started...
INFO:root:finished waiting on llm response
INFO:root:response written to file
```

## 🚀 Tech Stack

- Python
- LLM Tooling: [Langchain](https://github.com/hwchase17/langchain)
- LLM: [OpenAI GPT](https://openai.com/), [OpenRouter](https://openrouter.ai/)

## Privacy

### OpenAI

This project uses OpenAI API. By default your data will not be used for learning, as per [API data usage policies](https://openai.com/policies/api-data-usage-policies):
> OpenAI will not use data submitted by customers via our API to train or improve our models, unless you explicitly decide to share your data with us for this purpose. You can opt-in to share data.

### OpenRouter

OpenRouter describe privacy and filtering in [settings](https://openrouter.ai/account) for each model.
