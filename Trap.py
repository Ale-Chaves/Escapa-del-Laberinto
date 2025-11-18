import pygame

class Trap:
    def __init__(self, fila, col, tile_size):
        self.fila = fila
        self.col = col
        self.tile_size = tile_size
        
        # Estado de la trampa
        self.activa = True
        self.animando = False
        self.debe_desaparecer = False
        
        # Sistema de animación
        self.frame_actual = 1
        self.sprites = self.cargar_sprites()
        
        # Animación de activación
        self.secuencia_activacion = [1, 2, 3, 4, 5, 5, 4, 3, 2, 1]
        self.indice_animacion = 0
        self.contador_frames = 0
        self.frames_por_sprite = 2
        
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
            (self.tile_size // 2, 5),
            (self.tile_size - 5, self.tile_size - 5),
            (5, self.tile_size - 5)
        ]
        pygame.draw.polygon(superficie, (255, 0, 0), puntos)
        pygame.draw.polygon(superficie, (200, 0, 0), puntos, 2)
        return superficie
    
    def activar(self):
        """Activa la trampa (inicia la animación de activación)"""
        if not self.animando:
            self.animando = True
            self.activa = False
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
            
            # Si la animación terminó
            if self.indice_animacion >= len(self.secuencia_activacion):
                self.debe_desaparecer = True
                self.animando = False
                return
            
            # Actualizar frame según la secuencia
            self.frame_actual = self.secuencia_activacion[self.indice_animacion]
    
    def colisiona_con_enemigo(self, enemigo_pos):
        return self.activa and (self.fila, self.col) == enemigo_pos
    
    def dibujar(self, ventana, margen_x, margen_y):
        if self.debe_desaparecer:
            return
        
        x = margen_x + (self.col * self.tile_size)
        y = margen_y + (self.fila * self.tile_size)
        
        # Obtener sprite actual
        sprite = self.sprites[self.frame_actual - 1]
        ventana.blit(sprite, (x, y))
    
    def get_posicion(self):
        """Retorna la posición de la trampa"""
        return (self.fila, self.col)


class TrapManager:
    def __init__(self, max_trampas=3, cooldown=5.0):
        self.trampas = []
        self.max_trampas = max_trampas
        self.cooldown = cooldown
        self.ultimo_uso = 0
        
    def puede_colocar_trampa(self, tiempo_actual):
        return tiempo_actual - self.ultimo_uso >= self.cooldown
    
    def colocar_trampa(self, fila, col, tile_size, tiempo_actual):
        if not self.puede_colocar_trampa(tiempo_actual):
            return False
        
        # Verificar que no haya ya una trampa en esa posición
        for trampa in self.trampas:
            if (trampa.activa or trampa.animando) and trampa.get_posicion() == (fila, col):
                return False
        
        # Si hay 3 o más trampas activas/animando, eliminar la más antigua
        trampas_existentes = [t for t in self.trampas if (t.activa or t.animando)]
        if len(trampas_existentes) >= self.max_trampas:
            # Eliminar la primera trampa (la más antigua)
            trampa_antigua = trampas_existentes[0]
            trampa_antigua.debe_desaparecer = True
        
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
        
        # Eliminar trampas que terminaron su animación
        trampas_antes = len(self.trampas)
        self.trampas = [t for t in self.trampas if not t.debe_desaparecer]
        
        # Si se eliminó alguna trampa, reiniciar cooldown
        if len(self.trampas) < trampas_antes:
            import pygame
            self.ultimo_uso = pygame.time.get_ticks() / 1000
    
    def verificar_colisiones(self, enemigos, tiempo_actual):
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
        for trampa in self.trampas:
            trampa.dibujar(ventana, margen_x, margen_y)
    
    def get_cooldown_restante(self, tiempo_actual):
        tiempo_restante = self.cooldown - (tiempo_actual - self.ultimo_uso)
        return max(0, tiempo_restante)
    
    def get_trampas_activas(self):
        """Retorna el número de trampas activas (sin contar las que están animando)"""
        return sum(1 for t in self.trampas if t.activa)