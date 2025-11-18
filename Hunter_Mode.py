import pygame
import sys
from PIL import Image, ImageSequence
import random

from Hunter_Hud import PointsBox1, TimerBar1, EnergyBar1
from Ending_Screen import EndingScreen
from Player import Player
from Enemy import Enemy
import Music_Manager
from Countdown import Countdown



'''Variables Globales'''

ANCHO_VENTANA = 800
ALTO_VENTANA = 600
FPS = 10

# MAPA
TILE = 25
MAP_COLS = 24
MAP_ROWS = 18

# Margen para centrar el mapa
MARGEN_X = (ANCHO_VENTANA - (MAP_COLS * TILE)) // 2
MARGEN_Y = (ALTO_VENTANA - (MAP_ROWS * TILE)) // 2


class HunterMode:
    def __init__(self, ventana, nombre_jugador, num_enemigos=2, velocidad_enemigos=1.0):

        # HUD

        self.timer = TimerBar1(duracion=120, x=200, y=20)
        self.points_box = PointsBox1(x=20, y=550, width=200, height=40, initial_points=0)
        self.energy_bar = EnergyBar1(max_energy=100, x=550, y=550)

        self.ventana = ventana
        self.nombre_jugador = nombre_jugador
        self.reloj = pygame.time.Clock()
        self.corriendo = True

        # Cargar los frames del GIF (BG_2.gif)
        self.frames = self.cargar_gif("ASSETS/GIFS/BG_2.gif")
        self.frame_index = 0
        
        # Cargar sprites
        self.cargar_sprites()
        
        # Jugador
        self.jugador = None
        
        # Enemigos - Configuración de dificultad
        self.enemigos = []
        self.num_enemigos = num_enemigos
        self.velocidad_enemigos = velocidad_enemigos
        
        # Sistema de puntuación para modo Hunter
        self.puntos_perdida_por_escape = 100
        self.puntos_ganancia_por_captura = 200
        
        # Cuenta regresiva
        self.countdown = Countdown(ventana, ANCHO_VENTANA, ALTO_VENTANA)

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
        
        # Dibujar mapa
        self.dibujar_mapa()
        
        # Dibujar enemigos
        for enemigo in self.enemigos:
            enemigo.dibujar(self.ventana, MARGEN_X, MARGEN_Y)
        
        # Dibujar jugador
        if self.jugador:
            self.jugador.dibujar(self.ventana, MARGEN_X, MARGEN_Y)
        
        # Dibujar HUD
        self.energy_bar.draw(self.ventana)
        self.timer.draw(self.ventana)
        self.points_box.draw(self.ventana)
        
        pygame.display.flip()

    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                self.corriendo = False

    def ejecutar(self):
        self.mapa = self.generar_mapa()
        
        # Crear jugador después de generar el mapa
        self.jugador = Player(self.inicio[0], self.inicio[1], TILE, modo="hunter")
        
        # Crear enemigos en posiciones aleatorias
        self.crear_enemigos()
        
        # Mostrar cuenta regresiva antes de empezar
        if not self.countdown.ejecutar(self.dibujar):
            return False
        
        # Iniciar el timer DESPUÉS de la cuenta regresiva
        self.timer.start()
        
        # Iniciar música del modo
        Music_Manager.reproducir_musica("ASSETS/OST/Hunter_Mode.mp3")

        while self.corriendo:
            # Verificar si el timer terminó
            if self.timer.is_finished():
                # Detener música del modo
                Music_Manager.detener_musica()
                
                end = EndingScreen(self.ventana, self.nombre_jugador, self.points_box.points, "hunter")
                volver_al_menu = end.run()
                self.corriendo = False
                return volver_al_menu
            
            # Verificar si algún enemigo llegó a la salida
            enemigos_a_eliminar = []
            for enemigo in self.enemigos:
                if enemigo.llego_a_salida():
                    Music_Manager.reproducir_efecto("Eliminated")
                    # Restar puntos
                    self.points_box.add_points(-self.puntos_perdida_por_escape)
                    # Marcar para eliminar
                    enemigos_a_eliminar.append(enemigo)
            
            # Eliminar enemigos que escaparon y crear nuevos
            for enemigo in enemigos_a_eliminar:
                self.enemigos.remove(enemigo)
                self.crear_un_enemigo()
            
            # Verificar colisiones con enemigos
            jugador_pos = self.jugador.get_posicion()
            enemigos_atrapados = []
            for enemigo in self.enemigos:
                if enemigo.colisiona_con_jugador(jugador_pos):
                    # Reproducir sonido de eliminación
                    Music_Manager.reproducir_efecto("Eliminated")
                    # Dar puntos por captura
                    self.points_box.add_points(self.puntos_ganancia_por_captura)
                    # Marcar para eliminar
                    enemigos_atrapados.append(enemigo)
            
            # Eliminar enemigos atrapados y crear nuevos
            for enemigo in enemigos_atrapados:
                self.enemigos.remove(enemigo)
                self.crear_un_enemigo()

            dt = self.reloj.get_time() / 1000
            tiempo_actual = pygame.time.get_ticks() / 1000

            self.manejar_eventos()
            
            # Actualizar jugador
            teclas = pygame.key.get_pressed()
            self.jugador.mover(teclas, self.mapa, self.energy_bar)
            
            # Actualizar enemigos
            for enemigo in self.enemigos:
                enemigo.actualizar(jugador_pos, self.mapa, tiempo_actual)
            
            # Manejar energía
            if self.jugador.corriendo:
                self.energy_bar.drain(dt)
            else:
                self.energy_bar.recover(dt)
            
            self.dibujar()
            self.reloj.tick(FPS)
        
        # Detener música al salir
        Music_Manager.detener_musica()
        return False
    
    def crear_enemigos(self):
        """Crea los enemigos en posiciones aleatorias del mapa"""
        intentos = 0
        max_intentos = 100
        
        # Calcular frames_por_movimiento basado en la velocidad
        frames_por_movimiento = int(8 / self.velocidad_enemigos)
        
        while len(self.enemigos) < self.num_enemigos and intentos < max_intentos:
            intentos += 1
            
            # Posición aleatoria
            fila = random.randint(2, MAP_ROWS - 3)
            col = random.randint(2, MAP_COLS - 3)
            
            # Verificar que esté LEJOS de la salida (al menos 10 casillas)
            distancia_a_salida = abs(fila - self.salida[0]) + abs(col - self.salida[1])
            
            if (self.mapa[fila][col] == "P" and
                abs(fila - self.inicio[0]) + abs(col - self.inicio[1]) >= 5 and
                (fila, col) != self.salida and
                distancia_a_salida >= 10):
                
                enemigo = Enemy(fila, col, TILE, modo="hunter")
                enemigo.frames_por_movimiento = frames_por_movimiento
                # Establecer la posición de la salida para que el enemigo sepa hacia dónde huir
                enemigo.set_salida(self.salida)
                self.enemigos.append(enemigo)
    
    def crear_un_enemigo(self):
        """Crea un enemigo nuevo en posición aleatoria"""
        intentos = 0
        max_intentos = 50
        frames_por_movimiento = int(8 / self.velocidad_enemigos)
        
        while intentos < max_intentos:
            intentos += 1
            fila = random.randint(2, MAP_ROWS - 3)
            col = random.randint(2, MAP_COLS - 3)
            
            # Verificar que esté LEJOS de la salida (al menos 10 casillas)
            distancia_a_salida = abs(fila - self.salida[0]) + abs(col - self.salida[1])
            
            if (self.mapa[fila][col] == "P" and
                abs(fila - self.inicio[0]) + abs(col - self.inicio[1]) >= 5 and
                (fila, col) != self.salida and
                distancia_a_salida >= 10):
                
                enemigo = Enemy(fila, col, TILE, modo="hunter")
                enemigo.frames_por_movimiento = frames_por_movimiento
                # Establecer la posición de la salida
                enemigo.set_salida(self.salida)
                self.enemigos.append(enemigo)
                break

    def generar_mapa(self):
        """Genera un laberinto aleatorio con bordes de muros"""
        
        self.MAP_COLS = MAP_COLS
        self.MAP_ROWS = MAP_ROWS

        # Inicializar todo como caminos
        mapa = [["P" for _ in range(MAP_COLS)] for _ in range(MAP_ROWS)]

        # Crear bordes de muros (marco exterior)
        for col in range(MAP_COLS):
            mapa[0][col] = "W"
            mapa[MAP_ROWS - 1][col] = "W"
        
        for fila in range(MAP_ROWS):
            mapa[fila][0] = "W"
            mapa[fila][MAP_COLS - 1] = "W"

        # Definir inicio y salida (dentro de los bordes)
        # Jugador empieza CERCA de la salida para interceptar enemigos
        salida_fila = random.randint(2, MAP_ROWS - 3)
        salida_col = MAP_COLS - 3
        
        # Jugador aparece cerca de la salida (entre 2-4 casillas)
        inicio_fila = salida_fila
        inicio_col = salida_col - random.randint(2, 4)

        # Guardar posiciones importantes
        self.inicio = (inicio_fila, inicio_col)
        self.salida = (salida_fila, salida_col)

        # Crear camino garantizado a la salida
        camino_garantizado = self.crear_camino_garantizado(inicio_fila, inicio_col, 
                                                            salida_fila, salida_col)

        # Agregar muros en patrón equilibrado
        self.agregar_muros_equilibrados(mapa, camino_garantizado)

        # Agregar lianas y túneles
        self.agregar_elementos_tacticos(mapa, camino_garantizado)

        # Asegurar que inicio y salida estén despejados
        mapa[inicio_fila][inicio_col] = "P"
        mapa[salida_fila][salida_col] = "E"

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
        num_muros_objetivo = int(celdas_interiores * random.uniform(0.30, 0.40))
        muros_colocados = 0

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
        
        # Calcular basado en celdas interiores de camino disponibles
        celdas_camino = 0
        for fila in range(1, MAP_ROWS - 1):
            for col in range(1, MAP_COLS - 1):
                if mapa[fila][col] == "P":
                    celdas_camino += 1

        num_lianas = int(celdas_camino * random.uniform(0.10, 0.15))
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