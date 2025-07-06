import requests
import json

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='data/kzsk/prod/logs/llm.log',
                    encoding='utf-8',
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = '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'

def query_vl_model(model_name, user_prompt=None, user_input=None, image=None, system_prompt=None, history=None, temperature=0):
    user_prompt = user_prompt.format(**user_input) if user_prompt else user_input

    input_parameters = {
        "model": model_name,
        "user_prompt": user_prompt,
        "user_input": user_input,
        # "image": image, # Too long in logs(temp comment)
        "system_prompt": system_prompt,
        "history": history
    }

    logger.info(f"Query model {model_name}. params={input_parameters}")

    # base64_image = encode_image_base64(image)

    messages = [
        {
            "role": "system",
            "content": system_prompt},
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": user_prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{image}"
                    }
                }
            ]
        }
    ]

    response = requests.post(
        url=URL,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        data=json.dumps({
            "model": model_name,
            "messages": messages,
            "temperature": temperature
        })
    )

    if response.status_code!= 200:
        logger.error(f"Error while querying model {model_name}. status_code={response.status_code}, response={response.text}")

    #print(response.text)

    response_text = response.text
    logger.info(f"Response from model {model_name}. output={response_text.strip()}")

    return response_text

def query_llm_model(model_name, user_prompt=None, user_input=None, system_prompt=None, history=None, temperature=0):
    user_prompt = user_prompt.format(**user_input) if user_prompt else user_input

    input_parameters = {
        "model": model_name,
        "user_prompt": user_prompt,
        "user_input": user_input,
        "system_prompt": system_prompt,
        "history": history
    }

    logger.info(f"Query model {model_name}. params={input_parameters}")

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]

    response = requests.post(
        url=URL,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        data=json.dumps({
            "model": model_name,
            "messages": messages,
            "temperature": temperature
        })
    )

    if response.status_code!= 200:
        logger.error(f"Error while querying model {model_name}. status_code={response.status_code}, response={response.text}")

    print(response.text)

    response_text = response.text
    logger.info(f"Response from model {model_name}. output={response_text.strip()}")

    return response_text
