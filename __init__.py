from aqt import mw
from aqt.utils import showInfo, qconnect
from aqt.qt import *
import os
import re
from typing import Set
from functools import lru_cache

HTML_PATTERN = re.compile(r'<.*?>')
KANJI_PATTERN = re.compile(r'[一-龠]')

@lru_cache(maxsize=1)
def read_joyo_kanji() -> Set[str]:
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kanji.txt')
    with open(file_path, 'r', encoding='utf-8') as file:
        return set(file.read().split())

def clear_html_tags(raw_question: str) -> str:
    return HTML_PATTERN.sub('', raw_question).split('\n')[-1]

def get_kanji_from_cards() -> Set[str]:
    kanji_set = set()
    cards = mw.col.find_cards("")
    for card_id in cards:
        question = mw.col.get_card(card_id).question()
        cleaned_text = clear_html_tags(question)
        kanji_set.update(ch for ch in cleaned_text if KANJI_PATTERN.match(ch))
    return kanji_set

def main() -> None:
    try:
        deck_kanji = get_kanji_from_cards()
        joyo_kanji = read_joyo_kanji()
        
        missing_kanji = joyo_kanji - deck_kanji
        missing_count = len(missing_kanji)
        
        report = [
            f"Missing Jōyō Kanji: {missing_count}",
            f"Total unique kanji in deck: {len(deck_kanji)}",
            f"Coverage: {((len(joyo_kanji) - missing_count) / len(joyo_kanji) * 100):.1f}%"
        ]
        
        showInfo("\n".join(report))
        
    except Exception as e:
        showInfo(f"Error checking kanji: {str(e)}")

action = QAction("Check missing Jōyō Kanji", mw)
qconnect(action.triggered, main)
mw.form.menuTools.addAction(action)