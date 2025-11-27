import customtkinter as ctk
from datetime import datetime


class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(
            parent,
            width=300,
            corner_radius=0,
            fg_color=("#f8fafc", "#12121f")
        )
        self.app = app
        self.chat_buttons = {}

        self.setup_ui()

    def setup_ui(self):
        # === ЛОГОТИП ===
        logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        logo_frame.pack(fill="x", padx=20, pady=(25, 20))

        ctk.CTkLabel(
            logo_frame,
            text="🤖 AI Chat",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=("#1e1b4b", "#e2e8f0")
        ).pack(side="left")

        # Версия
        ctk.CTkLabel(
            logo_frame,
            text="v1.0",
            font=ctk.CTkFont(size=10),
            text_color=("gray50", "#64748b")
        ).pack(side="right", pady=(8, 0))

        # === КНОПКА НОВОГО ЧАТА ===
        self.new_chat_btn = ctk.CTkButton(
            self,
            text="✨  Новый чат",
            command=self.app.new_chat,
            height=50,
            corner_radius=14,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color=("#6366f1", "#6366f1"),
            hover_color=("#4f46e5", "#4f46e5"),
            anchor="center"
        )
        self.new_chat_btn.pack(fill="x", padx=20, pady=(0, 20))

        # === РАЗДЕЛИТЕЛЬ ===
        divider = ctk.CTkFrame(self, height=1, fg_color=("#e2e8f0", "#1e1e2e"))
        divider.pack(fill="x", padx=20, pady=(0, 15))

        # === ЗАГОЛОВОК ИСТОРИИ ===
        history_header = ctk.CTkFrame(self, fg_color="transparent")
        history_header.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(
            history_header,
            text="📁 История чатов",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("gray50", "#64748b")
        ).pack(side="left")

        # === СПИСОК ЧАТОВ ===
        self.chats_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=("#c7d2fe", "#4338ca"),
            scrollbar_button_hover_color=("#a5b4fc", "#6366f1")
        )
        self.chats_scroll.pack(fill="both", expand=True, padx=10, pady=5)

        # === НИЖНЯЯ ПАНЕЛЬ ===
        bottom_frame = ctk.CTkFrame(
            self,
            fg_color=("#f1f5f9", "#1e1e2e"),
            corner_radius=0
        )
        bottom_frame.pack(fill="x", side="bottom")

        # Кнопка настроек
        settings_btn = ctk.CTkButton(
            bottom_frame,
            text="⚙️  Настройки",
            command=self.app.open_settings,
            fg_color="transparent",
            hover_color=("#e2e8f0", "#252542"),
            border_width=0,
            height=50,
            corner_radius=0,
            font=ctk.CTkFont(size=14),
            text_color=("gray40", "#94a3b8"),
            anchor="center"
        )
        settings_btn.pack(fill="x")

        # Экспорт
        export_btn = ctk.CTkButton(
            bottom_frame,
            text="📥  Экспорт чата",
            command=self.app.export_chat,
            fg_color="transparent",
            hover_color=("#e2e8f0", "#252542"),
            border_width=0,
            height=50,
            corner_radius=0,
            font=ctk.CTkFont(size=14),
            text_color=("gray40", "#94a3b8"),
            anchor="center"
        )
        export_btn.pack(fill="x")

    def refresh_chats(self, chats: list, current_id: int = None):
        """Обновить список чатов"""
        for widget in self.chats_scroll.winfo_children():
            widget.destroy()
        self.chat_buttons.clear()

        if not chats:
            empty_label = ctk.CTkLabel(
                self.chats_scroll,
                text="Нет сохранённых чатов",
                font=ctk.CTkFont(size=12),
                text_color=("gray50", "#64748b")
            )
            empty_label.pack(pady=40)
            return

        for chat in chats:
            chat_id, title, created, updated, model = chat
            is_active = chat_id == current_id

            # Контейнер чата
            if is_active:
                chat_fg = ("#e0e7ff", "#312e81")
            else:
                chat_fg = "transparent"

            chat_frame = ctk.CTkFrame(
                self.chats_scroll,
                fg_color=chat_fg,
                corner_radius=12,
                height=60
            )
            chat_frame.pack(fill="x", pady=3, padx=5)
            chat_frame.pack_propagate(False)

            # Иконка чата
            if is_active:
                icon_fg = ("#6366f1", "#6366f1")
            else:
                icon_fg = ("#f1f5f9", "#252542")

            icon_frame = ctk.CTkFrame(
                chat_frame,
                width=36,
                height=36,
                corner_radius=10,
                fg_color=icon_fg
            )
            icon_frame.pack(side="left", padx=(10, 8), pady=12)
            icon_frame.pack_propagate(False)

            ctk.CTkLabel(
                icon_frame,
                text="💬",
                font=ctk.CTkFont(size=14)
            ).place(relx=0.5, rely=0.5, anchor="center")

            # Текст чата
            text_frame = ctk.CTkFrame(chat_frame, fg_color="transparent")
            text_frame.pack(side="left", fill="both", expand=True, pady=10)

            # Название
            title_text = title[:22] + "..." if len(title) > 22 else title

            if is_active:
                title_color = ("#4338ca", "#c7d2fe")
                title_weight = "bold"
            else:
                title_color = ("gray20", "#e2e8f0")
                title_weight = "normal"

            # ИСПРАВЛЕНО: убрал hover_color="transparent"
            title_btn = ctk.CTkButton(
                text_frame,
                text=title_text,
                command=lambda cid=chat_id: self.app.load_chat(cid),
                fg_color="transparent",
                hover_color=("#e2e8f0", "#3b3b5c"),  # Реальный цвет вместо transparent
                text_color=title_color,
                anchor="w",
                height=20,
                font=ctk.CTkFont(size=13, weight=title_weight)
            )
            title_btn.pack(fill="x")

            # Время
            try:
                time_str = datetime.fromisoformat(str(updated)).strftime("%d.%m %H:%M")
            except:
                time_str = "—"

            ctk.CTkLabel(
                text_frame,
                text=time_str,
                font=ctk.CTkFont(size=10),
                text_color=("gray50", "#64748b"),
                anchor="w"
            ).pack(fill="x")

            # Кнопка удаления
            del_btn = ctk.CTkButton(
                chat_frame,
                text="✕",
                width=28,
                height=28,
                corner_radius=8,
                fg_color="transparent",
                hover_color=("#fecaca", "#7f1d1d"),
                text_color=("gray40", "#94a3b8"),
                font=ctk.CTkFont(size=12),
                command=lambda cid=chat_id: self.app.delete_chat(cid)
            )
            del_btn.pack(side="right", padx=8)

            self.chat_buttons[chat_id] = chat_frame