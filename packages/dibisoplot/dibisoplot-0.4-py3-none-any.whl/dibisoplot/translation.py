import gettext
import logging
import warnings
import os

def get_translator(
        domain: str = 'dibisoplot',
        language: str = 'en',
        locale_dir: str = None
):
    # If locale_dir is not provided, use the default path relative to this file
    if locale_dir is None:
        # Get the directory where this translation.py file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        locale_dir = os.path.join(current_dir, 'locales')
    
    # if English, using original strings
    if language == "en":
        translation = gettext.NullTranslations()
    else:
        try:
            translation = gettext.translation(domain, localedir=locale_dir, languages=[language])
        except FileNotFoundError as e:
            warnings.warn(
                f"No translation files found for {language} language. "
                "Using null translations (original English strings)."
            )
            logging.warning(e)
            translation = gettext.NullTranslations()
    return translation.gettext
