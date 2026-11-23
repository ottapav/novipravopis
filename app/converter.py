"""Nové pravopisné pravidlo.

Po obojetných souhláskách (b, f, l, m, p, s, v, z) se píše měkké i/í místo y/ý.
Výjimku tvoří cizí slova (viz exceptions.py).
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, List

from .exceptions import ALLOWED_PREFIXES, FOREIGN_STEMS

AMBIVALENT = frozenset("bflmpsvz")
Y_TO_I = {"y": "i", "ý": "í", "Y": "I", "Ý": "Í"}

_STEM_SET = frozenset(FOREIGN_STEMS)
_MIN_STEM = min(len(s) for s in FOREIGN_STEMS)
_MAX_STEM = max(len(s) for s in FOREIGN_STEMS)
_PREFIXES = sorted(ALLOWED_PREFIXES, key=len, reverse=True)

# Slovo = souvislá řada písmen (bez číslic a podtržítka).
_WORD_RE = re.compile(r"[^\W\d_]+")


def _starts_with_stem(s: str) -> bool:
    for n in range(_MIN_STEM, min(len(s), _MAX_STEM) + 1):
        if s[:n] in _STEM_SET:
            return True
    return False


def is_foreign(lower: str, depth: int = 0) -> bool:
    """Je (malými písmeny zapsané) slovo cizí, tj. výjimka z pravidla?"""
    if _starts_with_stem(lower):
        return True
    if depth >= 2:
        return False
    for prefix in _PREFIXES:
        if len(lower) > len(prefix) and lower.startswith(prefix):
            if is_foreign(lower[len(prefix):], depth + 1):
                return True
    return False


def _is_candidate(chars: List[str], i: int) -> bool:
    """Je znak na pozici i y/ý hned po obojetné souhlásce?"""
    return i > 0 and chars[i] in Y_TO_I and chars[i - 1].lower() in AMBIVALENT


def _has_candidate(chars: List[str]) -> bool:
    return any(_is_candidate(chars, i) for i in range(1, len(chars)))


def convert(text: Any) -> Dict[str, Any]:
    """Převede text na nový pravopis.

    Vrací slovník:
      text      – převedený text
      segments  – výsledek po kouscích ``{"t": text, "k": druh}``, aby šla změněná
                  písmena zvýraznit; druh je ``plain``, ``changed`` (písmeno změněné
                  z y/ý na i/í) nebo ``foreign`` (cizí slovo, které by se jinak
                  měnilo, ale zůstalo – výjimka)
      stats     – ``changedLetters``, ``changedWords``, ``foreignKept``
    """
    src = unicodedata.normalize("NFC", "" if text is None else str(text))
    segments: List[Dict[str, str]] = []
    stats = {"changedLetters": 0, "changedWords": 0, "foreignKept": 0}
    out: List[str] = []

    def push(t: str, kind: str) -> None:
        if not t:
            return
        out.append(t)
        if segments and segments[-1]["k"] == kind:
            segments[-1]["t"] += t
        else:
            segments.append({"t": t, "k": kind})

    last = 0
    for m in _WORD_RE.finditer(src):
        push(src[last:m.start()], "plain")
        last = m.end()

        word = m.group(0)
        chars = list(word)

        if not _has_candidate(chars):
            push(word, "plain")
        elif is_foreign(word.lower()):
            stats["foreignKept"] += 1
            push(word, "foreign")
        else:
            changed_in_word = 0
            for i, ch in enumerate(chars):
                if _is_candidate(chars, i):
                    push(Y_TO_I[ch], "changed")
                    changed_in_word += 1
                else:
                    push(ch, "plain")
            stats["changedLetters"] += changed_in_word
            if changed_in_word:
                stats["changedWords"] += 1
    push(src[last:], "plain")

    return {"text": "".join(out), "segments": segments, "stats": stats}
