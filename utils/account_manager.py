import json
import os
from typing import List, Optional, Dict


class AccountManager:
    """Gestor simple de cuentas GitHub.
    Nota: ya no se almacenan tokens; solo alias y username para poder hacer switch con 'gh'.
    Archivo: %USERPROFILE%/.bulletuploader/accounts.json
    Estructura: [{"name": "alias", "username": "usuario"}]
    """

    def __init__(self):
        home = os.path.expanduser("~")
        self.dir = os.path.join(home, ".bulletuploader")
        self.path = os.path.join(self.dir, "accounts.json")
        os.makedirs(self.dir, exist_ok=True)

    def load(self) -> List[Dict[str, str]]:
        if not os.path.exists(self.path):
            return []
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                return []
        except Exception:
            return []

    def save(self, accounts: List[Dict[str, str]]):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(accounts, f, ensure_ascii=False, indent=2)

    def add(self, name: str, username: Optional[str] = None):
        accounts = self.load()
        # Reemplazar si existe mismo alias
        accounts = [a for a in accounts if a.get("name") != name]
        entry = {"name": name}
        if username:
            entry["username"] = username
        accounts.append(entry)
        self.save(accounts)

    def remove(self, name: str):
        accounts = [a for a in self.load() if a.get("name") != name]
        self.save(accounts)

    def list_accounts(self) -> List[Dict[str, str]]:
        return self.load()

    def get_username(self, name: str) -> Optional[str]:
        for a in self.load():
            if a.get("name") == name:
                return a.get("username") or a.get("name")
        return None
