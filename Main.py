import pygame
import sys

# Inicializar Pygame
pygame.init()
pygame.mixer.init()

# Constantes
ANCHO_VENTANA = 800
ALTO_VENTANA = 600
FPS = 60

# Colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
VERDE_NEON = (57, 255, 20)
VERDE_CLARO = (144, 238, 144)
VERDE_OSCURO = (0, 100, 0)
ROJO_SANGRE = (139, 0, 0)

class Boton:
    def __init__(self, x, y, ancho, alto, texto, fuente):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.fuente = fuente
        self.hover = False
        
    def dibujar(self, ventana):
        # Fondo negro
        pygame.draw.rect(ventana, NEGRO, self.rect)
        
        # Borde blanco
        pygame.draw.rect(ventana, BLANCO, self.rect, 2)
        
        # Texto (blanco o verde claro según hover)
        color_texto = VERDE_CLARO if self.hover else BLANCO
        texto_surface = self.fuente.render(self.texto, True, color_texto)
        texto_rect = texto_surface.get_rect(center=self.rect.center)
        ventana.blit(texto_surface, texto_rect)
        
    def actualizar_hover(self, pos_mouse):
        self.hover = self.rect.collidepoint(pos_mouse)
        
    def es_clickeado(self, pos_mouse):
        return self.rect.collidepoint(pos_mouse)


class MainScreen:
    def __init__(self):
        self.ventana = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
        pygame.display.set_caption("Escapa del Laberinto")
        self.reloj = pygame.time.Clock()
        self.corriendo = True
        
        # Fuentes
        self.fuente_titulo = pygame.font.Font(None, 80)
        self.fuente_subtitulo = pygame.font.Font(None, 40)
        self.fuente_boton = pygame.font.Font(None, 36)
        
        # Cargar y reproducir música
        self.cargar_musica()
        
        # Crear botones
        self.crear_botones()
        
    def cargar_musica(self):
        """Carga y reproduce la música del menú principal"""
        try:
            pygame.mixer.music.load("OST/Main_Theme.mp3")
            pygame.mixer.music.set_volume(0.5)  # Volumen al 50%
            pygame.mixer.music.play(-1)  # -1 para reproducir en loop infinito
        except pygame.error as e:
            print(f"No se pudo cargar la música: {e}")
        
    def crear_botones(self):
        """Crea los botones del menú principal"""
        ancho_boton = 250
        alto_boton = 50
        x_centro = ANCHO_VENTANA // 2 - ancho_boton // 2
        y_inicial = 280
        espacio = 70
        
        self.btn_jugar = Boton(x_centro, y_inicial, ancho_boton, alto_boton, 
                               "Jugar", self.fuente_boton)
        self.btn_puntajes = Boton(x_centro, y_inicial + espacio, ancho_boton, alto_boton, 
                                  "Mejores Puntajes", self.fuente_boton)
        self.btn_ajustes = Boton(x_centro, y_inicial + espacio * 2, ancho_boton, alto_boton, 
                                 "Ajustes", self.fuente_boton)
        self.btn_salir = Boton(x_centro, y_inicial + espacio * 3, ancho_boton, alto_boton, 
                               "Salir", self.fuente_boton)
        
        self.botones = [self.btn_jugar, self.btn_puntajes, self.btn_ajustes, self.btn_salir]
        
    def dibujar_menu_principal(self):
        """Dibuja la pantalla principal del juego"""
        self.ventana.fill(NEGRO)
        
        # Título principal con efecto de sombra
        texto_sombra = self.fuente_titulo.render("ESCAPA DEL", True, ROJO_SANGRE)
        texto_titulo = self.fuente_titulo.render("ESCAPA DEL", True, VERDE_NEON)
        
        texto_sombra2 = self.fuente_titulo.render("LABERINTO", True, ROJO_SANGRE)
        texto_titulo2 = self.fuente_titulo.render("LABERINTO", True, VERDE_NEON)
        
        # Posicionar título centrado
        rect_titulo = texto_titulo.get_rect(center=(ANCHO_VENTANA // 2, 100))
        rect_titulo2 = texto_titulo2.get_rect(center=(ANCHO_VENTANA // 2, 170))
        
        # Dibujar sombra (desplazada)
        self.ventana.blit(texto_sombra, (rect_titulo.x + 3, rect_titulo.y + 3))
        self.ventana.blit(texto_sombra2, (rect_titulo2.x + 3, rect_titulo2.y + 3))
        
        # Dibujar título
        self.ventana.blit(texto_titulo, rect_titulo)
        self.ventana.blit(texto_titulo2, rect_titulo2)
        
        # Actualizar y dibujar botones
        pos_mouse = pygame.mouse.get_pos()
        for boton in self.botones:
            boton.actualizar_hover(pos_mouse)
            boton.dibujar(self.ventana)
        
        pygame.display.flip()
    
    def manejar_click(self, pos_mouse):
        """Maneja los clicks en los botones"""
        if self.btn_jugar.es_clickeado(pos_mouse):
            print("Jugar clickeado")
            # Aquí irá la lógica para iniciar el juego
            
        elif self.btn_puntajes.es_clickeado(pos_mouse):
            print("Mejores Puntajes clickeado")
            # Aquí irá la lógica para mostrar puntajes
            
        elif self.btn_ajustes.es_clickeado(pos_mouse):
            print("Ajustes clickeado")
            # Aquí irá la lógica para mostrar ajustes
            
        elif self.btn_salir.es_clickeado(pos_mouse):
            self.corriendo = False
    
    def ejecutar(self):
        """Loop principal del juego"""
        while self.corriendo:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.corriendo = False
                elif evento.type == pygame.MOUSEBUTTONDOWN:
                    if evento.button == 1:  # Click izquierdo
                        self.manejar_click(evento.pos)
                    
            self.dibujar_menu_principal()
            self.reloj.tick(FPS)
        
        pygame.quit()
        sys.exit()

# Punto de entrada del programa
if __name__ == "__main__":
    menu = MainScreen()
    menu.ejecutar()