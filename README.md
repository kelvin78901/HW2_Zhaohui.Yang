# Assignment 2 - LLM Business Writing Prototype

## Business Workflow: Customer Support Response Drafting

### Overview
This prototype uses an LLM to draft professional customer support email responses based on incoming customer complaints or inquiries.

### Task Definition

- **Workflow:** Drafting customer support responses for a mid-size SaaS company
- **User:** A customer support agent who reviews and sends the drafted replies
- **Input:** A customer email or message describing an issue, complaint, or question
- **Output:** A professional, empathetic, and actionable draft reply ready for agent review
- **Why automate:** Support agents handle 50-100 tickets per day. Drafting responses is repetitive and time-consuming. An LLM can produce a solid first draft in seconds, letting agents focus on accuracy, edge cases, and personalization rather than composing from scratch. This reduces average handle time while maintaining quality.

## Setup

### Requirements
```
pip install -r requirements.txt
```

### API Key
Set your Google AI Studio API key as an environment variable:
```bash
export GOOGLE_API_KEY="your-api-key-here"
```

### Running the App
```bash
python app.py
```

To run against the full evaluation set:
```bash
python app.py --eval
```

To use a specific prompt version (1, 2, or 3):
```bash
python app.py --prompt-version 2
```

To use a specific model (default is `gemini-3-pro` with automatic fallback to an available model):
```bash
python app.py --model gemini-3-pro --prompt-version 2
```

### Run full prompt-comparison evaluation and generate summary

This script runs all eval cases across prompt versions and writes both JSON + Markdown summaries.

```bash
python run_eval_summary.py
```

Optional examples:

```bash
python run_eval_summary.py --model gemini-3-pro
python run_eval_summary.py --prompt-versions 2 3
```

Outputs:
- `eval_summary_YYYYMMDD_HHMMSS.json`
- `eval_summary_YYYYMMDD_HHMMSS.md`

## VIDEO LINK
> https://vimeo.com/1180215109