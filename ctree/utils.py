import openai
import logging
import time
import os
import json 

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


def extract_json(content):
    try:
        start_idx = content.find("```json")
        if start_idx != -1:
            start_idx += 7
            end_idx = content.rfind("```")
            json_content = content[start_idx:end_idx].strip()
        else:
            json_content = content.strip()

        try:
            return json.loads(json_content)
        except json.JSONDecodeError:
            pass

        try:
            import ast
            return ast.literal_eval(json_content)
        except (ValueError, SyntaxError):
            pass

        logging.error("Failed to parse JSON or Python-literal content")
        return {}
    except Exception as e:
        logging.error(f"Unexpected error while extracting JSON: {e}")
        return {}