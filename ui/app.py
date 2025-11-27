import customtkinter as ctk
from tkinter import filedialog, messagebox
from threading import Thread
import time
from config import Config
from api.openrouter import OpenRouterAPI
from database.db_manager import DatabaseManager
from utils.export import ExportManager
from ui.sidebar import Sidebar
from ui.chat_frame import ChatFrame
from ui.settings_window import SettingsWindow


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        Config.init()
        self.settings = Config.load_settings()
        self.db = DatabaseManager()
        self.api = None
        self.current_chat_id = None
        self.is_processing = False

        self.title(f"🤖 {Config.APP_NAME}")
        self.geometry("1300x850")
        self.minsize(1000, 700)

        # Применить тему
        ctk.set_appearance_mode(self.settings.get("theme", "dark"))
        ctk.set_default_color_theme("blue")

        # Цвет фона окна
        self.configure(fg_color=("#f1f5f9", "#0f0f1a"))

        self.setup_ui()
        self.refresh_chat_list()
        self.init_api()

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Сайдбар
        self.sidebar = Sidebar(self, self)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Область чата
        self.chat_frame = ChatFrame(self, self)
        self.chat_frame.grid(row=0, column=1, sticky="nsew")

    def init_api(self):
        if self.settings.get("api_key"):
            self.api = OpenRouterAPI(self.settings["api_key"])
        else:
            self.api = None

    # === ЧАТЫ ===

    def new_chat(self) -> int:
        """Создать новый чат"""
        chat_id = self.db.create_chat(
            model=self.settings.get("model", ""),
            system_prompt=self.settings.get("system_prompt", "")
        )
        self.current_chat_id = chat_id
        self.chat_frame.clear_messages()
        self.chat_frame.set_title("Новый чат", self.settings.get("model", ""))
        self.refresh_chat_list()
        return chat_id

    def load_chat(self, chat_id: int):
        self.current_chat_id = chat_id
        chat = self.db.get_chat(chat_id)

        if chat:
            self.chat_frame.set_title(chat["title"], chat.get("model", ""))
            self.chat_frame.clear_messages()

            # Скрыть приветствие если есть сообщения
            messages = self.db.get_messages(chat_id)
            for msg in messages:
                self.chat_frame.add_message(msg["role"], msg["content"])

        self.refresh_chat_list()

    def delete_chat(self, chat_id: int):
        if messagebox.askyesno("Удаление", "Удалить этот чат?"):
            self.db.delete_chat(chat_id)
            if self.current_chat_id == chat_id:
                self.current_chat_id = None
                self.chat_frame.clear_messages()
                self.chat_frame.set_title("✨ Новый диалог", "")
            self.refresh_chat_list()

    def clear_current_chat(self):
        if self.current_chat_id:
            self.db.clear_messages(self.current_chat_id)
            self.chat_frame.clear_messages()

    def refresh_chat_list(self):
        chats = self.db.get_all_chats()
        self.sidebar.refresh_chats(chats, self.current_chat_id)

    # === СООБЩЕНИЯ ===

    def process_message(self, message: str):
        """Обработка сообщения"""

        if self.is_processing:
            return

        self.is_processing = True

        if not self.api:
            self.after(0, lambda: messagebox.showerror(
                "Ошибка", "Добавьте API ключ в настройках!"
            ))
            self.after(0, self.chat_frame.enable_input)
            self.is_processing = False
            return

        chat_id = self.current_chat_id

        if not chat_id:
            self.after(0, self.chat_frame.enable_input)
            self.is_processing = False
            return

        # Добавить сообщение пользователя
        self.after(0, lambda: self.chat_frame.add_message("user", message))
        self.db.add_message(chat_id, "user", message)

        # Обновить заголовок
        messages = self.db.get_messages(chat_id)
        if len(messages) == 1:
            title = message[:40] + "..." if len(message) > 40 else message
            self.db.update_chat_title(chat_id, title)
            model = self.settings.get("model", "")
            self.after(0, lambda: self.chat_frame.set_title(title, model))
            self.after(0, self.refresh_chat_list)

        # Подготовить API сообщения
        chat = self.db.get_chat(chat_id)

        api_messages = []
        system_prompt = self.settings.get("system_prompt", "")
        if chat and chat.get("system_prompt"):
            system_prompt = chat["system_prompt"]
        if system_prompt:
            api_messages.append({"role": "system", "content": system_prompt})

        for msg in messages:
            api_messages.append({"role": msg["role"], "content": msg["content"]})

        # Создать placeholder
        label_holder = {"label": None}

        def create_placeholder():
            _, label = self.chat_frame.add_streaming_message()
            label_holder["label"] = label

        self.after(0, create_placeholder)
        time.sleep(0.2)

        # Получить ответ
        full_response = ""
        model = self.settings.get("model", "mistralai/mistral-7b-instruct:free")

        try:
            for chunk in self.api.chat_stream(
                    api_messages,
                    model,
                    self.settings.get("max_tokens", 2048),
                    self.settings.get("temperature", 0.7)
            ):
                full_response += chunk
                text = full_response

                if label_holder["label"]:
                    self.after(0, lambda t=text:
                    self.chat_frame.update_streaming_message(label_holder["label"], t))
        except Exception as e:
            full_response = f"❌ Ошибка: {str(e)}"

        # Финализация
        if label_holder["label"]:
            self.after(0, lambda:
            self.chat_frame.finalize_streaming_message(label_holder["label"], full_response))

        # Сохранить
        if full_response and not any(full_response.startswith(x) for x in ["❌", "🔑", "🚫", "⚡", "⚠️"]):
            self.db.add_message(chat_id, "assistant", full_response)

        self.after(0, self.chat_frame.enable_input)
        self.is_processing = False

    # === ЭКСПОРТ ===

    def export_chat(self):
        if not self.current_chat_id:
            messagebox.showwarning("Экспорт", "Сначала выберите чат")
            return

        chat = self.db.get_chat(self.current_chat_id)
        messages = self.db.get_messages(self.current_chat_id)

        if not messages:
            messagebox.showwarning("Экспорт", "Чат пуст")
            return

        format_window = ctk.CTkToplevel(self)
        format_window.title("📥 Экспорт")
        format_window.geometry("350x250")
        format_window.transient(self)
        format_window.grab_set()
        format_window.configure(fg_color=("#f8fafc", "#12121f"))

        ctk.CTkLabel(
            format_window,
            text="📥 Выберите формат",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("gray10", "#e2e8f0")
        ).pack(pady=(30, 20))

        def export_as(fmt):
            format_window.destroy()

            extensions = {"md": ".md", "json": ".json", "txt": ".txt"}

            filepath = filedialog.asksaveasfilename(
                defaultextension=extensions[fmt],
                filetypes=[(f"{fmt.upper()}", f"*{extensions[fmt]}")]
            )

            if filepath:
                if fmt == "md":
                    content = ExportManager.to_markdown(chat["title"], messages)
                elif fmt == "json":
                    content = ExportManager.to_json(chat["title"], messages)
                else:
                    content = ExportManager.to_txt(chat["title"], messages)

                ExportManager.save_file(content, filepath)
                messagebox.showinfo("✅ Готово", f"Файл сохранён:\n{filepath}")

        btn_frame = ctk.CTkFrame(format_window, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30)

        formats = [
            ("📝 Markdown", "md"),
            ("📋 JSON", "json"),
            ("📄 Text", "txt")
        ]

        for text, fmt in formats:
            ctk.CTkButton(
                btn_frame,
                text=text,
                command=lambda f=fmt: export_as(f),
                height=45,
                corner_radius=12,
                fg_color=("#6366f1", "#6366f1"),
                hover_color=("#4f46e5", "#4f46e5"),
                font=ctk.CTkFont(size=14)
            ).pack(fill="x", pady=5)

    # === НАСТРОЙКИ ===

    def open_settings(self):
        SettingsWindow(self, self.settings, self.apply_settings)

    def apply_settings(self, new_settings):
        self.settings = new_settings
        Config.save_settings(new_settings)

        ctk.set_appearance_mode(new_settings.get("theme", "dark"))
        self.init_api()

    def on_closing(self):
        self.db.close()
        self.destroy()