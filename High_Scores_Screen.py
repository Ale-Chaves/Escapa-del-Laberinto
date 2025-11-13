import pygame
import sys
import os

# Constantes
ANCHO_VENTANA = 800
ALTO_VENTANA = 600
FPS = 60

# Colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
VERDE_CLARO = (144, 238, 144)
NARANJA = (255, 165, 0)


# ---------------- Clase Botón ---------------- #
class Boton:
    def __init__(self, x, y, ancho, alto, texto, fuente):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.fuente = fuente
        self.hover = False
        
    def dibujar(self, ventana):
        pygame.draw.rect(ventana, NEGRO, self.rect)
        pygame.draw.rect(ventana, BLANCO, self.rect, 2)
        color_texto = VERDE_CLARO if self.hover else BLANCO
        texto_surface = self.fuente.render(self.texto, True, color_texto)
        texto_rect = texto_surface.get_rect(center=self.rect.center)
        ventana.blit(texto_surface, texto_rect)
        
    def actualizar_hover(self, pos_mouse):
        self.hover = self.rect.collidepoint(pos_mouse)
        
    def es_clickeado(self, pos_mouse):
        return self.rect.collidepoint(pos_mouse)


# ---------------- Pantalla de selección de modos ---------------- #
class HighScoresScreen:
    def __init__(self, ventana):
        self.ventana = ventana
        self.reloj = pygame.time.Clock()
        self.activo = True
        
        # Fuentes
        self.fuente_titulo = pygame.font.Font(None, 80)
        self.fuente_subtitulo = pygame.font.Font(None, 40)
        self.fuente_boton = pygame.font.Font(None, 36)
        
        # Crear botones
        self.crear_botones()
        
    def crear_botones(self):
        ancho_boton = 250
        alto_boton = 50
        x_centro = ANCHO_VENTANA // 2 - ancho_boton // 2
        y_inicial = 200
        espacio = 70
        
        self.btn_escapa = Boton(x_centro, y_inicial, ancho_boton, alto_boton, 
                                "Escapa", self.fuente_boton)
        self.btn_cazador = Boton(x_centro, y_inicial + espacio, ancho_boton, alto_boton, 
                                 "Cazador", self.fuente_boton)
        self.btn_volver = Boton(x_centro, y_inicial + espacio * 3, ancho_boton, alto_boton, 
                                "Volver", self.fuente_boton)
        
        self.botones = [self.btn_escapa, self.btn_cazador, self.btn_volver]
        
    def dibujar(self):
        self.ventana.fill(NEGRO)
        
        texto_titulo = self.fuente_titulo.render("MEJORES PUNTAJES", True, BLANCO)
        rect_titulo = texto_titulo.get_rect(center=(ANCHO_VENTANA // 2, 100))
        self.ventana.blit(texto_titulo, rect_titulo)
        
        texto_subtitulo = self.fuente_subtitulo.render("Selecciona el modo:", True, BLANCO)
        rect_subtitulo = texto_subtitulo.get_rect(center=(ANCHO_VENTANA // 2, 160))
        self.ventana.blit(texto_subtitulo, rect_subtitulo)
        
        pos_mouse = pygame.mouse.get_pos()
        for boton in self.botones:
            boton.actualizar_hover(pos_mouse)
            boton.dibujar(self.ventana)
        
        pygame.display.flip()
    
    def manejar_click(self, pos_mouse):
        if self.btn_escapa.es_clickeado(pos_mouse):
            pantalla_top = TopScoresScreen(self.ventana, "escape")
            pantalla_top.ejecutar()
            
        elif self.btn_cazador.es_clickeado(pos_mouse):
            pantalla_top = TopScoresScreen(self.ventana, "hunter")
            pantalla_top.ejecutar()
            
        elif self.btn_volver.es_clickeado(pos_mouse):
            self.activo = False
    
    def ejecutar(self):
        self.activo = True
        while self.activo:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    self.manejar_click(evento.pos)
                    
            self.dibujar()
            self.reloj.tick(FPS)


# ---------------- Pantalla de TOP 5 ---------------- #
class TopScoresScreen:
    def __init__(self, ventana, modo):
        self.ventana = ventana
        self.reloj = pygame.time.Clock()
        self.modo = modo
        self.activo = True
        
        self.fuente_titulo = pygame.font.Font(None, 80)
        self.fuente_texto = pygame.font.Font(None, 40)
        self.fuente_boton = pygame.font.Font(None, 36)
        
        self.archivo = f"high_scores_{self.modo}.txt"
        self.crear_archivo_si_no_existe()
        
        self.crear_botones()
        self.puntajes = self.cargar_puntajes()
        
    def crear_archivo_si_no_existe(self):
        """Crea el archivo de puntajes si no existe"""
        if not os.path.exists(self.archivo):
            with open(self.archivo, "w") as f:
                pass  # archivo vacío
            
    def cargar_puntajes(self):
        """Carga los puntajes desde el archivo"""
        with open(self.archivo, "r") as f:
            lineas = [line.strip() for line in f.readlines() if line.strip()]
        return lineas  # lista de strings (por ahora)
        
    def crear_botones(self):
        ancho_boton = 200
        alto_boton = 50
        x_centro = ANCHO_VENTANA // 2 - ancho_boton // 2
        y_pos = 520
        self.btn_volver = Boton(x_centro, y_pos, ancho_boton, alto_boton, "Volver", self.fuente_boton)
        
    def dibujar(self):
        self.ventana.fill(NEGRO)
        
        texto_titulo = self.fuente_titulo.render("TOP 5", True, BLANCO)
        rect_titulo = texto_titulo.get_rect(center=(ANCHO_VENTANA // 2, 80))
        self.ventana.blit(texto_titulo, rect_titulo)
        
        if not self.puntajes:
            texto_vacio = self.fuente_texto.render("No hay puntajes para mostrar", True, NARANJA)
            rect_vacio = texto_vacio.get_rect(center=(ANCHO_VENTANA // 2, ALTO_VENTANA // 2))
            self.ventana.blit(texto_vacio, rect_vacio)
        else:
            # Mostrar lista de puntajes
            for i, score in enumerate(self.puntajes[:5]):
                texto_puntaje = self.fuente_texto.render(f"{i+1}. {score}", True, BLANCO)
                rect_puntaje = texto_puntaje.get_rect(center=(ANCHO_VENTANA // 2, 180 + i * 60))
                self.ventana.blit(texto_puntaje, rect_puntaje)
        
        pos_mouse = pygame.mouse.get_pos()
        self.btn_volver.actualizar_hover(pos_mouse)
        self.btn_volver.dibujar(self.ventana)
        
        pygame.display.flip()
        
    def manejar_click(self, pos_mouse):
        if self.btn_volver.es_clickeado(pos_mouse):
            self.activo = False
        
    def ejecutar(self):
        self.activo = True
        while self.activo:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    self.manejar_click(evento.pos)
            
            self.dibujar()
            self.reloj.tick(FPS)
