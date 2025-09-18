"""Localization manager for handling multi-language support."""

import os
import json
import locale
import pathlib
from xodex.core.singleton import Singleton

__all__ = ("Localization", "localize")


class Localization(Singleton):
    """
    Localization manager for handling multi-language support.

    Features:
    - Loads translations from JSON files in a folder.
    - Supports fallback language.
    - Observer pattern for language change notifications.
    - Pluralization support.
    - Dynamic language switching and reload.
    """

    def __init__(self, lang=None, folder="locales", fallback_lang="en"):
        """
        Initialize the Localization manager.

        Args:
            lang (str): Language code (e.g., 'en', 'fr'). If None, auto-detects.
            folder (str): Folder containing translation JSON files.
            fallback_lang (str): Fallback language code.
        """
        self.folder = folder
        self.fallback_lang = fallback_lang
        self.translations = {}
        self.fallback_translations = {}
        self.observers = []
        if lang is None:
            lang = self.detect_language()
        self.lang = lang
        self.load_language(self.fallback_lang, fallback=True)
        self.load_language(self.lang)

    def detect_language(self):
        """
        Detect system language.

        Returns:
            str: Detected language code or fallback.
        """
        lang, _ = locale.getdefaultlocale()
        if lang:
            return lang.split("_")[0]
        return self.fallback_lang

    def load_language(self, lang, fallback=False, folder=None):
        """
        Load translations for a given language.

        Args:
            lang (str): Language code.
            fallback (bool): If True, loads as fallback translations.
        """

        if folder:
            path = os.path.join(folder, f"{lang}.json")
        else:
            path = os.path.join(self.folder, f"{lang}.json")

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if fallback:
                self.fallback_translations = data
            else:
                self.translations = data
                self.lang = lang
                self.notify_observers()
        except FileNotFoundError:
            # print(f"[Localization] File not found: {path}")
            if fallback:
                self.fallback_translations = {}
            else:
                self.translations = {}

    def set_language(self, lang):
        """
        Change the current language and reload translations.

        Args:
            lang (str): New language code.
        """
        self.load_language(lang)

    def reload(self):
        """
        Reload the current language.
        """
        self.load_language(self.lang)

    def available_languages(self):
        """
        List available language codes in the locales folder.

        Returns:
            list[str]: List of language codes.
        """
        if not os.path.isdir(self.folder):
            return []
        return [f[:-5] for f in os.listdir(self.folder) if f.endswith(".json")]

    def gettext(self, key, plural=False, **kwargs):
        """
        Get the localized string for a key, with optional pluralization and formatting.

        Args:
            key (str): Translation key.
            plural (bool, optional): For pluralization.
            **kwargs: For string formatting.

        Returns:
            str: Localized string.
        """
        entry = self.translations.get(key) or self.fallback_translations.get(key)
        if entry is None:
            return key  # Key not found

        # Pluralization: if entry is a dict with 'one'/'other' keys
        if isinstance(entry, dict):
            form = "many" if plural else "one"
            text = entry.get(form, key)
        else:
            text = entry

        # String formatting support
        if kwargs:
            try:
                text = text.format(**kwargs)
            except Exception:
                pass
        return text

    def __call__(self, key, plural=False, **kwargs):
        """
        Shortcut for gettext.
        """
        return self.gettext(key, plural, **kwargs)

    # --- Observer pattern for language change notifications ---

    def add_observer(self, callback):
        """
        Add an observer callback to be notified on language change.

        Args:
            callback (callable): Function to call on language change.
        """
        if callback not in self.observers:
            self.observers.append(callback)

    def remove_observer(self, callback):
        """
        Remove an observer callback.

        Args:
            callback (callable): Function to remove.
        """
        if callback in self.observers:
            self.observers.remove(callback)

    def notify_observers(self):
        """
        Notify all observers about a language change.
        """
        for callback in self.observers:
            try:
                callback(self.lang)
            except Exception as e:
                print(f"[Localization] Observer error: {e}")


localize = Localization()
