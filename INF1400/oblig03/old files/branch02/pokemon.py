"""Modellene for Pokemon, statistikk, behov og evolusjon.

Denne modulen samler de viktigste klassene som beskriver hvordan en
Pokemon oppfører seg i farmen og i kamp.
"""

from enum import Enum, auto
import random
import pygame
import math
from data import Species, POKEMON_DATA


EVOLUTION_LEVELS = {
    Species.BULBASAUR: 10,
    Species.IVYSAUR: 20,
    Species.CHARMANDER: 10,
    Species.CHARMELEON: 20,
    Species.SQUIRTLE: 10,
    Species.WARTORTLE: 20,
    Species.PIDGEY: 8,
    Species.PIDGEOTTO: 18,
    Species.PIKACHU: 10,
    Species.STARYU: 10,
    Species.GASTLY: 16,
    Species.HAUNTER: 28,
    Species.VULPIX: 10,
    Species.DRATINI: 12,
    Species.EEVEE: 10,
}

EVOLUTION_MAP = {
    Species.BULBASAUR: Species.IVYSAUR,
    Species.IVYSAUR: Species.VENUSAUR,
    Species.CHARMANDER: Species.CHARMELEON,
    Species.CHARMELEON: Species.CHARIZARD,
    Species.SQUIRTLE: Species.WARTORTLE,
    Species.WARTORTLE: Species.BLASTOISE,
    Species.PIDGEY: Species.PIDGEOTTO,
    Species.PIDGEOTTO: Species.PIDGEOT,
    Species.PIKACHU: Species.RAICHU,
    Species.STARYU: Species.STARMIE,
    Species.GASTLY: Species.HAUNTER,
    Species.HAUNTER: Species.GENGAR,
    Species.VULPIX: Species.NINETALES,
    Species.DRATINI: Species.DRAGONAIR,
}

class Stats:
    def __init__(self, hp, attack, defense, speed, agility=0, evade=0):
        self.max_hp = hp
        self.current_hp = hp
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.agility = agility
        self.evade = evade

    def apply_need_boost(self, boost_factor: float):
        """Boost stats when needs are satisfied."""
        self.attack_boosted = int(self.attack * boost_factor)
        self.defense_boosted = int(self.defense * boost_factor)
        self.speed_boosted = int(self.speed * boost_factor)
        # you can also boost agility/evade similarly
    
    # Hjelpefunksjoner for lagring og lasting.
    def to_dict(self):
        return {
        "max_hp": self.max_hp,
        "current_hp": self.current_hp,
        "attack": self.attack,
        "defense": self.defense,
        "speed": self.speed,
        "agility": self.agility,
        "evade": self.evade,
        }
    @staticmethod
    def from_dict(data):
        s = Stats(
            hp=data["max_hp"],
            attack=data["attack"],
            defense=data["defense"],
            speed=data["speed"],
            agility=data.get("agility", 0),
            evade=data.get("evade", 0),
        )
        s.current_hp = data["current_hp"]
        return s
class Needs:
    def __init__(self):
        self.hunger = 100
        self.happiness = 100
        self.energy = 100
        self.social = 100

    def decay(self, dt: float):
        """dt = time delta in seconds or ticks."""
        self.hunger -= 0.5 * dt
        self.happiness -= 0.3 * dt
        self.energy -= 0.4 * dt
        self.social -= 0.2 * dt
        self._clamp()

    def _clamp(self):
        for attr in ("hunger", "happiness", "energy", "social"):
            value = getattr(self, attr)
            setattr(self, attr, max(0, min(100, value)))

    def is_satisfied(self) -> bool:
        return (
            self.hunger > 70 and
            self.happiness > 70 and
            self.energy > 70 and
            self.social > 70
        )

    def average(self) -> float:
        return (self.hunger + self.happiness + self.energy + self.social) / 4

    def is_critical(self) -> bool:
        return min(self.hunger, self.happiness, self.energy, self.social) <= 0

    def needs_attention(self) -> bool:
        return min(self.hunger, self.happiness, self.energy, self.social) <= 25
    
    # Hjelpefunksjoner for lagring og lasting.
    def to_dict(self):
        return {
        "hunger": self.hunger,
        "happiness": self.happiness,
        "energy": self.energy,
        "social": self.social,
        }
    @staticmethod
    def from_dict(data):
        n = Needs()
        n.hunger = data["hunger"]
        n.happiness = data["happiness"]
        n.energy = data["energy"]
        n.social = data["social"]
        return n
    


class Pokemon:
    def __init__(self, species: Species, level: int = 1):
        self.species = species
        data = POKEMON_DATA[species]
        self.type = data["type"]
        self.level = level
        self.xp = 0
        self.needs = Needs()
        self.stats = Stats(
            hp=data["base_hp"] + level * 5,
            attack=data["base_attack"] + level * 2,
            defense=data["base_defense"] + level * 2,
            speed=data["base_speed"] + level * 1,
            agility=data.get("base_agility", 0),
            evade=data.get("base_evade", 0),
        )
        self.anim_time = 0
        self.anim_offset = 0
        self.shake_timer = 0
        self.shake_offset = 0
        self.hp_shake_timer = 0
        self.hp_shake_offset = 0
        self.flash_timer = 0
        self.flash_alpha = 0
        self.crit = False
        self.display_xp = 0
        self.evolving = False
        self.evo_timer = 0
        self.evo_scale = 1.0
        self.pending_evolution = None
        self.display_hp = self.stats.current_hp
        self.hospitalized = False
        self.hospital_reason = ""

    
    def update_display_hp(self, dt):
        """Jevn ut visningen av HP-baren mot den faktiske HP-verdien."""
        speed = 60
        if self.display_hp < self.stats.current_hp:
            self.display_hp = min(self.stats.current_hp, self.display_hp + speed * dt)
        elif self.display_hp > self.stats.current_hp:
            self.display_hp = max(self.stats.current_hp, self.display_hp - speed * dt)

    def animate(self, dt):
        self.anim_time += dt
        self.anim_offset = int(5 * math.sin(self.anim_time * 3))

        if self.shake_timer > 0:
            self.shake_timer -= dt
            self.shake_offset = int(5 * math.sin(self.anim_time * 20))
        else:
            self.shake_offset = 0

        # HP-linjen rister kort når Pokemonen tar skade.
        if self.hp_shake_timer > 0:
            self.hp_shake_timer -= dt
            self.hp_shake_offset = int(3 * math.sin(self.anim_time * 40))
        else:
            self.hp_shake_offset = 0

        # Et hvitt blink gjør at treff blir lettere å se.
        if self.flash_timer > 0:
            self.flash_timer -= dt
            self.flash_alpha = 255 if int(self.flash_timer * 20) % 2 == 0 else 0
        else:
            self.flash_alpha = 0

        # Erfaring teller jevnt opp i UI i stedet for å hoppe direkte.
        if hasattr(self, "xp_target"):
            if self.display_xp < self.xp_target:
                self.display_xp += dt * 40
                if self.display_xp > self.xp_target:
                    self.display_xp = self.xp_target

        if self.evolving:
            self.evo_timer -= dt
            self.evo_scale = 1.0 + 0.22 * math.sin(self.anim_time * 18)
            self.flash_alpha = 170 if int(self.anim_time * 16) % 2 == 0 else 70
            if self.evo_timer <= 0:
                target_species = self.pending_evolution
                self.evolving = False
                self.evo_timer = 0
                self.evo_scale = 1.0
                self.flash_alpha = 0
                self.pending_evolution = None
                if target_species is not None:
                    self.evolve(target_species)


    def tick(self, dt: float):
        """Oppdater behov, helse og passiv erfaring for Pokemonen."""
        if self.hospitalized:
            return

        self.needs.decay(dt)
        self.apply_passive_health(dt)
        if self.needs.is_satisfied():
            self.stats.apply_need_boost(1.2)
            self.gain_xp(int(2 * dt))
        else:
            self.stats.apply_need_boost(1.0)
            self.gain_xp(int(1 * dt))

    def apply_passive_health(self, dt: float):
        if self.stats.current_hp <= 0:
            return

        if self.needs.is_satisfied():
            self.stats.current_hp = min(self.stats.max_hp, self.stats.current_hp + 2.4 * dt)
        elif self.needs.average() >= 55:
            self.stats.current_hp = min(self.stats.max_hp, self.stats.current_hp + 0.9 * dt)

        if self.needs.is_critical():
            neglect_damage = max(1.5, self.stats.max_hp * 0.045) * dt
            self.stats.current_hp = max(0, self.stats.current_hp - neglect_damage)
            if self.stats.current_hp <= 0:
                self.send_to_hospital("This Pokémon was not treated in time.")

    def send_to_hospital(self, reason: str = "This Pokémon needs a revive."):
        self.stats.current_hp = 0
        self.display_hp = 0
        self.hospitalized = True
        self.hospital_reason = reason

    def revive_from_hospital(self):
        self.hospitalized = False
        self.hospital_reason = ""
        self.stats.current_hp = max(1, self.stats.max_hp // 2)
        self.display_hp = self.stats.current_hp

    # --- interactions ---
    def feed(self, amount: int = 20):
        if self.hospitalized:
            return
        self.needs.hunger = min(100, self.needs.hunger + amount)

    def pet(self, amount: int = 15):
        if self.hospitalized:
            return
        self.needs.happiness = min(100, self.needs.happiness + amount)
        self.needs.social = min(100, self.needs.social + 10)

    def walk(self, duration: float):
        if self.hospitalized:
            return
        self.needs.social = min(100, self.needs.social + duration * 5)
        self.needs.energy = max(0, self.needs.energy - duration * 3)

    def sleep(self, duration: float):
        if self.hospitalized:
            return
        self.needs.energy = min(100, self.needs.energy + duration * 10)

    # --- battle / XP ---
    def take_damage(self, dmg: int):
        if self.hospitalized:
            return
        self.stats.current_hp = max(0, self.stats.current_hp - dmg)
        self.hp_shake_timer = 0.25  # quarter-second shake
        self.flash_timer = 0.15  # flash for 150ms

    def is_fainted(self) -> bool:
        return self.stats.current_hp <= 0

    def gain_xp(self, amount: int):
        self.xp += amount
        # XP animation target
        self.xp_target = self.xp
        while self.xp >= self.xp_to_next_level():
            self.xp -= self.xp_to_next_level()
            self.level_up()

    def xp_to_next_level(self) -> int:
        return 50 + (self.level - 1) * 25

    def level_up(self):
        self.level += 1
        self.stats.max_hp += 5
        self.stats.attack += 2
        self.stats.defense += 2
        self.stats.speed += 1
        self.stats.current_hp = self.stats.max_hp
        self.hospitalized = False
        self.hospital_reason = ""
        self.try_evolve()

    def try_evolve(self):
        target_species = self.next_evolution_species()
        if target_species is not None and self.can_evolve():
            self.evolve(target_species)

    def next_evolution_species(self):
        if self.species == Species.EEVEE:
            return random.choice([Species.JOLTEON, Species.VAPOREON, Species.FLAREON])
        return EVOLUTION_MAP.get(self.species)

    def can_evolve(self, ignore_level: bool = False) -> bool:
        target_species = self.next_evolution_species()
        if target_species is None or self.evolving or self.hospitalized:
            return False
        if ignore_level:
            return True
        required_level = EVOLUTION_LEVELS.get(self.species)
        if required_level is None:
            return False
        return self.level >= required_level

    def start_evolution_animation(self, force: bool = False) -> bool:
        target_species = self.next_evolution_species()
        if target_species is None or not self.can_evolve(ignore_level=force):
            return False

        self.pending_evolution = target_species
        self.evolving = True
        self.evo_timer = 2.2
        self.evo_scale = 1.0
        return True

    def evolve(self, new_species: Species):
        print(f"{self.species.name} evolved into {new_species.name}!")
        self.species = new_species
        data = POKEMON_DATA[new_species]
        self.type = data["type"]
        self.evolving = False
        self.pending_evolution = None
        self.evo_timer = 0
        self.evo_scale = 1.0
        # optionally re-scale stats
        self.stats.max_hp = data["base_hp"] + self.level * 5
        self.stats.current_hp = self.stats.max_hp
        self.hospitalized = False
        self.hospital_reason = ""
    # For save/load functionality, we can convert the whole Pokemon to/from a dictionary:
    def to_dict(self):
        return {
            "species": self.species.name,
            "level": self.level,
            "xp": self.xp,
            "display_xp": self.display_xp,
            "stats": self.stats.to_dict(),
            "needs": self.needs.to_dict(),
            "hospitalized": self.hospitalized,
            "hospital_reason": self.hospital_reason,
        }
    @staticmethod
    def from_dict(data):
        from data import Species  # avoid circular import

        species = Species[data["species"]]
        p = Pokemon(species, level=data["level"])
        p.xp = data["xp"]
        p.display_xp = data.get("display_xp", p.xp)
        p.stats = Stats.from_dict(data["stats"])
        p.needs = Needs.from_dict(data["needs"])
        p.hospitalized = data.get("hospitalized", False)
        p.hospital_reason = data.get("hospital_reason", "")
        p.display_hp = p.stats.current_hp
        return p


