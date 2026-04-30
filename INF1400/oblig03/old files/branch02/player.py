"""Spillermodellen for Pokemon Care Simulator.

Her lagres aktiv Pokemon, farm-samlingen, items, penger og badges.
"""

from pokemon import Pokemon

class Player:
    def __init__(self, starter: Pokemon, character_name: str = "Trainer"):
        self.active_pokemon = starter
        self.pokemon_farm: list[Pokemon] = [starter]
        self.pokeballs = float("inf")
        self.character_name = character_name
        self.money = 0
        self.gym_badges: list[str] = []
        self.inventory = {
            "potion": 0,
            "revive": 0,
            "cure": 0,
        }

    def add_pokemon(self, pokemon: Pokemon):
        self.pokemon_farm.append(pokemon)

    def award_party_xp(self, amount: int, include_hospitalized: bool = False) -> int:
        if amount <= 0:
            return 0

        rewarded_count = 0
        for pokemon in self.pokemon_farm:
            if pokemon.hospitalized and not include_hospitalized:
                continue
            pokemon.gain_xp(amount)
            rewarded_count += 1
        return rewarded_count

    def add_item(self, item_name: str, amount: int = 1):
        self.inventory[item_name] = self.inventory.get(item_name, 0) + amount

    def use_item(self, item_name: str) -> bool:
        if self.inventory.get(item_name, 0) <= 0:
            return False
        self.inventory[item_name] -= 1
        return True

    def has_badge(self, badge_name: str) -> bool:
        return badge_name in self.gym_badges

    def award_badge(self, badge_name: str) -> bool:
        if self.has_badge(badge_name):
            return False
        self.gym_badges.append(badge_name)
        return True

    # Hjelpefunksjoner for lagring og lasting.
    def to_dict(self):
        return {
            "active_index": self.pokemon_farm.index(self.active_pokemon),
            "pokemon_farm": [p.to_dict() for p in self.pokemon_farm],
            "character_name": self.character_name,
            "money": self.money,
            "gym_badges": self.gym_badges,
            "inventory": self.inventory,
        }
    @staticmethod
    def from_dict(data):
        from pokemon import Pokemon

        farm = [Pokemon.from_dict(p) for p in data["pokemon_farm"]]
        player = Player(farm[data["active_index"]], data.get("character_name", "Trainer"))
        player.pokemon_farm = farm
        player.money = data.get("money", 0)
        player.gym_badges = data.get("gym_badges", [])
        player.inventory = data.get(
            "inventory",
            {
                "potion": 0,
                "revive": 0,
                "cure": 0,
            },
        )
        return player
