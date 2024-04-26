import pygame


class Button:
    def __init__(self, x, y, width, height, colour, text, isai, ainum):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.colour = colour
        self.text = text
        self.isAI = isai
        self.AINum = ainum
        self.font = pygame.font.Font(None, 36)
        self.text = self.font.render(self.text, True, "#000000")

    def show(self, screen):
        font = pygame.font.Font(None, 36)
        pygame.draw.rect(screen, self.colour, (self.x, self.y, self.width, self.height))
        text_rect = self.text.get_rect(center=(self.x+(self.width//2), self.y + (self.height // 2)))
        screen.blit(self.text, text_rect)

    def is_pressed(self):
        if self.isAI:
            return self.AINum
