import pygame
import time

class TimerBar:
    def __init__(self, duracion, x, y, width=400, height=40):
        self.duracion = duracion
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.inicio = time.time()

        self.VERDE = (0, 255, 0)
        self.AMARILLO = (255, 255, 0)
        self.ROJO = (255, 0, 0)
        self.BLANCO = (255, 255, 255)

    def reset(self):
        self.inicio = time.time()

    def get_remaining_time(self):
        return max(self.duracion - (time.time() - self.inicio), 0)

    def is_finished(self):
        return self.get_remaining_time() <= 0

    def draw(self, pantalla):
        tiempo_restante = self.get_remaining_time()
        progreso = tiempo_restante / self.duracion

        if progreso > 0.5:
            color = self.VERDE
        elif progreso > 0.2:
            color = self.AMARILLO
        else:
            color = self.ROJO

        ancho_actual = int(self.width * progreso)

        pygame.draw.rect(pantalla, self.BLANCO, (self.x, self.y, self.width, self.height), 3)
        pygame.draw.rect(pantalla, color, (self.x, self.y, ancho_actual, self.height))


class PointsBox:
    def __init__(self, x, y, width, height, initial_points=0):
        self.points = initial_points
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)

        # Fuente default
        self.font = pygame.font.Font(None, 35)

    def add_points(self, amount):
        self.points += amount

    def draw(self, pantalla):
        pygame.draw.rect(pantalla, self.BLACK, (self.x, self.y, self.width, self.height), border_radius=4)
        pygame.draw.rect(pantalla, self.WHITE, (self.x, self.y, self.width, self.height), 2, border_radius=4)

        text = self.font.render(f"Puntos: {self.points}", True, self.WHITE)
        text_rect = text.get_rect(center=(self.x + self.width//2, self.y + self.height//2))

        pantalla.blit(text, text_rect)


############### ESTA ES LA BARRA DE ENERGIA #######################

class EnergyBar:
    def __init__(self, max_energy, x, y, width=300, height=25):
        self.max_energy = max_energy
        self.energy = max_energy
        
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # Colores
        self.GREEN = (0, 255, 0)
        self.YELLOW = (255, 255, 0)
        self.RED = (255, 0, 0)
        self.WHITE = (255, 255, 255)

        # Velocidades
        self.drain_speed = 20
        self.recover_speed = 10

    def drain(self, dt):
        self.energy -= self.drain_speed * dt
        self.energy = max(self.energy, 0)

    def recover(self, dt):
        self.energy += self.recover_speed * dt
        self.energy = min(self.energy, self.max_energy)

    def draw(self, pantalla):
        porcentaje = self.energy / self.max_energy
        width_actual = int(self.width * porcentaje)

        if porcentaje > 0.5:
            color = self.GREEN
        elif porcentaje > 0.2:
            color = self.YELLOW
        else:
            color = self.RED

        pygame.draw.rect(pantalla, self.WHITE, (self.x, self.y, self.width, self.height), 3)
        pygame.draw.rect(pantalla, color, (self.x, self.y, width_actual, self.height))