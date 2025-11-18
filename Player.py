import pygame
import os

class Player:
    def __init__(self, fila_inicio, col_inicio, tile_size, modo="escape"):
        self.fila = fila_inicio
        self.col = col_inicio
        self.tile_size = tile_size
        self.modo = modo
        
        # Determinar rol según modo
        self.rol = "Runner" if modo == "escape" else "Hunter"
        
        # Velocidad
        self.velocidad_normal = 1
        self.velocidad_sprint = 2
        self.corriendo = False
        
        # Sistema de cooldown para balancear velocidad
        self.contador_movimiento = 0
        self.frames_movimiento_normal = 6
        self.frames_movimiento_sprint = 3
        
        # Dirección actual
        self.direccion = "Down"
        
        # Sistema de animación
        self.frame_actual = 2
        self.secuencia_animacion = [1, 2, 3, 2]
        self.indice_secuencia = 1
        
        # Posición anterior para detectar cambios
        self.fila_anterior = fila_inicio
        self.col_anterior = col_inicio
        
        # Cargar sprites
        self.sprites = self.cargar_sprites()
        
        # Estado
        self.en_movimiento = False
        self.llego_a_salida = False
        
    def cargar_sprites(self):
        """Carga todos los sprites del jugador según su rol"""
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
                    print(f"Error al cargar sprite: {ruta} - {e}")
                    # Crear sprite de respaldo (círculo de color)
                    sprite = self.crear_sprite_respaldo()
                    sprites[direccion].append(sprite)
        
        return sprites
    
    def crear_sprite_respaldo(self):
        """Crea un sprite de respaldo si no se pueden cargar las imágenes"""
        superficie = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
        color = (0, 100, 255) if self.rol == "Runner" else (255, 100, 0)
        pygame.draw.circle(superficie, color, 
                          (self.tile_size // 2, self.tile_size // 2), 
                          self.tile_size // 3)
        return superficie
    
    def mover(self, teclas, mapa, energy_bar):
        # Determinar si está corriendo (Shift presionado y tiene energía)
        self.corriendo = (teclas[pygame.K_LSHIFT] and energy_bar.energy > 0)
        
        # Determinar frames necesarios según si corre o no
        frames_requeridos = self.frames_movimiento_sprint if self.corriendo else self.frames_movimiento_normal
        
        # Incrementar contador
        self.contador_movimiento += 1
        
        # Solo permitir movimiento cuando el contador alcance el límite
        if self.contador_movimiento < frames_requeridos:
            return
        
        # Resetear contador
        self.contador_movimiento = 0
        
        # Determinar dirección y movimiento
        nueva_fila = self.fila
        nueva_col = self.col
        moviendo = False
        
        if teclas[pygame.K_w] or teclas[pygame.K_UP]:
            self.direccion = "Up"
            nueva_fila -= 1
            moviendo = True
        elif teclas[pygame.K_s] or teclas[pygame.K_DOWN]:
            self.direccion = "Down"
            nueva_fila += 1
            moviendo = True
        elif teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            self.direccion = "Left"
            nueva_col -= 1
            moviendo = True
        elif teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            self.direccion = "Right"
            nueva_col += 1
            moviendo = True
        
        self.en_movimiento = moviendo
        
        # Si se está moviendo, verificar colisión y actualizar posición
        if moviendo:
            if self.puede_moverse(nueva_fila, nueva_col, mapa):
                # Detectar si realmente se movió a una nueva casilla
                if nueva_fila != self.fila or nueva_col != self.col:
                    self.actualizar_animacion()
                    
                self.fila = nueva_fila
                self.col = nueva_col
                
                # Verificar si llegó a la salida
                if mapa[self.fila][self.col] == "E":
                    self.llego_a_salida = True
        else:
            # Si no se mueve, volver a pose firme
            self.frame_actual = 2
            self.indice_secuencia = 1
    
    def puede_moverse(self, fila, col, mapa):
        # Verificar límites del mapa
        if fila < 0 or fila >= len(mapa) or col < 0 or col >= len(mapa[0]):
            return False
        
        tipo_casilla = mapa[fila][col]
        
        if self.modo == "escape":
            # Jugador RUNNER: puede pasar por P, T y E
            return tipo_casilla in ["P", "T", "E"]
        elif self.modo == "hunter":
            # Jugador HUNTER: puede pasar por P y L (NO por túneles ni salida)
            return tipo_casilla in ["P", "L"]
        
        return False
    
    def actualizar_animacion(self):
        """Actualiza el frame de animación del sprite (cambia con cada movimiento)"""
        # Avanzar en la secuencia de animación con cada movimiento
        self.indice_secuencia = (self.indice_secuencia + 1) % len(self.secuencia_animacion)
        self.frame_actual = self.secuencia_animacion[self.indice_secuencia]
    
    def dibujar(self, ventana, margen_x, margen_y):
        x = margen_x + (self.col * self.tile_size)
        y = margen_y + (self.fila * self.tile_size)
        
        # Obtener sprite actual
        sprite = self.sprites[self.direccion][self.frame_actual - 1]
        ventana.blit(sprite, (x, y))
    
    def get_posicion(self):
        """Retorna la posición actual del jugador"""
        return (self.fila, self.col)
    
    def reset_posicion(self, fila, col):
        """Reinicia la posición del jugador"""
        self.fila = fila
        self.col = col
        self.llego_a_salida = False