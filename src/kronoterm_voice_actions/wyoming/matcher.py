import re
import json
import os
from typing import Protocol, Dict, List, Any
from dataclasses import dataclass

from homeassistant.core import HomeAssistant
from rapidfuzz import process, fuzz
from unidecode import unidecode
from .client import KronotermCloudApi

_HERE = os.path.dirname(__file__)
_COMMANDS_CONFIG = os.path.join(_HERE, "commands_config.json")

class KronotermAction(Protocol):
    action_label: str
    parameters: Dict[str, Any]

@dataclass
class KronotermActionImpl:
    action_label: str
    parameters: Dict[str, Any]

# original tables
_RAW_UNIT_WORDS = {
    "nič": 0, "ena": 1, "dva": 2, "tri": 3, "štiri": 4, "pet": 5,
    "šest": 6, "sedem": 7, "osem": 8, "devet": 9,
    "deset": 10, "enajst": 11, "dvanajst": 12, "trinajst": 13,
    "štirinajst": 14, "petnajst": 15, "šestnajst": 16, "sedemnajst": 17,
    "osemnajst": 18, "devetnajst": 19
}
_RAW_TENS_WORDS = {
    "dvajset": 20, "trideset": 30, "štirideset": 40,
    "petdeset": 50, "šestdeset": 60, "sedemdeset": 70,
    "osemdeset": 80, "devetdeset": 90
}

# 1) normalize keys to ASCII
_UNIT_WORDS = {unidecode(k): v for k, v in _RAW_UNIT_WORDS.items()}
_TENS_WORDS = {unidecode(k): v for k, v in _RAW_TENS_WORDS.items()}
_ALL_NUM_WORDS = {**_UNIT_WORDS, **_TENS_WORDS}

def parse_slovene_number(text: str) -> int:
    text = unidecode(text.strip().lower())
    if not text:
        raise ValueError("Empty number text")

    # 2) split on ANY 'in' substring for compounds (catches both spaced & concatenated)
    if "in" in text:
        left, right = text.split("in", 1)
        try:
            return parse_slovene_number(left) + parse_slovene_number(right)
        except ValueError:
            pass

    # 3) pure digits
    if text.isdigit():
        return int(text)

    # 4) exact lookup (units & tens)
    if text in _ALL_NUM_WORDS:
        return _ALL_NUM_WORDS[text]

    # 5) tens+unit prefix, e.g. "sestdesetsest"
    for ten_word, ten_val in _TENS_WORDS.items():
        if text.startswith(ten_word):
            suffix = text[len(ten_word):].strip()
            try:
                return ten_val + parse_slovene_number(suffix)
            except ValueError:
                pass

    # 6) unit+tens suffix, e.g. "sestindvajset"
    for ten_word, ten_val in _TENS_WORDS.items():
        if text.endswith(ten_word):
            prefix = text[:-len(ten_word)].strip()
            try:
                return ten_val + parse_slovene_number(prefix)
            except ValueError:
                pass

    # 7) fuzzy fallback for minor ASR typos
    best, score, _ = process.extractOne(text, _ALL_NUM_WORDS.keys(), scorer=fuzz.partial_ratio)
    if score >= 80:
        return _ALL_NUM_WORDS[best]

    # 8) digits anywhere
    m = re.search(r"(\d+)", text)
    if m:
        return int(m.group(1))

    raise ValueError(f"Cannot parse number from '{text}'")

class _CmdTemplate:
    __slots__ = ("template","action","slot_names","fixed","regex")
    def __init__(self, tpl: str, action: str):
        self.template   = tpl
        self.action     = action
        # slots are hard-coded in JSON (e.g. <value>), loop numbers are literal words
        self.slot_names = re.findall(r"<(\w+)>", tpl)
        # remove slots for fuzzy matching
        self.fixed = re.sub(r"<\w+>", "", tpl).strip().lower()
        # build a regex that captures each <slot>
        pat = re.escape(tpl.lower())
        pat = re.sub(r"\\ ", r"\\s+", pat)
        for name in self.slot_names:
            pat = pat.replace(
                re.escape(f"<{name}>"),
                rf"(?P<{name}>[\wčšž\s]+?)"
            )
        self.regex = re.compile(rf"^{pat}$", re.IGNORECASE)

class KronotermParser:
    def __init__(self, json_path: str):
        with open(json_path, encoding='utf-8') as f:
            data = json.load(f)
        self._templates: List[_CmdTemplate] = [
            _CmdTemplate(c['template'], c['action'])
            for c in data.get('commands', [])
        ]

    def _normalize(self, text: str) -> str:
        text = text.lower()
        # drop punctuation except Slovene chars
        text = re.sub(r"[^\w\sčšž]", " ", text)
        # remove common ASR fillers
        text = re.sub(r"\b(um+|ahm+|eee+|please|prosim|hej)\b", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    def parse(self, transcription: str, threshold: int = 70) -> KronotermAction:
        clean = self._normalize(transcription)
        # pick best template by fuzzy match on fixed parts
        mapping = {tpl.fixed: tpl for tpl in self._templates}
        best_fixed, score, _ = process.extractOne(clean, mapping.keys(), scorer=fuzz.partial_ratio)
        if score < threshold:
            raise ValueError(f"No command matches '{transcription}' (best score={score})")
        cmd = mapping[best_fixed]

        # extract slots
        match = cmd.regex.match(clean)
        params: Dict[str, Any] = {}
        if match:
            for name, raw in match.groupdict().items():
                raw = raw.strip()
                try:
                    params[name] = parse_slovene_number(raw)
                except ValueError:
                    params[name] = raw
        else:
            # fallback: assign last token to any slot
            last = clean.split()[-1]
            for name in cmd.slot_names:
                try:
                    params[name] = parse_slovene_number(last)
                except ValueError:
                    params[name] = last

        return KronotermActionImpl(action_label=cmd.action, parameters=params)


async def execute_command(text: str, username: str, password: str, hass: HomeAssistant) -> str:
    parser = KronotermParser(_COMMANDS_CONFIG)
    action = parser.parse(text)
    api = KronotermCloudApi(username, password, hass)
    return await api.invoke_kronoterm_action(action)
