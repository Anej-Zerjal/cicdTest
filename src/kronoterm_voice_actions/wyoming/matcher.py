import re
import os
from typing import Dict, List, Any, Iterable

from rapidfuzz import process, fuzz
from unidecode import unidecode

from .kronoterm_models import KronotermAction
from .mqtt_client import MqttClient

_HERE = os.path.dirname(__file__)

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

_UNIT_WORDS = {unidecode(k): v for k, v in _RAW_UNIT_WORDS.items()}
_TENS_WORDS = {unidecode(k): v for k, v in _RAW_TENS_WORDS.items()}
_ALL_NUM_WORDS = {**_UNIT_WORDS, **_TENS_WORDS}


def parse_slovene_number(text: str) -> int:
    text = unidecode(text.strip().lower())
    if not text:
        raise ValueError("Empty number text")

    if "in" in text:
        left, right = text.split("in", 1)
        try:
            return parse_slovene_number(left) + parse_slovene_number(right)
        except ValueError:
            pass

    if text.isdigit():
        return int(text)

    if text in _ALL_NUM_WORDS:
        return _ALL_NUM_WORDS[text]

    for ten_word, ten_val in _TENS_WORDS.items():
        if text.startswith(ten_word):
            suffix = text[len(ten_word):].strip()
            try:
                return ten_val + parse_slovene_number(suffix)
            except ValueError:
                pass

    for ten_word, ten_val in _TENS_WORDS.items():
        if text.endswith(ten_word):
            prefix = text[:-len(ten_word)].strip()
            try:
                return ten_val + parse_slovene_number(prefix)
            except ValueError:
                pass

    best, score, _ = process.extractOne(text, _ALL_NUM_WORDS.keys(), scorer=fuzz.partial_ratio)
    if score >= 80:
        return _ALL_NUM_WORDS[best]

    m = re.search(r"(\d+)", text)
    if m:
        return int(m.group(1))

    raise ValueError(f"Cannot parse number from '{text}'")


class _CmdTemplate:
    # 1. Removed "action" from __slots__
    __slots__ = ("template", "slot_names", "fixed", "regex")

    # 2. Modified __init__ to not take or store 'action'
    def __init__(self, tpl: str):
        self.template = tpl
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
                rf"(?P<{name}>[\wčšž\s]+?)"  # Added ČŠŽ to allow Slovene chars in slots
            )
        self.regex = re.compile(rf"^{pat}$", re.IGNORECASE)


class KronotermParser:
    def __init__(self, templates: Iterable[str]):
        self._templates: List[_CmdTemplate] = [
            _CmdTemplate(template_string)
            for template_string in templates
        ]


    def _normalize(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^\w\sčšž]", " ", text)
        text = re.sub(r"\b(um+|ahm+|eee+|please|prosim|hej)\b", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    def parse(self, transcription: str,
              threshold: int = 70) -> KronotermAction:
        clean = self._normalize(transcription)
        mapping = {tpl.fixed: tpl for tpl in self._templates}
        # Ensure mapping is not empty to prevent error with process.extractOne
        if not mapping:
            raise ValueError(f"No command templates loaded from config. Cannot parse '{transcription}'.")

        best_fixed, score, _ = process.extractOne(clean, mapping.keys(), scorer=fuzz.partial_ratio)

        if score < threshold:
            raise ValueError(f"No command matches '{transcription}' (best score={score}, threshold={threshold})")
        cmd = mapping[best_fixed]

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
            if cmd.slot_names:
                last_words = clean.split()
                potential_slot_value = clean.replace(best_fixed, "").strip()
                if not potential_slot_value and last_words:
                    potential_slot_value = last_words[-1]

                for name in cmd.slot_names:  # Assign the same potential value to all slots
                    try:
                        params[name] = parse_slovene_number(potential_slot_value)
                    except ValueError:
                        params[name] = potential_slot_value

        return KronotermAction(action=cmd.template, parameters=params)


async def execute_command(text: str) -> str:
    client = MqttClient()
    parser = KronotermParser(client.map_template_to_function.keys())
    action_obj: KronotermAction = parser.parse(text)
    return await client.invoke_kronoterm_action(action_obj)