import customtkinter as ctk
from config import Config


class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent, settings: dict, on_save):
        super().__init__(parent)
        self.settings = settings.copy()
        self.on_save = on_save

        self.title("⚙️ Настройки")
        self.geometry("550x700")
        self.resizable(False, False)

        # Центрирование
        self.transient(parent)
        self.grab_set()

        # Цвет фона
        self.configure(fg_color=("#f8fafc", "#12121f"))

        self.setup_ui()

    def setup_ui(self):
        # Заголовок
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 20))

        ctk.CTkLabel(
            header,
            text="⚙️ Настройки",
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
            text_color=("gray10", "#e2e8f0")
        ).pack(side="left")

        # Скролл область
        main_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=("#c7d2fe", "#4338ca")
        )
        main_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # === API KEY ===
        self._create_section(main_frame, "🔑 API Ключ")

        api_container = ctk.CTkFrame(
            main_frame,
            fg_color=("white", "#1e1e2e"),
            corner_radius=12,
            border_width=1,
            border_color=("#e2e8f0", "#374151")
        )
        api_container.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            api_container,
            text="Получите бесплатный ключ на openrouter.ai/keys",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "#64748b")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.api_key_entry = ctk.CTkEntry(
            api_container,
            placeholder_text="sk-or-v1-...",
            show="•",
            height=45,
            corner_radius=10,
            border_width=0,
            fg_color=("#f8fafc", "#12121f"),
            font=ctk.CTkFont(size=14)
        )
        self.api_key_entry.pack(fill="x", padx=15, pady=(0, 15))
        self.api_key_entry.insert(0, self.settings.get("api_key", ""))

        # === МОДЕЛЬ ===
        self._create_section(main_frame, "🤖 Модель AI")

        model_container = ctk.CTkFrame(
            main_frame,
            fg_color=("white", "#1e1e2e"),
            corner_radius=12,
            border_width=1,
            border_color=("#e2e8f0", "#374151")
        )
        model_container.pack(fill="x", pady=(0, 20))

        self.model_var = ctk.StringVar(value=self.settings.get("model", ""))

        for i, (name, model_id) in enumerate(Config.FREE_MODELS.items()):
            is_selected = self.model_var.get() == model_id

            model_btn = ctk.CTkRadioButton(
                model_container,
                text=f"  {name}",
                variable=self.model_var,
                value=model_id,
                font=ctk.CTkFont(size=14),
                fg_color="#6366f1",
                hover_color="#4f46e5",
                border_color=("#d1d5db", "#4b5563")
            )
            model_btn.pack(anchor="w", padx=15, pady=10)

        # === SYSTEM PROMPT ===
        self._create_section(main_frame, "📝 Системный промпт")

        prompt_container = ctk.CTkFrame(
            main_frame,
            fg_color=("white", "#1e1e2e"),
            corner_radius=12,
            border_width=1,
            border_color=("#e2e8f0", "#374151")
        )
        prompt_container.pack(fill="x", pady=(0, 20))

        self.system_prompt_text = ctk.CTkTextbox(
            prompt_container,
            height=100,
            corner_radius=10,
            border_width=0,
            fg_color=("#f8fafc", "#12121f"),
            font=ctk.CTkFont(size=13)
        )
        self.system_prompt_text.pack(fill="x", padx=15, pady=15)
        self.system_prompt_text.insert("1.0", self.settings.get("system_prompt", ""))

        # === ТЕМПЕРАТУРА ===
        self._create_section(main_frame, "🌡️ Температура (креативность)")

        temp_container = ctk.CTkFrame(
            main_frame,
            fg_color=("white", "#1e1e2e"),
            corner_radius=12,
            border_width=1,
            border_color=("#e2e8f0", "#374151")
        )
        temp_container.pack(fill="x", pady=(0, 20))

        temp_header = ctk.CTkFrame(temp_container, fg_color="transparent")
        temp_header.pack(fill="x", padx=15, pady=(15, 10))

        ctk.CTkLabel(
            temp_header,
            text="Низкая = точность, Высокая = креативность",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "#64748b")
        ).pack(side="left")

        self.temp_label = ctk.CTkLabel(
            temp_header,
            text=f"{self.settings.get('temperature', 0.7)}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#6366f1", "#a5b4fc")
        )
        self.temp_label.pack(side="right")

        self.temp_slider = ctk.CTkSlider(
            temp_container,
            from_=0,
            to=2,
            number_of_steps=20,
            command=self.update_temp_label,
            button_color="#6366f1",
            button_hover_color="#4f46e5",
            progress_color="#6366f1"
        )
        self.temp_slider.set(self.settings.get("temperature", 0.7))
        self.temp_slider.pack(fill="x", padx=15, pady=(0, 15))

        # === ТЕМА ===
        self._create_section(main_frame, "🎨 Тема оформления")

        theme_container = ctk.CTkFrame(
            main_frame,
            fg_color=("white", "#1e1e2e"),
            corner_radius=12,
            border_width=1,
            border_color=("#e2e8f0", "#374151")
        )
        theme_container.pack(fill="x", pady=(0, 20))

        self.theme_var = ctk.StringVar(value=self.settings.get("theme", "dark"))

        theme_inner = ctk.CTkFrame(theme_container, fg_color="transparent")
        theme_inner.pack(fill="x", padx=15, pady=15)

        themes = [
            ("🌙 Тёмная", "dark"),
            ("☀️ Светлая", "light"),
            ("💻 Системная", "system")
        ]

        for text, value in themes:
            ctk.CTkRadioButton(
                theme_inner,
                text=f"  {text}",
                variable=self.theme_var,
                value=value,
                font=ctk.CTkFont(size=14),
                fg_color="#6366f1",
                hover_color="#4f46e5",
                border_color=("#d1d5db", "#4b5563")
            ).pack(side="left", padx=(0, 25))

        # === КНОПКИ ===
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=(0, 30))

        ctk.CTkButton(
            btn_frame,
            text="Отмена",
            command=self.destroy,
            fg_color="transparent",
            hover_color=("#e2e8f0", "#374151"),
            border_width=2,
            border_color=("#d1d5db", "#4b5563"),
            text_color=("gray40", "#94a3b8"),
            width=120,
            height=45,
            corner_radius=12,
            font=ctk.CTkFont(size=14)
        ).pack(side="left")

        ctk.CTkButton(
            btn_frame,
            text="💾 Сохранить",
            command=self.save,
            fg_color="#6366f1",
            hover_color="#4f46e5",
            width=150,
            height=45,
            corner_radius=12,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="right")

    def _create_section(self, parent, title):
        """Создать заголовок секции"""
        ctk.CTkLabel(
            parent,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("gray30", "#e2e8f0")
        ).pack(anchor="w", pady=(10, 8))

    def update_temp_label(self, value):
        self.temp_label.configure(text=f"{value:.1f}")

    def save(self):
        self.settings["api_key"] = self.api_key_entry.get().strip()
        self.settings["model"] = self.model_var.get()
        self.settings["system_prompt"] = self.system_prompt_text.get("1.0", "end-1c")
        self.settings["temperature"] = round(self.temp_slider.get(), 1)
        self.settings["theme"] = self.theme_var.get()

        self.on_save(self.settings)
        self.destroy()