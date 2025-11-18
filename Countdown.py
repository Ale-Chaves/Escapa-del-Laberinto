import pygame
import time

class Countdown:
    """Cuenta regresiva 3-2-1-GO! antes de iniciar el juego"""
    
    def __init__(self, ventana, ancho_ventana, alto_ventana):
        self.ventana = ventana
        self.ancho_ventana = ancho_ventana
        self.alto_ventana = alto_ventana
        
        # Fuente dorada para los números
        self.fuente_grande = pygame.font.Font(None, 200)
        self.color_dorado = (255, 215, 0)
        
        # Secuencia de cuenta regresiva
        self.secuencia = ["3", "2", "1", "GO!"]
        self.duracion_por_numero = 1.0
        
    def dibujar_numero(self, texto):
        # Crear texto con sombra para efecto 3D
        texto_sombra = self.fuente_grande.render(texto, True, (100, 80, 0))
        texto_principal = self.fuente_grande.render(texto, True, self.color_dorado)
        
        # Centrar texto
        rect_texto = texto_principal.get_rect(center=(self.ancho_ventana // 2, self.alto_ventana // 2))
        rect_sombra = rect_texto.copy()
        rect_sombra.x += 5
        rect_sombra.y += 5
        
        # Dibujar sombra primero, luego texto principal
        self.ventana.blit(texto_sombra, rect_sombra)
        self.ventana.blit(texto_principal, rect_texto)
    
    def ejecutar(self, callback_dibujar_fondo):
        for numero in self.secuencia:
            tiempo_inicio = time.time()
            
            while time.time() - tiempo_inicio < self.duracion_por_numero:
                # Verificar eventos
                for evento in pygame.event.get():
                    if evento.type == pygame.QUIT:
                        return False
                    elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                        return False
                
                # Dibujar fondo (el juego congelado)
                callback_dibujar_fondo()
                
                # Dibujar número de cuenta regresiva encima
                self.dibujar_numero(numero)
                
                pygame.display.flip()
                pygame.time.Clock().tick(60)
        
        return True