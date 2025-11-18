import pygame
import random
from collections import deque

class Enemy:
    def __init__(self, fila, col, tile_size, modo="escape"):
        self.fila = fila
        self.col = col
        self.fila_spawn = fila
        self.col_spawn = col
        self.tile_size = tile_size
        self.modo = modo
        
        # Determinar rol según modo (opuesto al jugador)
        self.rol = "Hunter" if modo == "escape" else "Runner"
        
        # Velocidad
        self.velocidad = 1
        self.contador_movimiento = 0
        self.frames_por_movimiento = 8
        
        # Dirección actual
        self.direccion = "Down"
        
        # Sistema de animación
        self.frame_actual = 2  # Empezar en pose firme
        self.secuencia_animacion = [1, 2, 3, 2]
        self.indice_secuencia = 1
        
        # Cargar sprites
        self.sprites = self.cargar_sprites()
        
        # Estado (para sistema de trampas)
        self.vivo = True
        self.tiempo_muerte = None
        self.tiempo_reaparicion = 10.0
        
        # Pathfinding
        self.camino = []
        self.objetivo_anterior = None
        
        # Para modo Hunter
        self.salida_pos = None
        self.distancia_huida = 5
        
    def cargar_sprites(self):
        """Carga todos los sprites del enemigo según su rol"""
        sprites = {}
        direcciones = ["Up", "Down", "Left", "Right"]
        
        for direccion in direcciones:
            sprites[direccion] = []
            for num in [1, 2, 3]:
                ruta = f"ASSETS/SPRITES/Characters/{self.rol}/{self.rol} {direccion} {num}.png"
                try:
                    sprite = pygame.image.load(ruta)
                    sprite = pygame.transform.scale(sprite, (self.tile_size, self.tile_size))
                    sprites[direccion].append(sprite)
                except Exception as e:
                    print(f"Error al cargar sprite enemigo: {ruta} - {e}")
                    sprite = self.crear_sprite_respaldo()
                    sprites[direccion].append(sprite)
        
        return sprites
    
    def crear_sprite_respaldo(self):
        """Crea un sprite de respaldo si no se pueden cargar las imágenes"""
        superficie = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
        color = (255, 0, 0) if self.rol == "Hunter" else (0, 255, 0)
        pygame.draw.circle(superficie, color, 
                          (self.tile_size // 2, self.tile_size // 2), 
                          self.tile_size // 3)
        return superficie
    
    def set_salida(self, salida_pos):
        self.salida_pos = salida_pos
    
    def actualizar(self, jugador_pos, mapa, tiempo_actual):
        if not self.vivo:
            return
        
        # Incrementar contador de movimiento
        self.contador_movimiento += 1
        
        # Mover solo cada ciertos frames
        if self.contador_movimiento >= self.frames_por_movimiento:
            self.contador_movimiento = 0
            
            # Comportamiento según el modo
            if self.modo == "escape":
                # Modo Escape: perseguir al jugador
                self.mover_hacia_jugador(jugador_pos, mapa)
            elif self.modo == "hunter":
                # Modo Hunter: huir hacia la salida
                self.huir_hacia_salida(jugador_pos, mapa)
    
    def mover_hacia_jugador(self, jugador_pos, mapa):
        # Si el objetivo cambió, recalcular camino
        if jugador_pos != self.objetivo_anterior:
            self.camino = self.encontrar_camino_hacia_objetivo(jugador_pos, mapa)
            self.objetivo_anterior = jugador_pos
        
        # Si hay un camino, seguirlo
        if self.camino and len(self.camino) > 1:
            self.seguir_camino(mapa)
    
    def huir_hacia_salida(self, jugador_pos, mapa):
        if not self.salida_pos:
            return
        
        # Calcular distancia al jugador
        distancia_jugador = abs(self.fila - jugador_pos[0]) + abs(self.col - jugador_pos[1])
        
        # Si el jugador está muy cerca, priorizar huir
        if distancia_jugador <= self.distancia_huida:
            # Huir directamente del jugador
            self.camino = self.encontrar_camino_huyendo(jugador_pos, mapa)
        else:
            # Si el jugador está lejos, ir hacia la salida
            if self.salida_pos != self.objetivo_anterior:
                self.camino = self.encontrar_camino_hacia_objetivo(self.salida_pos, mapa)
                self.objetivo_anterior = self.salida_pos
        
        # Seguir el camino calculado
        if self.camino and len(self.camino) > 1:
            self.seguir_camino(mapa)
    
    def seguir_camino(self, mapa):
        siguiente = self.camino[1]
        nueva_fila, nueva_col = siguiente
        
        # Determinar dirección del movimiento
        if nueva_fila < self.fila:
            self.direccion = "Up"
        elif nueva_fila > self.fila:
            self.direccion = "Down"
        elif nueva_col < self.col:
            self.direccion = "Left"
        elif nueva_col > self.col:
            self.direccion = "Right"
        
        # Mover si es posible
        if self.puede_moverse(nueva_fila, nueva_col, mapa):
            # Detectar si realmente se movió a una nueva casilla
            if nueva_fila != self.fila or nueva_col != self.col:
                self.actualizar_animacion()
                
            self.fila = nueva_fila
            self.col = nueva_col
            self.camino.pop(0)
    
    def encontrar_camino_hacia_objetivo(self, objetivo, mapa):
        inicio = (self.fila, self.col)
        
        cola = deque([inicio])
        visitados = {inicio}
        padres = {inicio: None}
        
        while cola:
            actual = cola.popleft()
            
            if actual == objetivo:
                # Reconstruir camino
                camino = []
                while actual is not None:
                    camino.append(actual)
                    actual = padres[actual]
                return list(reversed(camino))
            
            # Explorar vecinos (4 direcciones)
            fila, col = actual
            for df, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nueva_fila = fila + df
                nueva_col = col + dc
                vecino = (nueva_fila, nueva_col)
                
                if vecino not in visitados and self.puede_moverse(nueva_fila, nueva_col, mapa):
                    visitados.add(vecino)
                    padres[vecino] = actual
                    cola.append(vecino)
        
        # Si no hay camino, quedarse quieto
        return [inicio]
    
    def encontrar_camino_huyendo(self, jugador_pos, mapa):
        inicio = (self.fila, self.col)
        mejor_movimiento = inicio
        max_distancia = 0
        
        # Evaluar las 4 direcciones posibles
        for df, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nueva_fila = self.fila + df
            nueva_col = self.col + dc
            
            if self.puede_moverse(nueva_fila, nueva_col, mapa):
                distancia = abs(nueva_fila - jugador_pos[0]) + abs(nueva_col - jugador_pos[1])
                
                # Elegir la dirección que más nos aleje del jugador
                if distancia > max_distancia:
                    max_distancia = distancia
                    mejor_movimiento = (nueva_fila, nueva_col)
        
        return [inicio, mejor_movimiento]
    
    def llego_a_salida(self):
        if self.modo == "hunter" and self.salida_pos:
            return (self.fila, self.col) == self.salida_pos
        return False
    
    def puede_moverse(self, fila, col, mapa):
        if fila < 0 or fila >= len(mapa) or col < 0 or col >= len(mapa[0]):
            return False
        
        tipo_casilla = mapa[fila][col]
        if self.modo == "escape":
            # Enemigos son HUNTERS: pueden pasar por P y L
            return tipo_casilla in ["P", "L"]
        elif self.modo == "hunter":
            # Enemigos son RUNNERS: pueden pasar por P, T y E (para escapar)
            return tipo_casilla in ["P", "T", "E"]
        
        return False
    
    def actualizar_animacion(self):
        """Actualiza el frame de animación del sprite (cambia con cada movimiento)"""
        self.indice_secuencia = (self.indice_secuencia + 1) % len(self.secuencia_animacion)
        self.frame_actual = self.secuencia_animacion[self.indice_secuencia]
    
    def colisiona_con_jugador(self, jugador_pos):
        return self.vivo and (self.fila, self.col) == jugador_pos
    
    def morir(self, tiempo_actual):
        self.vivo = False
        self.tiempo_muerte = tiempo_actual
    
    def puede_reaparecer(self, tiempo_actual):
        if self.vivo:
            return False
        
        if self.tiempo_muerte is None:
            return False
        
        return (tiempo_actual - self.tiempo_muerte) >= self.tiempo_reaparicion
    
    def reaparecer(self, nueva_fila, nueva_col):
        self.vivo = True
        self.fila = nueva_fila
        self.col = nueva_col
        self.tiempo_muerte = None
        self.camino = []
        self.objetivo_anterior = None
    
    def dibujar(self, ventana, margen_x, margen_y):
        if not self.vivo:
            return
        
        x = margen_x + (self.col * self.tile_size)
        y = margen_y + (self.fila * self.tile_size)
        
        sprite = self.sprites[self.direccion][self.frame_actual - 1]
        ventana.blit(sprite, (x, y))
    
    def get_posicion(self):
        """Retorna la posición actual del enemigo como tupla (fila, col)"""
        return (self.fila, self.col)