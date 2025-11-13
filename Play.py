import pygame
import sys
from Player_Name import PlayerNameScreen
from Music_Manager import reproducir_musica

# Colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
VERDE_CLARO = (144, 238, 144)

ANCHO_VENTANA = 800
ALTO_VENTANA = 600
FPS = 60


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


class PlayScreen:
    def __init__(self, ventana):
        self.ventana = ventana
        self.reloj = pygame.time.Clock()
        self.corriendo = True

        self.fuente_titulo = pygame.font.Font(None, 72)
        self.fuente_boton = pygame.font.Font(None, 40)

        self.crear_botones()
        reproducir_musica("ASSETS/OST/Mode_Selection.mp3")

    def crear_botones(self):
        ancho_boton = 250
        alto_boton = 60
        x_centro = ANCHO_VENTANA // 2 - ancho_boton // 2
        y_inicial = 250
        espacio = 80

        self.btn_escape = Boton(x_centro, y_inicial, ancho_boton, alto_boton, "ESCAPE", self.fuente_boton)
        self.btn_cazador = Boton(x_centro, y_inicial + espacio, ancho_boton, alto_boton, "CAZADOR", self.fuente_boton)
        self.btn_volver = Boton(x_centro, y_inicial + espacio * 2, ancho_boton, alto_boton, "VOLVER", self.fuente_boton)

        self.botones = [self.btn_escape, self.btn_cazador, self.btn_volver]

    def dibujar(self):
        self.ventana.fill(NEGRO)

        # Título centrado
        texto_titulo = self.fuente_titulo.render("SELECCIONA EL MODO", True, BLANCO)
        rect_titulo = texto_titulo.get_rect(center=(ANCHO_VENTANA // 2, 120))
        self.ventana.blit(texto_titulo, rect_titulo)

        # Dibujar botones
        pos_mouse = pygame.mouse.get_pos()
        for boton in self.botones:
            boton.actualizar_hover(pos_mouse)
            boton.dibujar(self.ventana)

        pygame.display.flip()

    def manejar_click(self, pos_mouse):
        if self.btn_escape.es_clickeado(pos_mouse):
            pantalla_nombre = PlayerNameScreen(self.ventana, "ESCAPE")
            pantalla_nombre.ejecutar()

        elif self.btn_cazador.es_clickeado(pos_mouse):
            pantalla_nombre = PlayerNameScreen(self.ventana, "CAZADOR")
            pantalla_nombre.ejecutar()

        elif self.btn_volver.es_clickeado(pos_mouse):
            self.corriendo = False

    def ejecutar(self):
        while self.corriendo:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    self.manejar_click(evento.pos)

            self.dibujar()
            self.reloj.tick(FPS)
