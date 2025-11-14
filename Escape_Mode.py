import pygame
import sys
from PIL import Image, ImageSequence

'''Variables Globales'''

ANCHO_VENTANA = 800
ALTO_VENTANA = 600
FPS = 10
#MAPA
TILE = 20
MAP_COLS = ANCHO_VENTANA // TILE
MAP_ROWS = ALTO_VENTANA // TILE



class EscapeMode:
    def __init__(self, ventana, nombre_jugador):
        print("Entrando a Escape Mode...")
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
        self.ventana.fill((0, 0, 0))  # limpia pantalla

        self.dibujar_mapa()
        pygame.display.flip()


    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                self.corriendo = False

    def ejecutar(self):
        print("EscapeMode iniciando...")
        self.mapa = self.generar_mapa()

        while self.corriendo:
            self.manejar_eventos()
            self.dibujar()
            self.reloj.tick(FPS)

    
    ##############ACA VA EL MAPA:

    def generar_mapa(self):
        import random

        MAP_COLS = ANCHO_VENTANA // TILE
        MAP_ROWS = ALTO_VENTANA // TILE
        self.MAP_COLS = MAP_COLS
        self.MAP_ROWS = MAP_ROWS

        mapa = []
        for fila in range(MAP_ROWS):
            mapa.append(["W"]*MAP_COLS)

        inicio_fila = random.randint(0, MAP_ROWS - 1)
        inicio_col = 0 

        salida_fila = random.randint(0, MAP_ROWS - 1)
        salida_col = MAP_COLS - 1

        mapa[inicio_fila][inicio_col] = "P"
        
        fila = inicio_fila
        col = inicio_col

        while col < salida_col:
            movimiento = random.choice(["R", "U", "D"])  # derecha, arriba, abajo

            if movimiento == "R":
                if col + 1 < MAP_COLS:
                    col += 1

            elif movimiento == "U":
                if fila - 1 >= 0:
                    fila -= 1

            elif movimiento == "D":
                if fila + 1 < MAP_ROWS:
                    fila += 1

            mapa[fila][col] = "P"

        # QUE HAYA SALIDA:
        mapa[salida_fila][salida_col] = "P"

        opciones = ["P", "W", "L", "T"]  # piso, pared, liana, tunel

        for f in range(MAP_ROWS):
            for c in range(MAP_COLS):
                # cambiar a que una pared sea camino
                if mapa[f][c] == "W":
                    mapa[f][c] = random.choice(opciones)

        return mapa
    
    # ACA YA GENERA LA MATRIZ, AHORA SIGUE QUE LA DIBUJE

    def dibujar_mapa(self):


        COLORES = {
            "P": (200, 200, 200),
            "W": (50, 50, 50),
            "L": (0, 180, 0),
            "T": (100, 50, 0),
        }

        for fila in range(self.MAP_ROWS):
            for col in range(self.MAP_COLS):

                tipo = self.mapa[fila][col]
                x = col * TILE
                y = fila * TILE

                pygame.draw.rect(self.ventana,COLORES[tipo],(x,y,TILE,TILE))