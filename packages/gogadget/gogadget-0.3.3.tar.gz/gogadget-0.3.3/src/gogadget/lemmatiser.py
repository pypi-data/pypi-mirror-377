__author__ = "Jonathan Fox"
__copyright__ = "Copyright 2024, Jonathan Fox"
__license__ = "GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html"
__full_source_code__ = "https://github.com/jonathanfox5/gogadget"

from lemon_tizer import LemonTizer

from .help_text import SupportedLanguages


def lemma_dummy(language: str) -> None:
    """Function to initialise the lemmatiser on first run and download the required modules"""
    lt = LemonTizer(language, "lg")
    lt.lemmatize_sentence("Wololo")


def language_supported(language: str) -> bool:
    """Check if the language is supported.
    LemonTizer has its own function that is more accurate but this works offline."""

    supported = language in SupportedLanguages.spacy_languages.keys()
    return supported
