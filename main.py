#!/usr/bin/env python3
"""
AI Chat Client - OpenRouter Edition
====================================
Современный AI чат-клиент с поддержкой бесплатных моделей

Автор: Your Name
GitHub: https://github.com/your-username/ai-chat-client
"""

from ui.app import App

def main():
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()

if __name__ == "__main__":
    main()