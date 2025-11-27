import json
from datetime import datetime
from pathlib import Path


class ExportManager:

    @staticmethod
    def to_markdown(chat_title: str, messages: list) -> str:
        """Экспорт в Markdown"""
        lines = [
            f"# {chat_title}",
            f"*Exported: {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
            "",
            "---",
            ""
        ]

        for msg in messages:
            role = "👤 **User**" if msg["role"] == "user" else "🤖 **Assistant**"
            lines.append(f"## {role}")
            lines.append("")
            lines.append(msg["content"])
            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def to_json(chat_title: str, messages: list) -> str:
        """Экспорт в JSON"""
        data = {
            "title": chat_title,
            "exported_at": datetime.now().isoformat(),
            "messages": messages
        }
        return json.dumps(data, indent=2, ensure_ascii=False)

    @staticmethod
    def to_txt(chat_title: str, messages: list) -> str:
        """Экспорт в TXT"""
        lines = [
            f"Chat: {chat_title}",
            f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "=" * 50,
            ""
        ]

        for msg in messages:
            role = "USER" if msg["role"] == "user" else "ASSISTANT"
            lines.append(f"[{role}]")
            lines.append(msg["content"])
            lines.append("-" * 30)
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def save_file(content: str, filepath: Path):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)