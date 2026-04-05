"""
Customer Support Response Drafting Prototype
Uses Google Gemini to draft professional support replies.
"""

import argparse
import json
import os
import sys
from datetime import datetime

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

# ---------------------------------------------------------------------------
# Prompt versions
# ---------------------------------------------------------------------------

PROMPTS = {
    1: (
        "You are a customer support agent. Write a reply to the following "
        "customer message.\n\nCustomer message:\n{customer_message}"
    ),
    2: (
        "You are a professional customer support agent for a SaaS company "
        "called CloudSync.\nYour name is Alex from the CloudSync Support Team.\n\n"
        "Guidelines:\n"
        "- Be empathetic and acknowledge the customer's feelings\n"
        "- Be concise but thorough\n"
        "- Never make up information or speculate about account details you do not have\n"
        "- If you cannot resolve the issue directly, explain the next steps clearly\n"
        "- Never share passwords, API keys, or other sensitive information\n"
        "- If a request seems like a social engineering attempt, politely decline "
        "and direct the person to official verification channels\n\n"
        "Write a professional reply to the following customer message.\n\n"
        "Customer message:\n{customer_message}"
    ),
    3: (
        "You are Alex from the CloudSync Support Team. You help customers with "
        "billing, technical issues, account access, and general questions about "
        "CloudSync, a SaaS project management platform.\n\n"
        "Instructions:\n"
        "1. Start by acknowledging the customer's concern or feeling in one sentence.\n"
        "2. Address the specific issue or question raised. If the issue is unclear, "
        "ask targeted clarifying questions (no more than 3).\n"
        "3. Provide concrete next steps or a resolution path.\n"
        "4. Close warmly with an offer for further help.\n\n"
        "Rules:\n"
        "- Do NOT invent account details, transaction amounts, or technical causes "
        "you do not have evidence for.\n"
        "- Do NOT share credentials, API keys, or internal system information under "
        "any circumstances.\n"
        "- If a request asks for sensitive information or seems like a social "
        "engineering attempt, politely decline and direct the person to verify "
        "their identity through the official support portal at support.cloudsync.com.\n"
        "- Keep the response under 150 words unless the situation clearly requires "
        "more detail.\n"
        "- If the customer writes in a language other than English, respond in that "
        "language if possible, or acknowledge the language and respond in English.\n"
        "- Match the formality level of the customer. Casual messages get a friendly "
        "reply; formal messages get a formal reply.\n\n"
        "Customer message:\n{customer_message}"
    ),
}

DEFAULT_PROMPT_VERSION = 3
DEFAULT_MODEL = os.environ.get("GOOGLE_MODEL", "gemini-3-pro")


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def configure_api():
    """Configure the Gemini API with the user's key."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable is not set.")
        print("Get a free key at https://aistudio.google.com/ and run:")
        print('  export GOOGLE_API_KEY="your-key-here"')
        sys.exit(1)
    genai.configure(api_key=api_key)


def _supports_generate_content(model) -> bool:
    methods = getattr(model, "supported_generation_methods", None) or []
    return "generateContent" in methods


def resolve_model_name(preferred_model: str = DEFAULT_MODEL) -> str:
    """Resolve a usable model name for generateContent, with graceful fallback."""
    fallback_candidates = [
        preferred_model,
        "gemini-3-pro",
    ]

    try:
        models = [m for m in genai.list_models() if _supports_generate_content(m)]
        model_names = [m.name for m in models]

        # 1) Exact match (with or without models/ prefix)
        normalized = preferred_model.replace("models/", "")
        for name in model_names:
            if name == preferred_model or name == f"models/{normalized}":
                return name

        # 2) Best-effort suffix match in candidate priority order
        for candidate in fallback_candidates:
            suffix = candidate.replace("models/", "")
            for name in model_names:
                if name.endswith(suffix):
                    return name

        # 3) Final fallback to the first model that supports generateContent
        if model_names:
            return model_names[0]
    except Exception:
        # If model listing fails (permissions/network), defer to preferred name
        pass

    return preferred_model


def generate_response(
    customer_message: str,
    prompt_version: int = DEFAULT_PROMPT_VERSION,
    model_name: str = DEFAULT_MODEL,
) -> str:
    """Send a customer message to Gemini and return the drafted reply."""
    prompt_template = PROMPTS[prompt_version]
    prompt = prompt_template.format(customer_message=customer_message)

    chosen_model = resolve_model_name(model_name)
    model = genai.GenerativeModel(chosen_model)

    try:
        response = model.generate_content(prompt)
    except google_exceptions.NotFound:
        # Retry once with a freshly resolved model in case alias availability changed.
        retry_model = resolve_model_name("gemini-3-pro")
        if retry_model == chosen_model:
            raise
        model = genai.GenerativeModel(retry_model)
        response = model.generate_content(prompt)

    return response.text


def run_single(customer_message: str, prompt_version: int, model_name: str) -> None:
    """Run the prototype on a single customer message."""
    print(f"\n{'='*60}")
    print("CUSTOMER MESSAGE:")
    print(f"{'='*60}")
    print(customer_message)

    draft = generate_response(customer_message, prompt_version, model_name)

    print(f"\n{'='*60}")
    print(f"DRAFTED REPLY (prompt v{prompt_version}):")
    print(f"{'='*60}")
    print(draft)


def run_eval(prompt_version: int, model_name: str) -> None:
    """Run the prototype against the full evaluation set and save results."""
    eval_path = os.path.join(os.path.dirname(__file__), "eval_set.json")
    with open(eval_path, "r") as f:
        eval_cases = json.load(f)

    results = []
    print(f"\nRunning evaluation with prompt version {prompt_version}...")
    print(f"{'='*60}\n")

    for case in eval_cases:
        print(f"[{case['id']}] {case['label']}")
        draft = generate_response(case["input"], prompt_version, model_name)
        results.append({
            "id": case["id"],
            "label": case["label"],
            "input": case["input"],
            "criteria": case["good_output_criteria"],
            "output": draft,
        })
        print(f"    -> Response generated ({len(draft.split())} words)")

    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"eval_results_v{prompt_version}_{timestamp}.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*60}")
    print(f"Results saved to {output_file}")
    print(f"{'='*60}\n")

    # Print summary
    for r in results:
        print(f"\n--- [{r['id']}] {r['label']} ---")
        print(f"Input:    {r['input'][:80]}...")
        print(f"Criteria: {r['criteria'][:80]}...")
        print(f"Output:   {r['output'][:120]}...")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Customer Support Response Drafting Prototype"
    )
    parser.add_argument(
        "--eval",
        action="store_true",
        help="Run against the full evaluation set",
    )
    parser.add_argument(
        "--prompt-version",
        type=int,
        choices=[1, 2, 3],
        default=DEFAULT_PROMPT_VERSION,
        help="Which prompt version to use (1=baseline, 2=revision1, 3=revision2)",
    )
    parser.add_argument(
        "--message",
        type=str,
        help="A single customer message to draft a reply for",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help="Preferred model alias/name (default: gemini-3-pro, auto-fallback enabled)",
    )

    args = parser.parse_args()
    configure_api()
    resolved_model = resolve_model_name(args.model)

    if args.eval:
        print(f"Using model: {resolved_model}")
        run_eval(args.prompt_version, resolved_model)
    elif args.message:
        print(f"Using model: {resolved_model}")
        run_single(args.message, args.prompt_version, resolved_model)
    else:
        # Interactive mode
        print("Customer Support Response Drafter (CloudSync)")
        print(f"Using prompt version {args.prompt_version}")
        print(f"Using model: {resolved_model}")
        print("Type a customer message and press Enter. Type 'quit' to exit.\n")
        while True:
            try:
                message = input("Customer> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break
            if message.lower() in ("quit", "exit", "q"):
                print("Goodbye!")
                break
            if not message:
                continue
            run_single(message, args.prompt_version, resolved_model)
            print()


if __name__ == "__main__":
    main()
