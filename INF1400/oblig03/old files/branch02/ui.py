"""Enkle UI-hjelpere for knapper, tekst og helsefelt.

Denne modulen samler små tegnefunksjoner som brukes flere steder i spillet.
"""

import pygame
import math


_mouse_position_provider = None


def set_mouse_position_provider(provider):
    global _mouse_position_provider

    _mouse_position_provider = provider


def get_ui_mouse_pos():
    if _mouse_position_provider is None:
        return pygame.mouse.get_pos()
    return _mouse_position_provider()


class Button:
    def __init__(self, x, y, width, height, text, font, bg_color=(80, 80, 120), text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.text_color = text_color

    def draw(self, screen):
        mouse_pos = get_ui_mouse_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)
        fill_color = self.bg_color
        if is_hovered:
            fill_color = tuple(min(255, channel + 35) for channel in self.bg_color)

        pygame.draw.rect(screen, fill_color, self.rect, border_radius=8)
        if is_hovered:
            pygame.draw.rect(screen, (255, 240, 180), self.rect, width=2, border_radius=8)

        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class PokeballButton(Button):
    def __init__(self, x, y, size, text, font):
        super().__init__(x, y, size, size, text, font, bg_color=(0, 0, 0, 0))

    def draw(self, screen):
        mouse_pos = get_ui_mouse_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)
        center = self.rect.center
        radius = self.rect.width // 2

        outline_color = (255, 240, 180) if is_hovered else (30, 30, 40)
        top_color = (250, 90, 90) if is_hovered else (225, 60, 60)
        bottom_color = (250, 250, 250) if is_hovered else (232, 232, 232)

        pygame.draw.circle(screen, outline_color, center, radius + 3)
        pygame.draw.circle(screen, bottom_color, center, radius)
        pygame.draw.circle(screen, top_color, center, radius)
        pygame.draw.rect(screen, bottom_color, (self.rect.left, center[1], self.rect.width, radius))
        pygame.draw.line(screen, outline_color, (self.rect.left + 6, center[1]), (self.rect.right - 6, center[1]), 5)
        pygame.draw.circle(screen, outline_color, center, radius // 3 + 6)
        pygame.draw.circle(screen, (245, 245, 245), center, radius // 3)

        text_surf = self.font.render(self.text, True, outline_color)
        text_rect = text_surf.get_rect(center=(center[0], self.rect.bottom + 18))
        screen.blit(text_surf, text_rect)


def draw_text(screen, text, x, y, font, color=(255, 255, 255)):
    """Tegn tekst på skjermen uten å gjenta samme kode flere steder."""
    surf = font.render(text, True, color)
    screen.blit(surf, (x, y))


def draw_health_bar(screen, x, y, width, height, current, max_value, shake_offset=0):
    ratio = current / max_value

    # Når HP er lav, pulserer linjen rødt for å gjøre faren tydelig.
    if ratio < 0.25:
        flash = (math.sin(pygame.time.get_ticks() * 0.01) + 1) / 2  
        red = int(200 + flash * 55)
        green = int(0 + flash * 30)
        color = (red, green, 0)
    else:
        color = (50, 220, 50)

    # Bakgrunnen viser tapt HP.
    pygame.draw.rect(screen, (180, 50, 50), (x + shake_offset, y, width, height))

    # Forgrunnen viser gjenværende HP.
    pygame.draw.rect(screen, color, (x + shake_offset, y, width * ratio, height))
