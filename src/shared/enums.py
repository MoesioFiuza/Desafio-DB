from enum import Enum


class SearchMode(str, Enum):
    TOKEN = "token"
    PHRASE = "phrase"
