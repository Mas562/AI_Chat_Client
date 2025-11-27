import os
import json
from pathlib import Path


class Config:
    APP_NAME = "AI Chat Client"
    VERSION = "1.0.0"

    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    DB_PATH = DATA_DIR / "chats.db"

    API_URL = "https://openrouter.ai/api/v1/chat/completions"

    # ✅ Актуальные бесплатные модели (январь 2025)
    FREE_MODELS = {
        "Mistral 7B": "mistralai/mistral-7b-instruct:free",
        "Llama 3.2 3B": "meta-llama/llama-3.2-3b-instruct:free",
        "Gemini 2.0 Flash": "google/gemini-2.0-flash-exp:free",
        "Llama 3.1 8B": "meta-llama/llama-3.1-8b-instruct:free",
        "Zephyr 7B": "huggingfaceh4/zephyr-7b-beta:free",
    }

    DEFAULT_SETTINGS = {
        "api_key": "",
        "model": "mistralai/mistral-7b-instruct:free",
        "theme": "dark",
        "system_prompt": "You are a helpful assistant.",
        "max_tokens": 2048,
        "temperature": 0.7
    }

    SETTINGS_PATH = DATA_DIR / "settings.json"

    @classmethod
    def init(cls):
        cls.DATA_DIR.mkdir(exist_ok=True)

    @classmethod
    def load_settings(cls):
        if cls.SETTINGS_PATH.exists():
            with open(cls.SETTINGS_PATH, "r", encoding="utf-8") as f:
                saved = json.load(f)
                return {**cls.DEFAULT_SETTINGS, **saved}
        return cls.DEFAULT_SETTINGS.copy()

    @classmethod
    def save_settings(cls, settings):
        with open(cls.SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)