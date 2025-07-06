import json
import re

from src.config.chunk_prompt import LLM_TEXT_QUESTIONS_USER_PROMPT, LLM_TEXT_QUESTIONS_SYSTEM_PROMPT
from src.config.vl_prompt import VL_TABLE_DESCRIPTION_USER_PROMPT,VL_TABLE_DESCRIPTION_SYSTEM_PROMPT, VL_IMAGE_DESCRIPTION_SYSTEM_PROMPT, VL_IMAGE_DESCRIPTION_USER_PROMPT

from src.connectors.openrouter_connector import query_vl_model, query_llm_model

import logging

logger = logging.getLogger(__name__)

class LLMHandler:
    def __init__(
            self,
            enrichment_model_name="meta-llama/llama-3-8b-instruct",
            vl_model_name="qwen/qwen2.5-vl-7b-instruct",
            attempts=5
        ):

        self.enrichment_model_name = enrichment_model_name
        self.vl_model_name = vl_model_name
        self.attempts = attempts

    def extract_table_description(self, image=None, page_text=None, table_raw=None, history=None):
        # Query the OpenRouter API to get the table description
        output = {}
        for attempt in range(1, self.attempts + 1):
            try:
                logger.info(f"Attempt {attempt} of {self.attempts} to extract table description")
                try:
                    response = query_vl_model(model_name=self.vl_model_name,
                                                       image=image,
                                                       user_prompt=VL_TABLE_DESCRIPTION_USER_PROMPT,
                                                       user_input={
                                                           'table_raw': table_raw,
                                                           'page_text': page_text
                                                       },
                                                       system_prompt=VL_TABLE_DESCRIPTION_SYSTEM_PROMPT)
                except Exception as e:
                    logger.error(f"Error while querying API for image description. Error={e}")

                try:
                    output = json.loads(json.loads(response)['choices'][0]['message']['content'][7:-3])
                    break
                except Exception as e:
                    logger.error(f"Error while parsing table description response: {response}. Error={e}")
            except Exception as e:
                    logger.error(f"Error while extracting table description. Error={e}")
        return output

    def extract_image_description(self, image=None, page_text=None, history=None):
        images = {}
        for attempt in range(1, self.attempts + 1):
            try:
                logger.info(f"Attempt {attempt} of {self.attempts} to extract image description")
                try:
                    # Query the OpenRouter API to get the image description
                    response = query_vl_model(model_name=self.vl_model_name,
                                                       image=image,
                                                       user_prompt=VL_IMAGE_DESCRIPTION_USER_PROMPT,
                                                       user_input={
                                                           'page_text': page_text
                                                       },
                                                       system_prompt=VL_IMAGE_DESCRIPTION_SYSTEM_PROMPT)
                except Exception as e:
                    logger.error(f"Error while querying API for image description. Error={e}")
                try:
                    images = json.loads(json.loads(response)['choices'][0]['message']['content'][7:-3])
                    break
                except Exception as e:
                    logger.error(f"Error while parsing image description response: {response}. Error={e}")
            except Exception as e:
                logger.error(f"Error while extracting image description. Error={e}")

        return images

    def get_text_questions(self, text_chunk):
        """
        Generates relevant questions that can be answered from the given text chunk.

        Args:
        text_chunk (str): The text chunk to generate questions from.
        num_questions (int): Number of questions to generate.
        model (str): The model to use for question generation.

        Returns:
        List[str]: List of generated questions.
        """

        questions = []
        for attempt in range(1, self.attempts + 1):
            try:
                logger.info(f"Attempt {attempt} of {self.attempts} to get text questions")
                try:
                    response = query_llm_model(model_name=self.enrichment_model_name,
                                              user_prompt=LLM_TEXT_QUESTIONS_USER_PROMPT,
                                              user_input={
                                                  'text_chunk': text_chunk
                                              },
                                              system_prompt=LLM_TEXT_QUESTIONS_SYSTEM_PROMPT)
                except Exception as e:
                    logger.error(f"Error while querying API for text questions. Error={e}")

                try:
                    output = json.loads(response)['choices'][0]['message']['content']

                    questions = []

                    # Extract questions using regex pattern matching
                    for line in output.split('\n'):
                        # Remove numbering and clean up whitespace
                        cleaned_line = re.sub(r'^\d+\.\s*', '', line.strip())
                        if cleaned_line and cleaned_line.endswith('?'):
                            questions.append(cleaned_line)
                    break
                except Exception as e:
                    logger.error(f"Error while parsing text questions response: {response}. Error={e}")
            except Exception as e:
                logger.error(f"Error while extracting text questions. Error={e}")

        return questions



