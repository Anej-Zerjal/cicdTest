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
    __slots__ = ("template", "slot_names", "fixed", "regex")

    def __init__(self, tpl: str):
        self.template = tpl
        self.slot_names = re.findall(r"<(\w+)>", tpl)
        self.fixed = re.sub(r"<\w+>", "", tpl).strip().lower()

        pat = re.escape(tpl.lower())
        pat = re.sub(r"\\ ", r"\\s+", pat)  # Allow flexible spacing

        for name in self.slot_names:
            if name == "temperature":
                slot_pattern = r"(?P<temperature>[\d\wčšž\s]+?)"  # Keep it somewhat broad initially
            else:
                # Generic pattern for other potential future slots
                slot_pattern = rf"(?P<{name}>[\wčšž\s]+?)"

            pat = pat.replace(
                re.escape(f"<{name}>"),
                slot_pattern
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
            for name, raw_value_from_regex in match.groupdict().items():
                raw_value_from_regex = raw_value_from_regex.strip()
                if name == "temperature":
                    try:
                        cleaned_raw_value = raw_value_from_regex
                        for suffix_to_remove in [" stopinj", " stopinje", " stopinjo"]:
                            if cleaned_raw_value.lower().endswith(suffix_to_remove):
                                cleaned_raw_value = cleaned_raw_value[:-len(suffix_to_remove)].strip()
                                break  # Remove only one suffix

                        params[name] = parse_slovene_number(cleaned_raw_value)
                    except ValueError:
                        params[name] = raw_value_from_regex  # Fallback to raw if number parsing fails
                else:
                    # For other types of slots in the future
                    try:
                        # Assuming other future slots might also be numbers, or handle differently
                        params[name] = parse_slovene_number(raw_value_from_regex)
                    except ValueError:
                        params[name] = raw_value_from_regex

        return KronotermAction(action=cmd.template, parameters=params)


async def execute_command(text: str) -> str:
    client = MqttClient()
    parser = KronotermParser(client.map_template_to_function.keys())
    action_obj: KronotermAction = parser.parse(text)
    return await client.invoke_kronoterm_action(action_obj)