import html
import re


def to_telegram_html(text: str) -> str:
    escaped_text = html.escape(text)
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escaped_text, flags=re.DOTALL)
