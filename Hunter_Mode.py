import pygame
import sys
from PIL import Image, ImageSequence

ANCHO_VENTANA = 800
ALTO_VENTANA = 600
FPS = 10  # Velocidad de animación del GIF


class HunterMode:
    def __init__(self, ventana, nombre_jugador):
        self.ventana = ventana
        self.nombre_jugador = nombre_jugador
        self.reloj = pygame.time.Clock()
        self.corriendo = True

        # Cargar los frames del GIF (BG_2.gif)
        self.frames = self.cargar_gif("ASSETS/GIFS/BG_2.gif")
        self.frame_index = 0

    def cargar_gif(self, ruta):
        frames = []
        try:
            imagen = Image.open(ruta)
            for frame in ImageSequence.Iterator(imagen):
                frame = frame.convert("RGBA")
                frame = frame.resize((ANCHO_VENTANA, ALTO_VENTANA))
                modo = frame.mode
                size = frame.size
                data = frame.tobytes()
                py_image = pygame.image.fromstring(data, size, modo)
                frames.append(py_image)
        except Exception as e:
            print(f"Error al cargar GIF: {e}")
            frame_negro = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA))
            frame_negro.fill((0, 0, 0))
            frames.append(frame_negro)
        return frames

    def dibujar(self):
        self.ventana.blit(self.frames[self.frame_index], (0, 0))
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        pygame.display.flip()

    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                self.corriendo = False

    def ejecutar(self):
        while self.corriendo:
            self.manejar_eventos()
            self.dibujar()
            self.reloj.tick(FPS)
