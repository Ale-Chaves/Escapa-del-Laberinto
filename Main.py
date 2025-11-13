import pygame
import sys
from PIL import Image
from High_Scores_Screen import HighScoresScreen
from Settings_Screen import SettingsScreen
from Play import PlayScreen
from Music_Manager import reproducir_musica, detener_musica

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


class GifAnimado:
    def __init__(self, ruta_gif):
        self.frames = []
        self.frame_actual = 0
        self.tiempo_por_frame = 100
        self.ultimo_update = pygame.time.get_ticks()
        self.cargar_gif(ruta_gif)

    def cargar_gif(self, ruta_gif):
        try:
            gif = Image.open(ruta_gif)
            for frame_num in range(gif.n_frames):
                gif.seek(frame_num)
                frame = gif.convert("RGBA")
                frame = frame.resize((ANCHO_VENTANA, ALTO_VENTANA), Image.LANCZOS)
                modo = frame.mode
                tamaño = frame.size
                datos = frame.tobytes()
                py_frame = pygame.image.fromstring(datos, tamaño, modo)
                self.frames.append(py_frame)
        except Exception as e:
            print(f"Error al cargar GIF: {e}")
            frame_negro = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA))
            frame_negro.fill(NEGRO)
            self.frames.append(frame_negro)

    def actualizar(self):
        if len(self.frames) <= 1:
            return
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - self.ultimo_update > self.tiempo_por_frame:
            self.frame_actual = (self.frame_actual + 1) % len(self.frames)
            self.ultimo_update = tiempo_actual

    def dibujar(self, ventana):
        if self.frames:
            ventana.blit(self.frames[self.frame_actual], (0, 0))


class MainScreen:
    def __init__(self):
        self.ventana = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
        pygame.display.set_caption("Escapa del Laberinto")
        self.reloj = pygame.time.Clock()
        self.corriendo = True

        # Fuentes
        self.fuente_titulo = pygame.font.Font(None, 80)
        self.fuente_boton = pygame.font.Font(None, 36)

        # Fondo animado
        self.fondo_gif = GifAnimado("ASSETS/GIFS/BG_1.gif")

        # Música del menú
        self.cargar_musica()

        # Crear botones
        self.crear_botones()

    def cargar_musica(self):
        reproducir_musica("ASSETS/OST/Main_Theme.mp3")  # Reproducir música principal del menú

    def crear_botones(self):
        ancho_boton = 250
        alto_boton = 50
        x_centro = ANCHO_VENTANA // 2 - ancho_boton // 2
        y_inicial = 280
        espacio = 70

        self.btn_jugar = Boton(x_centro, y_inicial, ancho_boton, alto_boton, "Jugar", self.fuente_boton)
        self.btn_puntajes = Boton(x_centro, y_inicial + espacio, ancho_boton, alto_boton, "Mejores Puntajes", self.fuente_boton)
        self.btn_ajustes = Boton(x_centro, y_inicial + espacio * 2, ancho_boton, alto_boton, "Ajustes", self.fuente_boton)
        self.btn_salir = Boton(x_centro, y_inicial + espacio * 3, ancho_boton, alto_boton, "Salir", self.fuente_boton)

        self.botones = [self.btn_jugar, self.btn_puntajes, self.btn_ajustes, self.btn_salir]

    def dibujar_menu_principal(self):
        self.fondo_gif.actualizar()
        self.fondo_gif.dibujar(self.ventana)

        # Título con sombra
        texto_sombra = self.fuente_titulo.render("ESCAPA DEL", True, (40, 40, 40))
        texto_titulo = self.fuente_titulo.render("ESCAPA DEL", True, BLANCO)
        texto_sombra2 = self.fuente_titulo.render("LABERINTO", True, (40, 40, 40))
        texto_titulo2 = self.fuente_titulo.render("LABERINTO", True, BLANCO)

        rect_titulo = texto_titulo.get_rect(center=(ANCHO_VENTANA // 2, 100))
        rect_titulo2 = texto_titulo2.get_rect(center=(ANCHO_VENTANA // 2, 170))

        self.ventana.blit(texto_sombra, (rect_titulo.x + 4, rect_titulo.y + 4))
        self.ventana.blit(texto_sombra2, (rect_titulo2.x + 4, rect_titulo2.y + 4))
        self.ventana.blit(texto_titulo, rect_titulo)
        self.ventana.blit(texto_titulo2, rect_titulo2)

        pos_mouse = pygame.mouse.get_pos()
        for boton in self.botones:
            boton.actualizar_hover(pos_mouse)
            boton.dibujar(self.ventana)

        pygame.display.flip()

    def manejar_click(self, pos_mouse):
        if self.btn_jugar.es_clickeado(pos_mouse):
            # Al entrar a PlayScreen, detener música actual y reproducir Mode_Selection solo si no estaba ya en Play
            pantalla_play = PlayScreen(self.ventana)
            pantalla_play.ejecutar()
            # Al regresar de PlayScreen, detener Mode_Selection y volver a música principal
            detener_musica()
            reproducir_musica("ASSETS/OST/Main_Theme.mp3")

        elif self.btn_puntajes.es_clickeado(pos_mouse):
            pantalla_puntajes = HighScoresScreen(self.ventana)
            pantalla_puntajes.ejecutar()

        elif self.btn_ajustes.es_clickeado(pos_mouse):
            pantalla_ajustes = SettingsScreen(self.ventana)
            pantalla_ajustes.ejecutar()

        elif self.btn_salir.es_clickeado(pos_mouse):
            self.corriendo = False

    def ejecutar(self):
        while self.corriendo:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.corriendo = False
                elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    self.manejar_click(evento.pos)

            self.dibujar_menu_principal()
            self.reloj.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    menu = MainScreen()
    menu.ejecutar()
