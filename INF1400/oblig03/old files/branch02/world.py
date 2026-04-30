"""Verdenslogikk for encounters, fangst og trenerkamper.

Denne modulen styrer hvilke ville Pokemon som kan dukke opp, hvordan
kamprunder fungerer, og hva som skjer når spilleren prøver å fange en
vill Pokemon.
"""

import random
import math
from pokemon import Pokemon
from data import Species, get_effectiveness_text, get_type_multiplier
from player import Player

# Alle arter kan fortsatt dukke opp som ville Pokemon, men med ulik sjeldenhet.
# Høyere nivåer og sterkere arter er sjeldnere.
WILD_SPECIES_WEIGHTS: dict[Species, int] = {
    Species.PIKACHU: 14,
    Species.CHARMANDER: 12,
    Species.SQUIRTLE: 12,
    Species.BULBASAUR: 12,
    Species.EEVEE: 12,
    Species.PIDGEY: 15,
    Species.VULPIX: 10,
    Species.STARYU: 10,
    Species.GASTLY: 9,
    Species.DRATINI: 6,
    Species.JOLTEON: 4,
    Species.VAPOREON: 4,
    Species.RAICHU: 3,
    Species.FLAREON: 3,
    Species.NINETALES: 3,
    Species.STARMIE: 3,
    Species.HAUNTER: 3,
    Species.DRAGONAIR: 3,
    Species.CHARMELEON: 3,
    Species.WARTORTLE: 3,
    Species.IVYSAUR: 3,
    Species.PIDGEOTTO: 4,
    Species.CHARIZARD: 1,
    Species.BLASTOISE: 1,
    Species.VENUSAUR: 1,
    Species.PIDGEOT: 1,
    Species.GENGAR: 1,
    Species.MOLTRES: 1,
}
ALL_WILD_SPECIES = list(WILD_SPECIES_WEIGHTS)

class Encounter:
    OPENING_WILD_DELAY = 1.9
    ATTACK_START_DELAY = 0.3
    ATTACK_LUNGE_TIME = 0.22
    ATTACK_IMPACT_HOLD = 0.14
    ATTACK_RETURN_TIME = 0.2
    ATTACK_BETWEEN_DELAY = 0.2
    PLAYER_ATTACK_VECTOR = (156.0, -70.0)
    WILD_ATTACK_VECTOR = (-156.0, 70.0)

    def __init__(
        self,
        wild_pokemon,
        player,
        encounter_kind: str = "wild",
        opponent_name: str | None = None,
        intro_text: str | None = None,
        is_gym_leader: bool = False,
    ):
        self.wild = wild_pokemon
        self.player = player
        self.player_pokemon = player.active_pokemon
        self.encounter_kind = encounter_kind
        self.opponent_name = opponent_name
        self.intro_text = intro_text
        self.intro_timer = 1.9 if intro_text else 0.0
        self.intro_active = bool(intro_text)
        self.is_gym_leader = is_gym_leader
        self.is_over = False
        self.caught = False
        self.transition = 0.0
        self.last_money_reward = 0
        self.last_xp_reward = 0
        self.catch_anim_active = False
        self.catch_anim_phase = "idle"
        self.catch_anim_timer = 0.0
        self.catch_anim_result = None
        self.catch_blinks_done = 0
        self.catch_resolution = None
        self.catch_ball_pos = (0.0, 0.0)
        self.catch_ball_visible = False
        self.catch_fog_timer = 0.0
        self.catch_ready_to_finish = False
        self.catch_escape_blinks = 3
        self.catch_flash_timer = 0.0
        self.last_effectiveness_text = ""
        self.opening_attack_pending = encounter_kind == "wild"
        self.opening_attack_delay = self.OPENING_WILD_DELAY if self.opening_attack_pending else 0.0
        self.attack_sequence_active = False
        self.attack_phase = "idle"
        self.attack_timer = 0.0
        self.attack_order: list[str] = []
        self.attack_index = 0
        self.active_attacker_side: str | None = None
        self.player_attack_offset = (0.0, 0.0)
        self.wild_attack_offset = (0.0, 0.0)
        self.turn_messages: list[str] = []

    def perform_turn(self):
        self.start_turn_sequence()

    def start_turn_sequence(self, attack_order: list[str] | None = None) -> bool:
        if self.intro_active or self.catch_anim_active or self.is_over or self.attack_sequence_active or self.opening_attack_pending:
            return False

        self.last_money_reward = 0
        self.last_xp_reward = 0
        self.last_effectiveness_text = ""
        self.turn_messages = []
        self.player_pokemon.crit = False
        self.wild.crit = False
        self.player_attack_offset = (0.0, 0.0)
        self.wild_attack_offset = (0.0, 0.0)
        self.attack_sequence_active = True
        self.attack_phase = "delay"
        self.attack_timer = 0.0
        self.attack_order = attack_order or (["player", "wild"] if random.random() < 0.5 else ["wild", "player"])
        self.attack_index = 0
        self.active_attacker_side = self.attack_order[0]
        return True

    def update_opening_attack(self, dt: float) -> bool:
        if not self.opening_attack_pending or self.encounter_kind != "wild" or self.is_over:
            return False
        if self.attack_sequence_active or self.catch_anim_active or self.intro_active:
            return False
        if self.transition > 0.02:
            return False

        self.opening_attack_delay = max(0.0, self.opening_attack_delay - dt)
        if self.opening_attack_delay > 0.0:
            return False

        opening_side = "player" if random.random() < 0.5 else "wild"
        self.opening_attack_pending = False
        return self.start_turn_sequence([opening_side])

    def update_attack_sequence(self, dt: float):
        events = []
        if not self.attack_sequence_active:
            return events

        self.attack_timer += dt

        if self.attack_phase == "delay":
            if self.attack_timer >= self.ATTACK_START_DELAY:
                self.attack_phase = "lunge"
                self.attack_timer = 0.0
                events.append({"type": "attack_started", "side": self.active_attacker_side})

        elif self.attack_phase == "lunge":
            progress = min(1.0, self.attack_timer / self.ATTACK_LUNGE_TIME)
            self._set_attack_offset(self.active_attacker_side, self._ease_out(progress))
            if progress >= 1.0:
                attack_result = self._resolve_current_attack()
                events.append({
                    "type": "attack_hit" if attack_result["hit"] else "attack_miss",
                    "side": self.active_attacker_side,
                })
                self.attack_phase = "impact"
                self.attack_timer = 0.0

        elif self.attack_phase == "impact":
            self._set_attack_offset(self.active_attacker_side, 1.0)
            if self.attack_timer >= self.ATTACK_IMPACT_HOLD:
                self.attack_phase = "return"
                self.attack_timer = 0.0

        elif self.attack_phase == "return":
            progress = min(1.0, self.attack_timer / self.ATTACK_RETURN_TIME)
            self._set_attack_offset(self.active_attacker_side, 1.0 - self._ease_out(progress))
            if progress >= 1.0:
                self.player_attack_offset = (0.0, 0.0)
                self.wild_attack_offset = (0.0, 0.0)
                if self.is_over or self.attack_index >= len(self.attack_order) - 1:
                    self._finish_attack_sequence()
                    events.append({"type": "turn_finished"})
                else:
                    self.attack_index += 1
                    self.active_attacker_side = self.attack_order[self.attack_index]
                    self.attack_phase = "between"
                    self.attack_timer = 0.0

        elif self.attack_phase == "between":
            if self.attack_timer >= self.ATTACK_BETWEEN_DELAY:
                self.attack_phase = "delay"
                self.attack_timer = 0.0

        return events

    def _ease_out(self, progress: float) -> float:
        return 1.0 - (1.0 - progress) * (1.0 - progress)

    def _set_attack_offset(self, side: str | None, progress: float):
        if side == "player":
            self.player_attack_offset = (
                self.PLAYER_ATTACK_VECTOR[0] * progress,
                self.PLAYER_ATTACK_VECTOR[1] * progress,
            )
            self.wild_attack_offset = (0.0, 0.0)
        elif side == "wild":
            self.wild_attack_offset = (
                self.WILD_ATTACK_VECTOR[0] * progress,
                self.WILD_ATTACK_VECTOR[1] * progress,
            )
            self.player_attack_offset = (0.0, 0.0)

    def _resolve_current_attack(self):
        attacker_side = self.active_attacker_side
        attacker = self.player_pokemon if attacker_side == "player" else self.wild
        defender = self.wild if attacker_side == "player" else self.player_pokemon

        hit_chance = 0.87 + (attacker.stats.agility - defender.stats.evade) * 0.01
        hit_chance = max(0.62, min(0.96, hit_chance))
        if random.random() > hit_chance:
            attacker.crit = False
            self._append_turn_message(f"{attacker.species.name.title()} missed!")
            return {"hit": False}

        is_crit = random.random() < 0.15
        damage = max(1, attacker.stats.attack - defender.stats.defense // 2)
        multiplier = get_type_multiplier(attacker.type, defender.type)
        damage = max(0, int(round(damage * multiplier)))
        if is_crit:
            damage *= 2
        attacker.crit = is_crit

        defender.take_damage(damage)
        defender.shake_timer = 0.2
        defender.hp_shake_timer = 0.2
        defender.flash_timer = 0.22

        effectiveness_text = get_effectiveness_text(multiplier)
        if effectiveness_text:
            self._append_turn_message(effectiveness_text)
        if is_crit:
            self._append_turn_message("Critical hit!")

        if attacker_side == "player":
            if self.encounter_kind == "trainer" and self.is_gym_leader:
                fight_reward = 24 + self.wild.level * 5
            elif self.encounter_kind == "trainer":
                fight_reward = 14 + self.wild.level * 3
            else:
                fight_reward = 8 + self.wild.level * 2
            self.player.money += fight_reward
            self.last_money_reward += fight_reward

        if defender.is_fainted():
            self.is_over = True
            if attacker_side == "player":
                if self.encounter_kind == "trainer" and self.is_gym_leader:
                    xp_reward = 90 + self.wild.level * 5
                elif self.encounter_kind == "trainer":
                    xp_reward = 55 + self.wild.level * 4
                else:
                    xp_reward = 30 + self.wild.level * 3
                self.player.award_party_xp(xp_reward)
                self.last_xp_reward = xp_reward

                if self.encounter_kind == "trainer" and self.is_gym_leader:
                    win_reward = 140 + self.wild.level * 38
                elif self.encounter_kind == "trainer":
                    win_reward = 70 + self.wild.level * 26
                else:
                    win_reward = 40 + self.wild.level * 20
                self.player.money += win_reward
                self.last_money_reward += win_reward

        return {"hit": True, "damage": damage}

    def _append_turn_message(self, message: str):
        if not message:
            return
        self.turn_messages.append(message)
        self.last_effectiveness_text = " ".join(self.turn_messages)

    def _finish_attack_sequence(self):
        self.attack_sequence_active = False
        self.attack_phase = "idle"
        self.attack_timer = 0.0
        self.active_attacker_side = None
        self.player_attack_offset = (0.0, 0.0)
        self.wild_attack_offset = (0.0, 0.0)

    def catch_chance(self) -> float:
        if self.encounter_kind != "wild":
            return 0.0
        hp_ratio = self.wild.stats.current_hp / self.wild.stats.max_hp
        return max(0.1, 1.0 - hp_ratio)  # Lavere HP gir høyere fangstsjanse.

    def catch_difficulty_label(self) -> str:
        """Gi en enkel tekst som forklarer hvor vanskelig fangsten er."""
        chance = self.catch_chance()
        if chance >= 0.65:
            return "Easy to catch"
        if chance >= 0.3:
            return "Hard to catch"
        return "Almost impossible to catch"

    def start_catch_attempt(self) -> bool:
        if self.encounter_kind != "wild" or self.catch_anim_active or self.is_over or self.opening_attack_pending or self.attack_sequence_active:
            return False

        self.last_money_reward = 0
        self.last_xp_reward = 0
        chance = self.catch_chance()
        self.catch_anim_active = True
        self.catch_anim_phase = "throw"
        self.catch_anim_timer = 0.0
        self.catch_anim_result = random.random() < chance
        self.catch_blinks_done = 0
        self.catch_resolution = None
        self.catch_ball_pos = (180.0, 430.0)
        self.catch_ball_visible = True
        self.catch_fog_timer = 0.0
        self.catch_flash_timer = 0.0
        self.catch_escape_blinks = random.randint(1, 3)
        self.catch_ready_to_finish = False
        return True

    def update_catch_animation(self, dt: float):
        if not self.catch_anim_active:
            return

        self.catch_anim_timer += dt

        if self.catch_anim_phase == "throw":
            progress = min(1.0, self.catch_anim_timer / 0.55)
            start_x, start_y = 180.0, 430.0
            end_x, end_y = 558.0, 314.0
            arc_height = 150.0
            current_x = start_x + (end_x - start_x) * progress
            current_y = start_y + (end_y - start_y) * progress - math.sin(progress * math.pi) * arc_height
            self.catch_ball_pos = (current_x, current_y)
            if progress >= 1.0:
                self.catch_anim_phase = "absorb"
                self.catch_anim_timer = 0.0
                self.catch_ball_pos = (end_x, end_y)

        elif self.catch_anim_phase == "absorb":
            self.catch_ball_visible = True
            self.catch_fog_timer = min(1.0, self.catch_anim_timer / 0.34)
            if self.catch_anim_timer >= 0.34:
                self.catch_anim_phase = "blink"
                self.catch_anim_timer = 0.0
                self.catch_fog_timer = 0.0

        elif self.catch_anim_phase == "blink":
            blink_cycle = 0.24
            cycle_progress = self.catch_anim_timer / blink_cycle
            self.catch_ball_visible = int(cycle_progress * 8) % 2 == 0
            if self.catch_anim_timer >= blink_cycle:
                self.catch_blinks_done += 1
                self.catch_anim_timer = 0.0
                self.catch_ball_visible = True
                target_blinks = 3 if self.catch_anim_result else self.catch_escape_blinks
                if self.catch_blinks_done >= target_blinks:
                    if self.catch_anim_result:
                        catch_reward = 25 + self.wild.level * 15
                        catch_xp_reward = 18 + self.wild.level * 2
                        self.player.money += catch_reward
                        self.last_money_reward = catch_reward
                        self.last_xp_reward = catch_xp_reward
                        self.catch_resolution = "caught"
                        self.catch_ready_to_finish = True
                        self.catch_anim_phase = "done"
                    else:
                        self.catch_anim_phase = "escape"
                        self.catch_anim_timer = 0.0
                        self.catch_fog_timer = 0.45
                        self.catch_flash_timer = 0.42

        elif self.catch_anim_phase == "escape":
            self.catch_ball_visible = False
            self.catch_fog_timer = max(0.0, 0.45 - self.catch_anim_timer)
            self.catch_flash_timer = max(0.0, 0.42 - self.catch_anim_timer)
            if self.catch_anim_timer >= 0.45:
                self.catch_resolution = "escaped"
                self.catch_ready_to_finish = True
                self.catch_anim_phase = "done"

    def finish_catch_animation(self):
        if not self.catch_ready_to_finish:
            return None

        outcome = self.catch_resolution
        self.catch_anim_active = False
        self.catch_anim_phase = "idle"
        self.catch_anim_timer = 0.0
        self.catch_ready_to_finish = False
        self.catch_ball_visible = False
        self.catch_fog_timer = 0.0
        self.catch_flash_timer = 0.0

        if outcome == "caught":
            self.is_over = True
            self.caught = True
            return "caught"

        if outcome == "escaped":
            return "escaped"

        return None

    def update_intro(self, dt: float):
        if not self.intro_active:
            return
        self.intro_timer = max(0.0, self.intro_timer - dt)
        if self.intro_timer <= 0:
            self.intro_active = False

    def try_catch(self) -> bool:
        if self.catch_anim_result:
            self.is_over = True
            self.caught = True
            catch_reward = 25 + self.wild.level * 15
            self.player.money += catch_reward
            self.last_money_reward = catch_reward
            return True
        return False

class World:
    def __init__(self, player: Player):
        self.player = player
        self.current_encounter: Encounter | None = None
        self.walk_steps_taken = 0

    def roll_wild_level(self) -> int:
        active_level = max(1, self.player.active_pokemon.level)
        rarity_roll = random.random()

        # De fleste møter havner lavere enn nivået til spillerens aktive kamp-Pokemon.
        if rarity_roll < 0.86:
            lower_max = max(2, active_level + 1)
            return random.randint(1, lower_max)

        # En mindre del av møtene holder seg nærmere spillerens nivå.
        if rarity_roll < 0.99:
            near_min = max(1, active_level - 2)
            near_max = max(near_min, active_level + 3)
            return random.randint(near_min, near_max)

        # Svært sjeldne toppmøter med mye høyere nivå.
        return random.randint(10, 60)

    def roll_wild_species(self) -> Species:
        """Velg en vill art med vekter slik at sterke arter er sjeldnere."""
        return random.choices(
            population=list(WILD_SPECIES_WEIGHTS.keys()),
            weights=list(WILD_SPECIES_WEIGHTS.values()),
            k=1,
        )[0]

    def walk_step(self):
        """Kall denne når spilleren går rundt i terrenget."""
        self.walk_steps_taken += 1
        guaranteed_first_encounter = self.walk_steps_taken == 1
        encounter_chance = 0.34
        if guaranteed_first_encounter or random.random() < encounter_chance:
            species = self.roll_wild_species()
            level = self.roll_wild_level()
            wild = Pokemon(species, level)
            self.current_encounter = Encounter(wild, self.player)
            self.current_encounter.transition = 1.0

    def start_trainer_battle(
        self,
        trainer_name: str,
        pokemon_species: Species,
        level: int,
        intro_text: str | None = None,
        is_gym_leader: bool = False,
    ):
        trainer_pokemon = Pokemon(pokemon_species, level)
        trainer_pokemon.stats.current_hp = trainer_pokemon.stats.max_hp
        self.current_encounter = Encounter(
            trainer_pokemon,
            self.player,
            encounter_kind="trainer",
            opponent_name=trainer_name,
            intro_text=intro_text,
            is_gym_leader=is_gym_leader,
        )
        self.current_encounter.transition = 1.0
