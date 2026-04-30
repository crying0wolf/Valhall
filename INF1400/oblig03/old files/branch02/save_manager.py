"""En enkel JSON-basert lagringsmodul for spillet.

Modulen tar ansvar for å skrive og lese save-filer uten ekstra logikk.
"""

import json

SAVE_FILE = "savegame.json"


class SaveManager:
    @staticmethod
    def save(data: dict, filename: str = SAVE_FILE):
        """Lagre spilldata som innrykket JSON."""
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)
        print("Game saved!")

    @staticmethod
    def load(filename: str = SAVE_FILE):
        """Last inn spilldata hvis filen finnes, ellers returner `None`."""
        try:
            with open(filename, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            print("No save file found.")
            return None