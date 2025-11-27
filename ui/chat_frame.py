import customtkinter as ctk
from threading import Thread
from datetime import datetime


class ChatFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app

        # Цветовая схема
        self.colors = {
            "user_bubble": "#6366f1",  # Индиго
            "user_bubble_dark": "#4f46e5",
            "ai_bubble": "#1e1e2e",  # Тёмно-серый
            "ai_bubble_light": "#f1f5f9",
            "accent": "#8b5cf6",  # Фиолетовый
            "border": "#374151",
            "text_secondary": "#9ca3af"
        }

        self.setup_ui()

    def setup_ui(self):
        # === ЗАГОЛОВОК ===
        self.header = ctk.CTkFrame(
            self,
            height=70,
            corner_radius=0,
            fg_color=("gray95", "#1a1a2e"),
            border_width=0
        )
        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        # Левая часть заголовка
        header_left = ctk.CTkFrame(self.header, fg_color="transparent")
        header_left.pack(side="left", fill="y", padx=20)

        self.chat_title_label = ctk.CTkLabel(
            header_left,
            text="✨ Новый диалог",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=("gray10", "#e2e8f0")
        )
        self.chat_title_label.pack(side="left", pady=20)

        # Правая часть заголовка
        header_right = ctk.CTkFrame(self.header, fg_color="transparent")
        header_right.pack(side="right", fill="y", padx=20)

        self.model_badge = ctk.CTkLabel(
            header_right,
            text="",
            font=ctk.CTkFont(size=11),
            fg_color=("#e0e7ff", "#312e81"),
            corner_radius=12,
            padx=12,
            pady=4,
            text_color=("#4338ca", "#a5b4fc")
        )
        self.model_badge.pack(side="right", pady=20)

        # === ОБЛАСТЬ СООБЩЕНИЙ ===
        self.messages_container = ctk.CTkFrame(
            self,
            fg_color=("gray98", "#0f0f1a"),
            corner_radius=0
        )
        self.messages_container.pack(fill="both", expand=True)

        self.messages_frame = ctk.CTkScrollableFrame(
            self.messages_container,
            fg_color="transparent",
            scrollbar_button_color=("#c7d2fe", "#4338ca"),
            scrollbar_button_hover_color=("#a5b4fc", "#6366f1")
        )
        self.messages_frame.pack(fill="both", expand=True, padx=30, pady=20)

        # Приветственное сообщение
        self.welcome_frame = ctk.CTkFrame(self.messages_frame, fg_color="transparent")
        self.welcome_frame.pack(expand=True, pady=100)

        ctk.CTkLabel(
            self.welcome_frame,
            text="🤖",
            font=ctk.CTkFont(size=60)
        ).pack()

        ctk.CTkLabel(
            self.welcome_frame,
            text="Привет! Я AI ассистент",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("gray20", "#e2e8f0")
        ).pack(pady=(20, 10))

        ctk.CTkLabel(
            self.welcome_frame,
            text="Напишите сообщение, чтобы начать диалог",
            font=ctk.CTkFont(size=14),
            text_color=("gray50", "#64748b")
        ).pack()

        # === ПАНЕЛЬ ВВОДА ===
        self.input_container = ctk.CTkFrame(
            self,
            fg_color=("gray95", "#1a1a2e"),
            corner_radius=0,
            height=120
        )
        self.input_container.pack(fill="x", side="bottom")
        self.input_container.pack_propagate(False)

        # Внутренний контейнер с рамкой
        input_wrapper = ctk.CTkFrame(
            self.input_container,
            fg_color=("white", "#252542"),
            corner_radius=16,
            border_width=2,
            border_color=("#e2e8f0", "#374151")
        )
        input_wrapper.pack(fill="x", padx=30, pady=20)

        # Поле ввода
        self.message_input = ctk.CTkTextbox(
            input_wrapper,
            height=60,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            wrap="word",
            fg_color="transparent",
            border_width=0,
            text_color=("gray10", "#e2e8f0")
        )
        self.message_input.pack(side="left", fill="both", expand=True, padx=15, pady=10)
        self.message_input.bind("<Control-Return>", lambda e: self.send_message())
        self.message_input.bind("<Return>", self._handle_enter)

        # Placeholder
        self.message_input.insert("1.0", "Напишите сообщение...")
        self.message_input.configure(text_color=("gray50", "#64748b"))
        self.message_input.bind("<FocusIn>", self._on_focus_in)
        self.message_input.bind("<FocusOut>", self._on_focus_out)

        # Кнопки справа
        btn_frame = ctk.CTkFrame(input_wrapper, fg_color="transparent")
        btn_frame.pack(side="right", padx=10, pady=10)

        self.send_btn = ctk.CTkButton(
            btn_frame,
            text="",
            width=45,
            height=45,
            corner_radius=12,
            font=ctk.CTkFont(size=18),
            fg_color=("#6366f1", "#6366f1"),
            hover_color=("#4f46e5", "#4f46e5"),
            command=self.send_message,
            image=None
        )
        self.send_btn.pack()

        # Используем текст вместо иконки
        self.send_btn.configure(text="➤")

    def _handle_enter(self, event):
        """Обработка Enter (отправка) и Shift+Enter (новая строка)"""
        if not event.state & 0x1:  # Если не зажат Shift
            self.send_message()
            return "break"

    def _on_focus_in(self, event):
        current = self.message_input.get("1.0", "end-1c")
        if current == "Напишите сообщение...":
            self.message_input.delete("1.0", "end")
            self.message_input.configure(text_color=("gray10", "#e2e8f0"))

    def _on_focus_out(self, event):
        current = self.message_input.get("1.0", "end-1c").strip()
        if not current:
            self.message_input.insert("1.0", "Напишите сообщение...")
            self.message_input.configure(text_color=("gray50", "#64748b"))

    def set_title(self, title: str, model: str = ""):
        self.chat_title_label.configure(text=f"💬 {title}")
        if model:
            short_model = model.split("/")[-1].replace(":free", "").replace("-instruct", "")
            self.model_badge.configure(text=f"🤖 {short_model}")
        else:
            self.model_badge.configure(text="")

    def add_message(self, role: str, content: str):
        """Добавить сообщение с современным дизайном"""

        # Скрыть приветствие
        if self.welcome_frame.winfo_exists():
            self.welcome_frame.destroy()

        is_user = role == "user"

        # Основной контейнер сообщения
        msg_container = ctk.CTkFrame(
            self.messages_frame,
            fg_color="transparent"
        )
        msg_container.pack(fill="x", pady=12)

        # Внутренний контейнер для выравнивания
        inner_container = ctk.CTkFrame(msg_container, fg_color="transparent")

        if is_user:
            inner_container.pack(anchor="e")
        else:
            inner_container.pack(anchor="w")

        # Аватар + сообщение
        msg_row = ctk.CTkFrame(inner_container, fg_color="transparent")
        msg_row.pack(fill="x")

        if not is_user:
            # Аватар AI слева
            avatar_frame = ctk.CTkFrame(
                msg_row,
                width=40,
                height=40,
                corner_radius=20,
                fg_color=("#8b5cf6", "#7c3aed")
            )
            avatar_frame.pack(side="left", padx=(0, 12))
            avatar_frame.pack_propagate(False)

            ctk.CTkLabel(
                avatar_frame,
                text="🤖",
                font=ctk.CTkFont(size=18)
            ).place(relx=0.5, rely=0.5, anchor="center")

        # Пузырь сообщения
        bubble = ctk.CTkFrame(
            msg_row,
            fg_color=(
                (self.colors["user_bubble"], self.colors["user_bubble_dark"])
                if is_user else
                (self.colors["ai_bubble_light"], self.colors["ai_bubble"])
            ),
            corner_radius=18
        )
        bubble.pack(side="right" if is_user else "left")

        # Текст сообщения
        text_label = ctk.CTkLabel(
            bubble,
            text=content,
            wraplength=450,
            justify="left",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color="white" if is_user else ("gray10", "#e2e8f0"),
            padx=16,
            pady=12
        )
        text_label.pack()

        if is_user:
            # Аватар пользователя справа
            avatar_frame = ctk.CTkFrame(
                msg_row,
                width=40,
                height=40,
                corner_radius=20,
                fg_color=("#6366f1", "#4f46e5")
            )
            avatar_frame.pack(side="right", padx=(12, 0))
            avatar_frame.pack_propagate(False)

            ctk.CTkLabel(
                avatar_frame,
                text="👤",
                font=ctk.CTkFont(size=18)
            ).place(relx=0.5, rely=0.5, anchor="center")

        # Время отправки
        time_label = ctk.CTkLabel(
            inner_container,
            text=datetime.now().strftime("%H:%M"),
            font=ctk.CTkFont(size=10),
            text_color=("gray50", "#64748b")
        )
        time_label.pack(anchor="e" if is_user else "w", padx=52, pady=(4, 0))

        # Прокрутка вниз
        self.messages_frame._parent_canvas.yview_moveto(1.0)

        return bubble, text_label

    def add_streaming_message(self) -> tuple:
        """Создать пустое сообщение для стриминга"""
        return self.add_message("assistant", "▌")

    def update_streaming_message(self, label, content: str):
        """Обновить текст"""
        label.configure(text=content + " ▌")
        self.messages_frame._parent_canvas.yview_moveto(1.0)

    def finalize_streaming_message(self, label, content: str):
        """Завершить стриминг"""
        label.configure(text=content)

    def clear_messages(self):
        for widget in self.messages_frame.winfo_children():
            widget.destroy()

        # Показать приветствие снова
        self.welcome_frame = ctk.CTkFrame(self.messages_frame, fg_color="transparent")
        self.welcome_frame.pack(expand=True, pady=100)

        ctk.CTkLabel(
            self.welcome_frame,
            text="🤖",
            font=ctk.CTkFont(size=60)
        ).pack()

        ctk.CTkLabel(
            self.welcome_frame,
            text="Привет! Я AI ассистент",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("gray20", "#e2e8f0")
        ).pack(pady=(20, 10))

        ctk.CTkLabel(
            self.welcome_frame,
            text="Напишите сообщение, чтобы начать диалог",
            font=ctk.CTkFont(size=14),
            text_color=("gray50", "#64748b")
        ).pack()

    def send_message(self):
        """Отправить сообщение"""
        message = self.message_input.get("1.0", "end-1c").strip()

        if not message or message == "Напишите сообщение...":
            return

        # Создаём чат если нужно
        if not self.app.current_chat_id:
            self.app.new_chat()

        self.message_input.delete("1.0", "end")
        self.send_btn.configure(state="disabled", text="⏳", fg_color=("#94a3b8", "#475569"))

        Thread(target=self.app.process_message, args=(message,), daemon=True).start()

    def enable_input(self):
        self.send_btn.configure(state="normal", text="➤", fg_color=("#6366f1", "#6366f1"))