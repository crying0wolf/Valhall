"""Laster inn og holder orden på sprites og GIF-animasjoner.

SpriteManager skjuler filtilgang og sørger for at resten av spillet kan
hente ferdige flater uten å bekymre seg for hvordan de ble lastet inn.
"""

import os

import pygame
from PIL import Image, ImageSequence

from data import Species

class SpriteManager:
    def __init__(self):
        self.sprites = {}
        self.battle_sprites = {"front": {}, "back": {}}

    def load(self, species: Species, path: str, scale: float = 2.0):
        """Last inn en vanlig spriteflate for en art."""
        try:
            img = pygame.image.load(path).convert_alpha()
            width, height = img.get_size()
            img = pygame.transform.scale(img, (int(width * scale), int(height * scale)))
        except (pygame.error, FileNotFoundError):
            img = pygame.Surface((96, 96), pygame.SRCALPHA)
            img.fill((180, 60, 60, 255))
        self.sprites[species] = img

    def load_battle_gif(self, species: Species, path: str, perspective: str, scale: float = 2.0):
        """Last inn alle bilder fra en kamp-GIF og lagre dem som animasjonsrammer."""
        frames = []
        durations = []

        try:
            with Image.open(path) as gif:
                for frame in ImageSequence.Iterator(gif):
                    rgba_frame = frame.convert("RGBA")
                    frame_bytes = rgba_frame.tobytes()
                    surface = pygame.image.fromstring(frame_bytes, rgba_frame.size, "RGBA").convert_alpha()
                    width, height = surface.get_size()
                    scaled = pygame.transform.scale(surface, (int(width * scale), int(height * scale)))
                    frames.append(scaled)
                    durations.append(max(60, frame.info.get("duration", gif.info.get("duration", 100))))
        except (FileNotFoundError, OSError, pygame.error):
            fallback = self.sprites.get(species)
            if fallback is None:
                fallback = pygame.Surface((96, 96), pygame.SRCALPHA)
                fallback.fill((180, 60, 60, 255))
            frames = [fallback]
            durations = [100]

        self.battle_sprites[perspective][species] = {
            "frames": frames,
            "durations": durations,
        }

    def load_battle_set(self, species: Species, sprite_dir: str, scale: float = 2.0):
        """Last inn både front- og back-animasjon for en art."""
        species_name = species.name.lower()
        front_path = os.path.join(sprite_dir, f"front_{species_name}.gif")
        back_path = os.path.join(sprite_dir, f"back_{species_name}.gif")
        self.load_battle_gif(species, front_path, "front", scale)
        self.load_battle_gif(species, back_path, "back", scale)

    def get(self, species: Species):
        return self.sprites.get(species, None)

    def get_battle_frame(self, species: Species, perspective: str, elapsed_ms: int):
        """Finn riktig animasjonsframe ut fra forløpt tid i millisekunder."""
        sprite_data = self.battle_sprites.get(perspective, {}).get(species)
        if not sprite_data:
            return self.get(species)

        frames = sprite_data["frames"]
        durations = sprite_data["durations"]
        if len(frames) == 1:
            return frames[0]

        total_duration = sum(durations)
        if total_duration <= 0:
            return frames[0]

        cycle_position = elapsed_ms % total_duration
        accumulated = 0
        for index, duration in enumerate(durations):
            accumulated += duration
            if cycle_position < accumulated:
                return frames[index]
        return frames[-1]