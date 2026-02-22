import os
import requests
import logging
from google import genai
import re
from transformers import pipeline
# from google.generativeai.types import GenerationConfig


class LLMClient:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key is required for LLMClient")
        self.api_key = api_key
        self.gemini_client = genai.Client(api_key=api_key)
        # self.hf_fallback = pipeline("text-generation", model="gpt2")
        self.logger = logging.getLogger(__name__)

    def generate_questions(self, prompts:dict) -> list:
        """Generate interview questions using Gemini or fallback to HuggingFace."""
        try:
            self.logger.info("Sending prompt to Gemini API")
            
            full_prompt = f"{prompts['system_prompt']}\n\n{prompts['user_prompt']}"
            response = self.gemini_client.models.generate_content(
                                    model="gemini-2.0-flash",
                                    contents=[
                                        {"role": "user", "parts": [{"text": full_prompt}]}
                                    ]
                                )
            
            raw_text = response.text if response.text is not None else ""
            raw = raw_text.strip()
            if not raw:
                raise ValueError("Gemini response is empty")
            
            cleaned_questions = self.clean_gemini_json(raw)
            
            if not cleaned_questions:
                raise ValueError("Gemini response empty")
            
            question_texts = []
            for item in cleaned_questions:
                if isinstance(item, dict) and "question" in item:
                    question_texts.append(item["question"])
                else:
                    self.logger.warning("Unexpected item in parsed_list: %r", item)
            return question_texts
        except Exception as e:
            self.logger.warning(f"Gemini API failed: {e}, using HuggingFace fallback")
            # return self._fallback_generate(prompt)
            return []
        
    def clean_gemini_json(self, raw: str) -> dict:
        import json
        cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
        return json.loads(cleaned)

    # def _fallback_generate(self, prompt: str) -> list:
    #     """Fallback to HuggingFace for question generation."""
    #     try:
    #         response = self.hf_fallback(prompt, max_length=100, num_return_sequences=10)
    #         if isinstance(response, list):
    #             return [r.get("generated_text", "") for r in response if isinstance(r, dict)]
    #         else:
    #             self.logger.error("Unexpected response format from HuggingFace fallback")
    #             raise ValueError("Invalid HuggingFace response format")
    #     except Exception as e:
    #         self.logger.error(f"HuggingFace fallback failed: {e}")
    #         raise

    def generate_feedback(self, prompts: dict) -> dict:
        """Generate feedback and summary using Gemini or fallback."""
        try:
            self.logger.info("Sending feedback prompt to Gemini API")
            full_prompt = f"{prompts['system_prompt']}\n\n{prompts['user_prompt']}"
            response = self.gemini_client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[{"role": "user", "parts": [{"text": full_prompt}]}]
            )
            raw_text = response.text if response.text is not None else ""
            raw = raw_text.strip()
            if not raw:
                raise ValueError("Gemini response is empty")
            return self.clean_gemini_json(raw)
        except Exception as e:
            self.logger.warning(f"Gemini API failed for feedback: {e}")
            # Fallback logic could go here
            raise
