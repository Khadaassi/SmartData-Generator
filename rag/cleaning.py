import re
import unicodedata

_MULTIPLE_BLANK_LINES = re.compile(r"\n{3,}")
_TRAILING_WHITESPACE = re.compile(r"[ \t]+\n")


def clean_text(raw: str) -> str:
    """Normalise un contenu de document avant découpage : encodage, espaces, lignes vides."""
    text = unicodedata.normalize("NFC", raw)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _TRAILING_WHITESPACE.sub("\n", text)
    text = _MULTIPLE_BLANK_LINES.sub("\n\n", text)
    return text.strip()
