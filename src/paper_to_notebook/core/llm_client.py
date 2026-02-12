"""Azure OpenAI exclusive client."""
from __future__ import annotations

import json
import time
import os
from typing import Callable, Optional, Any
from openai import AzureOpenAI

from ..config import MAX_RETRIES, RETRY_DELAYS


def _get_client() -> AzureOpenAI:
    return AzureOpenAI(
        api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT")
    )


def call_llm(
    system_prompt: str,
    user_content: list | str,
    max_tokens: int = 4096,
    model: str | None = None,
) -> str:
    """Make an Azure OpenAI API call."""
    client = _get_client()
    deployment_name = model or os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
    
    # Process user_content for OpenAI format
    messages = [{"role": "system", "content": system_prompt}]
    
    prompt_text = ""
    if isinstance(user_content, str):
        prompt_text = user_content
    else:
        for part in user_content:
            if isinstance(part, str):
                prompt_text += part
            else:
                # Basic string representation for non-string parts in Azure context
                prompt_text += f"\n[Attachment: {type(part).__name__}]"

    messages.append({"role": "user", "content": prompt_text})
    
    response = client.chat.completions.create(
        model=deployment_name,
        messages=messages,
        max_tokens=max_tokens,
        temperature=0.7
    )
    return response.choices[0].message.content


def call_llm_with_retry(
    system_prompt: str,
    user_content: list | str,
    max_tokens: int = 4096,
    model: str | None = None,
    **kwargs # Accept but ignore extra params like api_key, on_thinking
) -> str:
    """Call Azure OpenAI with retry logic."""
    last_error = None

    for attempt in range(MAX_RETRIES):
        try:
            return call_llm(system_prompt, user_content, max_tokens, model)

        except Exception as e:
            error_str = str(e).lower()
            if any(keyword in error_str for keyword in ["429", "rate", "500", "503", "overloaded", "unavailable"]):
                last_error = e
                wait = RETRY_DELAYS[min(attempt, len(RETRY_DELAYS) - 1)]
                print(f"  Transient error. Waiting {wait}s before retry {attempt+1}/{MAX_RETRIES}...")
                time.sleep(wait)
            else:
                raise

    raise RuntimeError(f"Failed after {MAX_RETRIES} retries. Last error: {last_error}")


def parse_llm_json(raw_text: str, step_name: str, **kwargs) -> dict | list:
    """Parse JSON from LLM response."""
    text = raw_text.strip()

    if text.startswith("```"):
        try:
            first_newline = text.index("\n")
            text = text[first_newline + 1:]
        except ValueError:
            pass
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"  Warning: JSON parse failed in {step_name}. Attempting repair...")
        repair_prompt = (
            f"The following text was supposed to be valid JSON but has a syntax error:\n\n"
            f"{text[:4000]}\n\n"
            f"Error: {e}\n\n"
            f"Return ONLY the corrected valid JSON, nothing else."
        )
        repaired = call_llm_with_retry(
            system_prompt="You are a JSON repair tool. Return only valid JSON.",
            user_content=[repair_prompt],
            max_tokens=max(len(text) // 2, 4096)
        )
        repaired = repaired.strip()
        if repaired.startswith("```"):
            repaired = repaired.split("\n", 1)[1]
        if repaired.endswith("```"):
            repaired = repaired[:-3]
        return json.loads(repaired.strip())
