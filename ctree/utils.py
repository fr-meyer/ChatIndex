import openai
import logging
import time
import os
import ast
import json
import re

CHATGPT_API_KEY = os.getenv("CHATGPT_API_KEY")


def ChatGPT_API(model, prompt, api_key=CHATGPT_API_KEY, chat_history=None, temperature=0, max_tokens=None):
    
    max_retries = 10
    client = openai.OpenAI(api_key=api_key)
    for i in range(max_retries):
        try:
            if chat_history:
                messages = chat_history
                messages.append({"role": "user", "content": prompt})
            else:
                messages = [{"role": "user", "content": prompt}]
            
            # Build kwargs for API call
            api_kwargs = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
            }
            if max_tokens is not None:
                api_kwargs["max_tokens"] = max_tokens
            
            response = client.chat.completions.create(**api_kwargs)
   
            return response.choices[0].message.content
        except Exception as e:
            print('************* Retrying *************')
            logging.error(f"Error: {e}")
            if i < max_retries - 1:
                time.sleep(1)  # Wait for 1秒 before retrying
            else:
                logging.error('Max retries reached for prompt: ' + prompt)
                return "Error"


def _strip_json_fence(content):
    text = content.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, flags=re.IGNORECASE | re.DOTALL)
    if fenced:
        return fenced.group(1).strip()

    opening_fence = re.search(r"```(?:json)?\s*", text, flags=re.IGNORECASE)
    if opening_fence:
        return text[opening_fence.end():].strip()

    return text


def _without_trailing_commas(content):
    return re.sub(r",(\s*[}\]])", r"\1", content)


def extract_json(content):
    try:
        json_content = _strip_json_fence(content)
    except Exception as e:
        logging.error(f"Unexpected error while extracting JSON: {e}")
        return {}

    for candidate in (json_content, _without_trailing_commas(json_content)):
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    try:
        return ast.literal_eval(json_content)
    except (SyntaxError, ValueError) as literal_error:
        logging.error(f"Failed to parse JSON even after cleanup: {literal_error}")
        return {}
