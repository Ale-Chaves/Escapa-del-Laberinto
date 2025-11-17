import pygame
import random
from collections import deque

class Enemy:
    def __init__(self, fila, col, tile_size, modo="escape"):
        """
        Inicializa un enemigo
        
        Args:
            fila: Fila inicial en el mapa
            col: Columna inicial en el mapa
            tile_size: Tamaño de cada casilla (25px)
            modo: "escape" o "hunter" para determinar comportamiento
        """
        self.fila = fila
        self.col = col
        self.fila_spawn = fila  # Guardar posición de spawn
        self.col_spawn = col
        self.tile_size = tile_size
        self.modo = modo
        
        # Determinar rol según modo (opuesto al jugador)
        self.rol = "Hunter" if modo == "escape" else "Runner"
        
        # Velocidad (más lenta que el jugador)
        self.velocidad = 1
        self.contador_movimiento = 0
        self.frames_por_movimiento = 8  # Esperar 8 frames antes de moverse
        
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
        
        # NUEVO: Para modo Hunter
        self.salida_pos = None  # Se establecerá desde Hunter_Mode
        self.distancia_huida = 5  # Casillas mínimas para mantener del jugador
        
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
        """
        Establece la posición de la salida (para modo Hunter)
        
        Args:
            salida_pos: Tupla (fila, col) de la salida
        """
        self.salida_pos = salida_pos
    
    def actualizar(self, jugador_pos, mapa, tiempo_actual):
        """
        Actualiza el estado del enemigo
        
        Args:
            jugador_pos: Tupla (fila, col) de la posición del jugador
            mapa: Matriz del mapa
            tiempo_actual: Tiempo actual en segundos (pygame.time.get_ticks() / 1000)
        """
        if not self.vivo:
            return
        
        # Incrementar contador de movimiento
        self.contador_movimiento += 1
        
        # Mover solo cada ciertos frames (para que sea más lento)
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
        """
        Mueve al enemigo hacia el jugador (MODO ESCAPE)
        
        Args:
            jugador_pos: Tupla (fila, col) del jugador
            mapa: Matriz del mapa
        """
        # Si el objetivo cambió, recalcular camino
        if jugador_pos != self.objetivo_anterior:
            self.camino = self.encontrar_camino_hacia_objetivo(jugador_pos, mapa)
            self.objetivo_anterior = jugador_pos
        
        # Si hay un camino, seguirlo
        if self.camino and len(self.camino) > 1:
            self.seguir_camino(mapa)
    
    def huir_hacia_salida(self, jugador_pos, mapa):
        """
        Mueve al enemigo hacia la salida, evitando al jugador (MODO HUNTER)
        
        Args:
            jugador_pos: Tupla (fila, col) del jugador
            mapa: Matriz del mapa
        """
        if not self.salida_pos:
            return  # No hacer nada si no hay salida definida
        
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
        """
        Sigue el camino calculado
        
        Args:
            mapa: Matriz del mapa
        """
        siguiente = self.camino[1]  # [0] es la posición actual
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
            self.camino.pop(0)  # Eliminar posición actual del camino
    
    def encontrar_camino_hacia_objetivo(self, objetivo, mapa):
        """
        Encuentra el camino más corto hacia un objetivo usando BFS
        
        Args:
            objetivo: Tupla (fila, col) del objetivo
            mapa: Matriz del mapa
            
        Returns:
            Lista de tuplas (fila, col) representando el camino
        """
        inicio = (self.fila, self.col)
        
        # BFS
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
        """
        Encuentra un camino alejándose del jugador (MODO HUNTER)
        
        Args:
            jugador_pos: Tupla (fila, col) del jugador
            mapa: Matriz del mapa
            
        Returns:
            Lista con el mejor movimiento para huir
        """
        inicio = (self.fila, self.col)
        mejor_movimiento = inicio
        max_distancia = 0
        
        # Evaluar las 4 direcciones posibles
        for df, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nueva_fila = self.fila + df
            nueva_col = self.col + dc
            
            if self.puede_moverse(nueva_fila, nueva_col, mapa):
                # Calcular distancia Manhattan desde esta posición al jugador
                distancia = abs(nueva_fila - jugador_pos[0]) + abs(nueva_col - jugador_pos[1])
                
                # Elegir la dirección que más nos aleje del jugador
                if distancia > max_distancia:
                    max_distancia = distancia
                    mejor_movimiento = (nueva_fila, nueva_col)
        
        return [inicio, mejor_movimiento]
    
    def llego_a_salida(self):
        """
        Verifica si el enemigo llegó a la salida (para modo Hunter)
        
        Returns:
            bool: True si está en la salida
        """
        if self.modo == "hunter" and self.salida_pos:
            return (self.fila, self.col) == self.salida_pos
        return False
    
    def puede_moverse(self, fila, col, mapa):
        """
        Verifica si el enemigo puede moverse a una casilla
        
        Args:
            fila: Fila destino
            col: Columna destino
            mapa: Matriz del mapa
            
        Returns:
            bool: True si puede moverse, False si no
        """
        # Verificar límites
        if fila < 0 or fila >= len(mapa) or col < 0 or col >= len(mapa[0]):
            return False
        
        tipo_casilla = mapa[fila][col]
        
        # ROLES INVERTIDOS:
        # Modo Escape: Enemigos son HUNTERS (Camino + Lianas)
        # Modo Hunter: Enemigos son RUNNERS (Camino + Túneles + Salida)
        
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
        """
        Verifica si el enemigo colisiona con el jugador
        
        Args:
            jugador_pos: Tupla (fila, col) del jugador
            
        Returns:
            bool: True si hay colisión
        """
        return self.vivo and (self.fila, self.col) == jugador_pos
    
    def morir(self, tiempo_actual):
        """
        Mata al enemigo (por trampa en modo Escape)
        
        Args:
            tiempo_actual: Tiempo actual en segundos
        """
        self.vivo = False
        self.tiempo_muerte = tiempo_actual
        print(f"Enemigo en ({self.fila}, {self.col}) eliminado por trampa")
    
    def puede_reaparecer(self, tiempo_actual):
        """
        Verifica si el enemigo puede reaparecer (solo para modo Escape con trampas)
        
        Args:
            tiempo_actual: Tiempo actual en segundos
            
        Returns:
            bool: True si ya pasaron 10 segundos desde su muerte
        """
        if self.vivo:
            return False
        
        if self.tiempo_muerte is None:
            return False
        
        return (tiempo_actual - self.tiempo_muerte) >= self.tiempo_reaparicion
    
    def reaparecer(self, nueva_fila, nueva_col):
        """
        Reaparece al enemigo en una nueva posición
        
        Args:
            nueva_fila: Nueva fila donde aparecerá
            nueva_col: Nueva columna donde aparecerá
        """
        self.vivo = True
        self.fila = nueva_fila
        self.col = nueva_col
        self.tiempo_muerte = None
        self.camino = []
        self.objetivo_anterior = None
        print(f"Enemigo reaparecido en ({nueva_fila}, {nueva_col})")
    
    def dibujar(self, ventana, margen_x, margen_y):
        """
        Dibuja el enemigo en pantalla
        
        Args:
            ventana: Superficie de pygame donde dibujar
            margen_x: Margen izquierdo del mapa
            margen_y: Margen superior del mapa
        """
        if not self.vivo:
            return  # No dibujar si está muerto
        
        x = margen_x + (self.col * self.tile_size)
        y = margen_y + (self.fila * self.tile_size)
        
        sprite = self.sprites[self.direccion][self.frame_actual - 1]
        ventana.blit(sprite, (x, y))
    
    def get_posicion(self):
        """Retorna la posición actual del enemigo como tupla (fila, col)"""
        return (self.fila, self.col)