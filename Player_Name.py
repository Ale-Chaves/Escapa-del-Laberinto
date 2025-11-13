import pygame
import sys
from Hunter_Mode import HunterMode
from Escape_Mode import EscapeMode
from Music_Manager import reproducir_musica, detener_musica

# Colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
VERDE_CLARO = (144, 238, 144)
GRIS = (80, 80, 80)

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
        color_borde = VERDE_CLARO if self.hover else BLANCO
        pygame.draw.rect(ventana, NEGRO, self.rect)
        pygame.draw.rect(ventana, color_borde, self.rect, 2)
        texto_surface = self.fuente.render(self.texto, True, color_borde)
        texto_rect = texto_surface.get_rect(center=self.rect.center)
        ventana.blit(texto_surface, texto_rect)

    def actualizar_hover(self, pos_mouse):
        self.hover = self.rect.collidepoint(pos_mouse)

    def es_clickeado(self, pos_mouse):
        return self.rect.collidepoint(pos_mouse)


class PlayerNameScreen:
    def __init__(self, ventana, modo):
        self.ventana = ventana
        self.modo = modo  # "ESCAPE" o "CAZADOR"
        self.reloj = pygame.time.Clock()
        self.corriendo = True

        self.fuente_titulo = pygame.font.Font(None, 70)
        self.fuente_texto = pygame.font.Font(None, 50)
        self.fuente_boton = pygame.font.Font(None, 40)

        # Entrada de texto
        self.nombre = ""
        self.input_rect = pygame.Rect(ANCHO_VENTANA // 2 - 200, 260, 400, 60)
        self.input_activo = False

        # Botones
        self.btn_volver = Boton(ANCHO_VENTANA // 2 - 125, 450, 250, 60, "VOLVER", self.fuente_boton)
        self.btn_jugar = Boton(ANCHO_VENTANA // 2 - 125, 360, 250, 60, "JUGAR", self.fuente_boton)

        reproducir_musica("ASSETS/OST/Mode_Selection.mp3")

    def dibujar(self):
        self.ventana.fill(NEGRO)

        # Título
        titulo = f"Modo {self.modo}"
        texto_titulo = self.fuente_titulo.render(titulo, True, BLANCO)
        rect_titulo = texto_titulo.get_rect(center=(ANCHO_VENTANA // 2, 130))
        self.ventana.blit(texto_titulo, rect_titulo)

        # Etiqueta del input
        etiqueta = self.fuente_texto.render("Ingresa tu nombre:", True, BLANCO)
        rect_etiqueta = etiqueta.get_rect(center=(ANCHO_VENTANA // 2, 220))
        self.ventana.blit(etiqueta, rect_etiqueta)

        # Caja de texto
        color_borde = VERDE_CLARO if self.input_activo else GRIS
        pygame.draw.rect(self.ventana, color_borde, self.input_rect, 3)

        # Texto dentro de la caja
        texto_surface = self.fuente_texto.render(self.nombre, True, BLANCO)
        self.ventana.blit(texto_surface, (self.input_rect.x + 10, self.input_rect.y + 10))

        # Mostrar botón "JUGAR" solo si el nombre no está vacío
        pos_mouse = pygame.mouse.get_pos()
        self.btn_volver.actualizar_hover(pos_mouse)
        self.btn_volver.dibujar(self.ventana)

        if self.nombre.strip() != "":
            self.btn_jugar.actualizar_hover(pos_mouse)
            self.btn_jugar.dibujar(self.ventana)

        pygame.display.flip()

    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if self.input_rect.collidepoint(evento.pos):
                    self.input_activo = True
                else:
                    self.input_activo = False

                if self.btn_volver.es_clickeado(evento.pos):
                    self.corriendo = False

                if self.nombre.strip() != "" and self.btn_jugar.es_clickeado(evento.pos):
                    detener_musica()
                    if self.modo == "CAZADOR":
                        juego = HunterMode(self.ventana, self.nombre)
                        juego.ejecutar()
                    elif self.modo == "ESCAPE":
                        juego = EscapeMode(self.ventana, self.nombre)
                        juego.ejecutar()
                    self.corriendo = False

            elif evento.type == pygame.KEYDOWN and self.input_activo:
                if evento.key == pygame.K_BACKSPACE:
                    self.nombre = self.nombre[:-1]
                elif evento.key == pygame.K_RETURN:
                    if self.nombre.strip() != "":
                        print(f"Jugador '{self.nombre}' iniciando modo {self.modo}")
                        self.corriendo = False
                else:
                    if len(self.nombre) < 15:
                        self.nombre += evento.unicode

    def ejecutar(self):
        while self.corriendo:
            self.manejar_eventos()
            self.dibujar()
            self.reloj.tick(FPS)
