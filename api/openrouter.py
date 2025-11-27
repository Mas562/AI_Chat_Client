import requests
import json as json_lib
from config import Config


class OpenRouterAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/ai-chat-client",
            "X-Title": Config.APP_NAME
        }

    def chat_stream(self, messages: list, model: str,
                    max_tokens: int = 2048, temperature: float = 0.7):
        """Стриминг ответа"""

        if not messages:
            yield "⚠️ Ошибка: пустой список сообщений"
            return

        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True
        }

        print(f"[API] Model: {model}")
        print(f"[API] Messages count: {len(messages)}")

        try:
            response = requests.post(
                Config.API_URL,
                headers=self.headers,
                json=payload,
                stream=True,
                timeout=120
            )

            print(f"[API] Status: {response.status_code}")

            if response.status_code == 401:
                yield "🔑 Ошибка: Неверный API ключ"
                return
            elif response.status_code == 403:
                yield "🚫 Ошибка: Модель недоступна"
                return
            elif response.status_code == 404:
                yield "❌ Ошибка: Модель не найдена. Выберите другую в настройках."
                return
            elif response.status_code == 429:
                yield "⚡ Rate limit. Подождите минуту."
                return
            elif response.status_code >= 400:
                yield f"❌ Ошибка сервера: {response.status_code}"
                return

            collected = ""

            for line in response.iter_lines():
                if line:
                    line = line.decode("utf-8")
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json_lib.loads(data)

                            if "error" in chunk:
                                error_msg = chunk["error"].get("message", "Unknown error")
                                yield f"\n❌ {error_msg}"
                                return

                            choices = chunk.get("choices", [])
                            if choices:
                                delta = choices[0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    collected += content
                                    yield content
                        except:
                            continue

            if not collected.strip():
                yield "⚠️ Модель не вернула ответ"

        except requests.exceptions.Timeout:
            yield "⏱️ Timeout"
        except requests.exceptions.ConnectionError:
            yield "🌐 Нет интернета"
        except Exception as e:
            yield f"❌ {str(e)}"