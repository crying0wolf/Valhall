import pygame


class Button(): # Initialiserer knapper som fungerer i pygame
    def __init__(self, image, pos, text_input, font, base_color, hovering_color, hover_sound=None, click_sound=None):
        self.has_custom_image = image is not None
        self.image = image
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.font = font
        self.base_color, self.hovering_color = base_color, hovering_color
        self.hover_sound = hover_sound
        self.click_sound = click_sound
        self.text_input = text_input
        self.text = self.font.render(self.text_input.upper(), True, self.base_color)

        if self.image is None:
            self.image = self.text
            self.hover_image = self.image
        else:
            self.hover_image = self.image.copy()
            self.hover_image.fill((55, 55, 55), special_flags=pygame.BLEND_RGB_ADD)

        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))
        self.hitbox = self.text_rect.inflate(40, 20)
        self.is_hovered = False
        self.was_hovered = False

    def update(self, screen): # Oppdaterer knappens tekst eller bilde.
        if self.image is not None:
            if self.is_hovered and self.has_custom_image:
                screen.blit(self.hover_image, self.rect)
            else:
                screen.blit(self.image, self.rect)

        screen.blit(self.text, self.text_rect)

    def checkForInput(self, position): # Sjekker for input og intaksjoner - kan klikkes?
        return self.hitbox.collidepoint(position)

    def changeColor(self, position): # At knappen skal bytte farge når vi hovrer musepekeren over denne.
        is_hovered = self.hitbox.collidepoint(position)
        self.is_hovered = is_hovered

        if is_hovered:
            self.text = self.font.render(self.text_input.upper(), True, self.hovering_color)
        else:
            self.text = self.font.render(self.text_input.upper(), True, self.base_color)

        if is_hovered and not self.was_hovered and self.hover_sound is not None:
            self.hover_sound.play()

        self.was_hovered = is_hovered

    def playClick(self):
        if self.click_sound is not None:
            self.click_sound.play()