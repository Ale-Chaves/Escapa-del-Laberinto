import pygame

class Trap:
    def __init__(self, fila, col, tile_size):
        """
        Inicializa una trampa
        
        Args:
            fila: Fila en el mapa donde se coloca
            col: Columna en el mapa donde se coloca
            tile_size: Tamaño de cada casilla (25px)
        """
        self.fila = fila
        self.col = col
        self.tile_size = tile_size
        
        # Estado de la trampa
        self.activa = True
        self.animando = False  # Si está en animación de activación
        self.debe_desaparecer = False  # NUEVO: marca para eliminación
        
        # Sistema de animación
        self.frame_actual = 1  # Frame inicial (Trap 1)
        self.sprites = self.cargar_sprites()
        
        # Animación de activación
        self.secuencia_activacion = [1, 2, 3, 4, 5, 5, 4, 3, 2, 1]  # 1→5→1
        self.indice_animacion = 0
        self.contador_frames = 0
        self.frames_por_sprite = 2  # Velocidad de la animación (más rápido)
        
    def cargar_sprites(self):
        """Carga los sprites de la trampa (Trap 1 a Trap 5)"""
        sprites = []
        
        for num in range(1, 6):
            ruta = f"ASSETS/SPRITES/Trap/Trap {num}.png"
            try:
                sprite = pygame.image.load(ruta)
                sprite = pygame.transform.scale(sprite, (self.tile_size, self.tile_size))
                sprites.append(sprite)
            except Exception as e:
                print(f"Error al cargar sprite trampa: {ruta} - {e}")
                # Sprite de respaldo (triángulo rojo)
                sprite = self.crear_sprite_respaldo()
                sprites.append(sprite)
        
        return sprites
    
    def crear_sprite_respaldo(self):
        """Crea un sprite de respaldo si no se pueden cargar las imágenes"""
        superficie = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
        # Dibujar un triángulo rojo (señal de peligro)
        puntos = [
            (self.tile_size // 2, 5),  # Arriba
            (self.tile_size - 5, self.tile_size - 5),  # Abajo derecha
            (5, self.tile_size - 5)  # Abajo izquierda
        ]
        pygame.draw.polygon(superficie, (255, 0, 0), puntos)
        pygame.draw.polygon(superficie, (200, 0, 0), puntos, 2)
        return superficie
    
    def activar(self):
        """Activa la trampa (inicia la animación de activación)"""
        if not self.animando:
            self.animando = True
            self.activa = False  # Ya no está activa para detectar colisiones
            self.indice_animacion = 0
    
    def actualizar(self):
        """Actualiza el estado de la trampa (animación)"""
        if not self.animando:
            return
        
        # Actualizar animación
        self.contador_frames += 1
        
        if self.contador_frames >= self.frames_por_sprite:
            self.contador_frames = 0
            self.indice_animacion += 1
            
            # Si la animación terminó (llegó al final: 1→5→1)
            if self.indice_animacion >= len(self.secuencia_activacion):
                self.debe_desaparecer = True  # Marcar para eliminación
                self.animando = False
                return
            
            # Actualizar frame según la secuencia
            self.frame_actual = self.secuencia_activacion[self.indice_animacion]
    
    def colisiona_con_enemigo(self, enemigo_pos):
        """
        Verifica si un enemigo está en la misma posición que la trampa
        
        Args:
            enemigo_pos: Tupla (fila, col) del enemigo
            
        Returns:
            bool: True si hay colisión
        """
        return self.activa and (self.fila, self.col) == enemigo_pos
    
    def dibujar(self, ventana, margen_x, margen_y):
        """
        Dibuja la trampa en pantalla
        
        Args:
            ventana: Superficie de pygame donde dibujar
            margen_x: Margen izquierdo del mapa
            margen_y: Margen superior del mapa
        """
        if self.debe_desaparecer:
            return  # No dibujar si ya debe desaparecer
        
        x = margen_x + (self.col * self.tile_size)
        y = margen_y + (self.fila * self.tile_size)
        
        # Obtener sprite actual (frame_actual - 1 porque los índices empiezan en 0)
        sprite = self.sprites[self.frame_actual - 1]
        ventana.blit(sprite, (x, y))
    
    def get_posicion(self):
        """Retorna la posición de la trampa"""
        return (self.fila, self.col)


class TrapManager:
    def __init__(self, max_trampas=3, cooldown=5.0):
        """
        Administrador de trampas
        
        Args:
            max_trampas: Número máximo de trampas activas simultáneamente
            cooldown: Tiempo de reutilización en segundos
        """
        self.trampas = []
        self.max_trampas = max_trampas
        self.cooldown = cooldown
        self.ultimo_uso = 0  # Timestamp del último uso
        
    def puede_colocar_trampa(self, tiempo_actual):
        """
        Verifica si se puede colocar una trampa nueva
        
        Args:
            tiempo_actual: Tiempo actual en segundos (pygame.time.get_ticks() / 1000)
            
        Returns:
            bool: True si puede colocar trampa
        """
        # MODIFICADO: Solo verificar cooldown, el límite se maneja automáticamente
        return tiempo_actual - self.ultimo_uso >= self.cooldown
    
    def colocar_trampa(self, fila, col, tile_size, tiempo_actual):
        """
        Coloca una trampa nueva en el mapa
        
        Args:
            fila: Fila donde colocar la trampa
            col: Columna donde colocar la trampa
            tile_size: Tamaño de casilla
            tiempo_actual: Tiempo actual en segundos
            
        Returns:
            bool: True si se colocó correctamente
        """
        if not self.puede_colocar_trampa(tiempo_actual):
            return False
        
        # Verificar que no haya ya una trampa en esa posición
        for trampa in self.trampas:
            if (trampa.activa or trampa.animando) and trampa.get_posicion() == (fila, col):
                return False
        
        # NUEVO: Si hay 3 o más trampas activas/animando, eliminar la más antigua
        trampas_existentes = [t for t in self.trampas if (t.activa or t.animando)]
        if len(trampas_existentes) >= self.max_trampas:
            # Eliminar la primera trampa (la más antigua)
            trampa_antigua = trampas_existentes[0]
            trampa_antigua.debe_desaparecer = True
            print(f"Trampa antigua en {trampa_antigua.get_posicion()} eliminada (límite de {self.max_trampas})")
        
        # Colocar trampa
        nueva_trampa = Trap(fila, col, tile_size)
        self.trampas.append(nueva_trampa)
        self.ultimo_uso = tiempo_actual
        return True
    
    def actualizar(self):
        """Actualiza todas las trampas (animaciones) y limpia las que deben desaparecer"""
        # Actualizar cada trampa
        for trampa in self.trampas:
            trampa.actualizar()
        
        # MODIFICADO: Eliminar trampas que terminaron su animación
        trampas_antes = len(self.trampas)
        self.trampas = [t for t in self.trampas if not t.debe_desaparecer]
        
        # Si se eliminó alguna trampa, reiniciar cooldown
        if len(self.trampas) < trampas_antes:
            import pygame
            self.ultimo_uso = pygame.time.get_ticks() / 1000
            print(f"Trampa desapareció. Cooldown reiniciado. Trampas activas: {self.get_trampas_activas()}")
    
    def verificar_colisiones(self, enemigos, tiempo_actual):
        """
        Verifica colisiones entre trampas y enemigos
        
        Args:
            enemigos: Lista de enemigos
            tiempo_actual: Tiempo actual en segundos
            
        Returns:
            int: Número de enemigos eliminados
        """
        enemigos_eliminados = 0
        
        for trampa in self.trampas:
            if not trampa.activa or trampa.animando:
                continue
            
            for enemigo in enemigos:
                if enemigo.vivo and trampa.colisiona_con_enemigo(enemigo.get_posicion()):
                    # Activar trampa (animación)
                    trampa.activar()
                    
                    # Eliminar enemigo
                    enemigo.morir(tiempo_actual)
                    enemigos_eliminados += 1
                    
                    break  # Una trampa solo elimina un enemigo
        
        return enemigos_eliminados
    
    def dibujar(self, ventana, margen_x, margen_y):
        """
        Dibuja todas las trampas activas
        
        Args:
            ventana: Superficie de pygame
            margen_x: Margen izquierdo del mapa
            margen_y: Margen superior del mapa
        """
        for trampa in self.trampas:
            trampa.dibujar(ventana, margen_x, margen_y)
    
    def get_cooldown_restante(self, tiempo_actual):
        """
        Obtiene el tiempo de cooldown restante
        
        Args:
            tiempo_actual: Tiempo actual en segundos
            
        Returns:
            float: Segundos restantes de cooldown (0 si ya puede colocar)
        """
        tiempo_restante = self.cooldown - (tiempo_actual - self.ultimo_uso)
        return max(0, tiempo_restante)
    
    def get_trampas_activas(self):
        """Retorna el número de trampas activas (sin contar las que están animando)"""
        return sum(1 for t in self.trampas if t.activa)