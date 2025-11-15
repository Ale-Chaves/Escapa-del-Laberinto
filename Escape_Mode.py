import pygame
import sys
from PIL import Image, ImageSequence
import random

from HUD import PointsBox, TimerBar, EnergyBar
from Ending_Screen import EndingScreen



'''Variables Globales'''

ANCHO_VENTANA = 800
ALTO_VENTANA = 600
FPS = 10

# MAPA - Ajustado para ser más pequeño y centrado
TILE = 25  # Aumentado para mejor visibilidad
MAP_COLS = 24  # Reducido de 40 a 24
MAP_ROWS = 18  # Reducido de 30 a 18

# Margen para centrar el mapa
MARGEN_X = (ANCHO_VENTANA - (MAP_COLS * TILE)) // 2
MARGEN_Y = (ALTO_VENTANA - (MAP_ROWS * TILE)) // 2


class EscapeMode:
    def __init__(self, ventana, nombre_jugador):

        # ESTO ES DEL HUD

        self.timer = TimerBar(duracion=10, x=200, y=20)
        self.points_box = PointsBox(x=20, y=550, width=200, height=40, initial_points=0)
        self.energy_bar = EnergyBar(max_energy=100, x=550, y=550)

        print("Entrando a Escape Mode...")

        self.ventana = ventana
        self.nombre_jugador = nombre_jugador
        self.reloj = pygame.time.Clock()
        self.corriendo = True

        # Cargar los frames del GIF (BG_2.gif)
        self.frames = self.cargar_gif("ASSETS/GIFS/BG_2.gif")
        self.frame_index = 0
        
        # Cargar sprites
        self.cargar_sprites()

    ###############################

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
    

    def cargar_sprites(self):
        """Carga los sprites de los elementos del mapa"""
        self.sprites = {}
        try:
            # Cargar y redimensionar sprites
            wall = pygame.image.load("ASSETS/SPRITES/Wall.png")
            self.sprites["W"] = pygame.transform.scale(wall, (TILE, TILE))
            
            vines = pygame.image.load("ASSETS/SPRITES/Vines.png")
            self.sprites["L"] = pygame.transform.scale(vines, (TILE, TILE))
            
            tunnel = pygame.image.load("ASSETS/SPRITES/Tunnel.png")
            self.sprites["T"] = pygame.transform.scale(tunnel, (TILE, TILE))
            
            door = pygame.image.load("ASSETS/SPRITES/Door.png")
            self.sprites["E"] = pygame.transform.scale(door, (TILE, TILE))
            
            print("Sprites cargados correctamente")
        except Exception as e:
            print(f"Error al cargar sprites: {e}")
            # Crear sprites de respaldo con colores
            self.sprites["W"] = self.crear_sprite_color((50, 50, 50))
            self.sprites["L"] = self.crear_sprite_color((0, 180, 0))
            self.sprites["T"] = self.crear_sprite_color((100, 50, 0))
            self.sprites["E"] = self.crear_sprite_color((255, 215, 0))
    
    def crear_sprite_color(self, color):
        """Crea un sprite simple de color como respaldo"""
        superficie = pygame.Surface((TILE, TILE))
        superficie.fill(color)
        return superficie

    def dibujar(self):
        # Dibujar el GIF de fondo
        if self.frames:
            self.ventana.blit(self.frames[self.frame_index], (0, 0))
            # Actualizar frame del GIF
            self.frame_index = (self.frame_index + 1) % len(self.frames)
        else:
            self.ventana.fill((0, 0, 0))
        self.energy_bar.draw(self.ventana)
        self.timer.draw(self.ventana)
        self.points_box.draw(self.ventana)
        self.dibujar_mapa()
        pygame.display.flip()

    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                self.corriendo = False



########################
#WHILE DE EJECUTAR



    def ejecutar(self):
        print("EscapeMode iniciando...")
        self.mapa = self.generar_mapa()

        while self.corriendo:

            if self.timer.is_finished():

                end = EndingScreen(self.ventana, self.nombre_jugador, self.points_box.points)
                end.run()
                self.corriendo = False

            dt = self.reloj.get_time() / 1000  # segundos

            self.manejar_eventos()
            self.dibujar()

            keys = pygame.key.get_pressed()
            running = keys[pygame.K_LSHIFT]

            if running:
                self.energy_bar.drain(dt)  # gastar energía
            else:
                self.energy_bar.recover(dt)  # regenerar

            pygame.display.flip()
            self.reloj.tick(FPS)



    ##############GENERACIÓN DEL MAPA:

    def generar_mapa(self):
        """Genera un laberinto aleatorio con bordes de muros"""
        
        self.MAP_COLS = MAP_COLS
        self.MAP_ROWS = MAP_ROWS

        # PASO 1: Inicializar todo como caminos
        mapa = [["P" for _ in range(MAP_COLS)] for _ in range(MAP_ROWS)]

        # PASO 2: Crear bordes de muros (marco exterior)
        for col in range(MAP_COLS):
            mapa[0][col] = "W"  # Borde superior
            mapa[MAP_ROWS - 1][col] = "W"  # Borde inferior
        
        for fila in range(MAP_ROWS):
            mapa[fila][0] = "W"  # Borde izquierdo
            mapa[fila][MAP_COLS - 1] = "W"  # Borde derecho

        # PASO 3: Definir inicio y salida (dentro de los bordes)
        inicio_fila = random.randint(2, MAP_ROWS - 3)
        inicio_col = 2
        
        salida_fila = random.randint(2, MAP_ROWS - 3)
        salida_col = MAP_COLS - 3

        # Guardar posiciones importantes
        self.inicio = (inicio_fila, inicio_col)
        self.salida = (salida_fila, salida_col)

        # PASO 4: Crear camino garantizado a la salida
        camino_garantizado = self.crear_camino_garantizado(inicio_fila, inicio_col, 
                                                            salida_fila, salida_col)

        # PASO 5: Agregar muros en patrón equilibrado
        self.agregar_muros_equilibrados(mapa, camino_garantizado)

        # PASO 6: Agregar lianas y túneles
        self.agregar_elementos_tacticos(mapa, camino_garantizado)

        # PASO 7: Asegurar que inicio y salida estén despejados
        mapa[inicio_fila][inicio_col] = "P"
        mapa[salida_fila][salida_col] = "E"  # E = Exit (salida)

        return mapa

    def crear_camino_garantizado(self, inicio_fila, inicio_col, salida_fila, salida_col):
        """Crea un camino garantizado desde inicio hasta salida"""
        camino = set()
        fila, col = inicio_fila, inicio_col
        
        while col < salida_col or fila != salida_fila:
            camino.add((fila, col))
            
            # Decidir dirección
            if col < salida_col and random.random() < 0.7:
                col += 1
            elif fila < salida_fila:
                fila += 1
            elif fila > salida_fila:
                fila -= 1
            elif col < salida_col:
                col += 1
        
        camino.add((salida_fila, salida_col))
        return camino

    def agregar_muros_equilibrados(self, mapa, camino_garantizado):
        """Agrega muros en patrón equilibrado para crear el laberinto"""
        
        # Calcular celdas interiores (sin contar bordes)
        celdas_interiores = (MAP_ROWS - 2) * (MAP_COLS - 2)
        
        # Queremos aproximadamente 30-40% del interior como muros
        # (para balance entre caminos y obstáculos)
        num_muros_objetivo = int(celdas_interiores * random.uniform(0.30, 0.40))
        
        muros_colocados = 0
        
        # Patrón de rejilla estilo Bomberman clásico
        # Colocar muros en posiciones estratégicas
        for fila in range(2, MAP_ROWS - 2):
            for col in range(2, MAP_COLS - 2):
                
                # No tocar el camino garantizado
                if (fila, col) in camino_garantizado:
                    continue
                
                # No tocar cerca del inicio o salida
                if (abs(fila - self.inicio[0]) <= 1 and abs(col - self.inicio[1]) <= 1):
                    continue
                if (abs(fila - self.salida[0]) <= 1 and abs(col - self.salida[1]) <= 1):
                    continue
                
                # Decidir si colocar muro con probabilidad controlada
                if muros_colocados < num_muros_objetivo:
                    # Crear algunos patrones de muros agrupados
                    if random.random() < 0.5:
                        mapa[fila][col] = "W"
                        muros_colocados += 1
                        
                        # Ocasionalmente crear grupos pequeños (2-4 muros juntos)
                        if random.random() < 0.3:
                            direcciones = [(0, 1), (1, 0), (0, -1), (-1, 0)]
                            random.shuffle(direcciones)
                            
                            for df, dc in direcciones[:random.randint(1, 2)]:
                                nf, nc = fila + df, col + dc
                                if (1 < nf < MAP_ROWS - 1 and 1 < nc < MAP_COLS - 1 and
                                    mapa[nf][nc] == "P" and (nf, nc) not in camino_garantizado and
                                    muros_colocados < num_muros_objetivo):
                                    mapa[nf][nc] = "W"
                                    muros_colocados += 1

    def agregar_elementos_tacticos(self, mapa, camino_garantizado):
        """Agrega lianas y túneles distribuidos estratégicamente por el mapa"""
        
        # Calcular basado en celdas interiores de CAMINO disponibles
        celdas_camino = 0
        for fila in range(1, MAP_ROWS - 1):
            for col in range(1, MAP_COLS - 1):
                if mapa[fila][col] == "P":
                    celdas_camino += 1
        
        # 10-15% de los caminos serán lianas
        num_lianas = int(celdas_camino * random.uniform(0.10, 0.15))
        # 10-15% de los caminos serán túneles
        num_tuneles = int(celdas_camino * random.uniform(0.10, 0.15))
        
        # Agregar lianas
        lianas_colocadas = 0
        intentos = 0
        while lianas_colocadas < num_lianas and intentos < num_lianas * 3:
            intentos += 1
            fila = random.randint(2, MAP_ROWS - 3)
            col = random.randint(2, MAP_COLS - 3)
            
            if (mapa[fila][col] == "P" and 
                (fila, col) not in camino_garantizado and
                # No poner cerca del inicio o salida
                not (abs(fila - self.inicio[0]) <= 1 and abs(col - self.inicio[1]) <= 1) and
                not (abs(fila - self.salida[0]) <= 1 and abs(col - self.salida[1]) <= 1)):
                mapa[fila][col] = "L"
                lianas_colocadas += 1
        
        # Agregar túneles
        tuneles_colocados = 0
        intentos = 0
        while tuneles_colocados < num_tuneles and intentos < num_tuneles * 3:
            intentos += 1
            fila = random.randint(2, MAP_ROWS - 3)
            col = random.randint(2, MAP_COLS - 3)
            
            if (mapa[fila][col] == "P" and 
                (fila, col) not in camino_garantizado and
                # No poner cerca del inicio o salida
                not (abs(fila - self.inicio[0]) <= 1 and abs(col - self.inicio[1]) <= 1) and
                not (abs(fila - self.salida[0]) <= 1 and abs(col - self.salida[1]) <= 1)):
                mapa[fila][col] = "T"
                tuneles_colocados += 1

    def dibujar_mapa(self):
        """Dibuja el mapa con sprites"""
        
        for fila in range(self.MAP_ROWS):
            for col in range(self.MAP_COLS):
                tipo = self.mapa[fila][col]
                x = MARGEN_X + (col * TILE)
                y = MARGEN_Y + (fila * TILE)

                # Dibujar según el tipo
                if tipo == "P":
                    # Camino - semi-transparente para ver el fondo
                    superficie = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
                    pygame.draw.rect(superficie, (200, 200, 200, 100), (0, 0, TILE, TILE))
                    self.ventana.blit(superficie, (x, y))
                    
                elif tipo in self.sprites:
                    # Usar sprites para W, L, T, E
                    self.ventana.blit(self.sprites[tipo], (x, y))
                
                # Borde para todas las casillas
                pygame.draw.rect(self.ventana, (0, 0, 0, 50), (x, y, TILE, TILE), 1)