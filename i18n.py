# i18n.py
import json, os

class I18N:
    def __init__(self, base_dir="locales", default_lang="en"):
        self.base_dir = base_dir
        self.lang = default_lang
        self.trans = {}
        self.load(self.lang)

    def load(self, lang):
        path = os.path.join(self.base_dir, f"{lang}.json")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing locale file: {path}")
        with open(path, "r", encoding="utf-8") as f:
            self.trans = json.load(f)
        self.lang = lang

    def t(self, key, **kwargs):
        cur = self.trans
        for part in key.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                cur = key
                break
        if isinstance(cur, str) and kwargs:
            try:
                return cur.format(**kwargs)
            except Exception:
                return cur
        return cur if isinstance(cur, str) else str(cur)

i18n = I18N()
