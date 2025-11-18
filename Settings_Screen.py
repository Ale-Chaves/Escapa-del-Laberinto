import pygame
import sys
import json
import os

# --- Constantes ---
ANCHO_VENTANA = 800
ALTO_VENTANA = 600
FPS = 60

NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
VERDE_OSCURO = (0, 150, 0)
ROJO = (220, 20, 60)
GRIS = (100, 100, 100)

CONFIG_FILE = "settings.json"


class Boton:
    def __init__(self, x, y, ancho, alto, texto, fuente, color_activado, color_desactivado, activo=True):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.fuente = fuente
        self.color_activado = color_activado
        self.color_desactivado = color_desactivado
        self.activo = activo
        self.hover = False

    def dibujar(self, ventana):
        color_fondo = self.color_activado if self.activo else self.color_desactivado
        pygame.draw.rect(ventana, color_fondo, self.rect)
        pygame.draw.rect(ventana, BLANCO, self.rect, 2)

        color_texto = BLANCO if not self.hover else (144, 238, 144)
        texto_surface = self.fuente.render(self.texto, True, color_texto)
        texto_rect = texto_surface.get_rect(center=self.rect.center)
        ventana.blit(texto_surface, texto_rect)

    def actualizar_hover(self, pos_mouse):
        self.hover = self.rect.collidepoint(pos_mouse)

    def es_clickeado(self, pos_mouse):
        return self.rect.collidepoint(pos_mouse)


class Slider:
    def __init__(self, x, y, ancho, valor_inicial=5, min_val=0, max_val=10):
        self.x = x
        self.y = y
        self.ancho = ancho
        self.altura = 10
        self.min_val = min_val
        self.max_val = max_val
        self.valor = valor_inicial
        self.handle_x = x + (valor_inicial / max_val) * ancho
        self.arrastrando = False
        self.suelto = False

    def dibujar(self, ventana):
        pygame.draw.rect(ventana, GRIS, (self.x, self.y, self.ancho, self.altura))
        pygame.draw.circle(ventana, (144, 238, 144), (int(self.handle_x), self.y + self.altura // 2), 10)

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if abs(evento.pos[0] - self.handle_x) < 15 and abs(evento.pos[1] - (self.y + self.altura // 2)) < 15:
                self.arrastrando = True
        elif evento.type == pygame.MOUSEBUTTONUP:
            if self.arrastrando:
                self.suelto = True
            self.arrastrando = False
        elif evento.type == pygame.MOUSEMOTION and self.arrastrando:
            self.handle_x = max(self.x, min(evento.pos[0], self.x + self.ancho))
            self.valor = int(round(((self.handle_x - self.x) / self.ancho) * self.max_val))

    def establecer_valor(self, nuevo_valor):
        self.valor = nuevo_valor
        self.handle_x = self.x + (nuevo_valor / self.max_val) * self.ancho

    def obtener_valor(self):
        return self.valor


class SettingsScreen:
    def __init__(self, ventana):
        self.ventana = ventana
        self.reloj = pygame.time.Clock()
        self.activo = True

        pygame.mixer.init()

        # Fuentes
        self.fuente_titulo = pygame.font.Font(None, 80)
        self.fuente_texto = pygame.font.Font(None, 40)
        self.fuente_boton = pygame.font.Font(None, 36)

        # Cargar configuración
        self.config = self.cargar_configuracion()

        # Guardar volumen anterior para restaurar
        self.volumen_previo_musica = self.config["volumen_musica"]
        self.volumen_previo_efectos = self.config["volumen_efectos"]

        # Cargar sonido de prueba
        self.sonido_eliminated = pygame.mixer.Sound("ASSETS/SOUND EFFECTS/Eliminated.mp3")

        # Crear elementos
        self.crear_elementos()

    # --- Configuración guardada ---
    def cargar_configuracion(self):
        if not os.path.exists(CONFIG_FILE):
            config = {
                "musica_activada": True,
                "efectos_activados": True,
                "volumen_musica": 5,
                "volumen_efectos": 5
            }
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=4)
        else:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
        return config

    def guardar_configuracion(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=4)

    # --- Crear botones y sliders ---
    def crear_elementos(self):
        ancho_boton = 300
        alto_boton = 50
        x_centro = ANCHO_VENTANA // 2 - ancho_boton // 2

        self.btn_musica = Boton(
            x_centro, 200, ancho_boton, alto_boton,
            f"Música: {'Activada' if self.config['musica_activada'] else 'Desactivada'}",
            self.fuente_boton, VERDE_OSCURO, ROJO, self.config["musica_activada"]
        )

        self.slider_musica = Slider(x_centro, 270, 300, self.config["volumen_musica"])

        self.btn_efectos = Boton(
            x_centro, 360, ancho_boton, alto_boton,
            f"Efectos: {'Activados' if self.config['efectos_activados'] else 'Desactivados'}",
            self.fuente_boton, VERDE_OSCURO, ROJO, self.config["efectos_activados"]
        )

        self.slider_efectos = Slider(x_centro, 430, 300, self.config["volumen_efectos"])

        self.btn_volver = Boton(
            x_centro, 520, ancho_boton, alto_boton,
            "Volver", self.fuente_boton, NEGRO, NEGRO
        )

        self.botones = [self.btn_musica, self.btn_efectos, self.btn_volver]

    # --- Dibujar pantalla ---
    def dibujar(self):
        self.ventana.fill(NEGRO)

        titulo = self.fuente_titulo.render("CONFIGURACIÓN", True, BLANCO)
        self.ventana.blit(titulo, titulo.get_rect(center=(ANCHO_VENTANA // 2, 100)))

        pos_mouse = pygame.mouse.get_pos()
        for boton in self.botones:
            boton.actualizar_hover(pos_mouse)
            boton.dibujar(self.ventana)

        # Sliders y etiquetas
        self.slider_musica.dibujar(self.ventana)
        self.slider_efectos.dibujar(self.ventana)

        texto_musica = self.fuente_texto.render(f"Volumen Música: {self.slider_musica.obtener_valor()}", True, BLANCO)
        self.ventana.blit(texto_musica, (ANCHO_VENTANA // 2 - texto_musica.get_width() // 2, 310))

        texto_efectos = self.fuente_texto.render(f"Volumen Efectos: {self.slider_efectos.obtener_valor()}", True, BLANCO)
        self.ventana.blit(texto_efectos, (ANCHO_VENTANA // 2 - texto_efectos.get_width() // 2, 470))

        pygame.display.flip()

    # --- Manejo de clicks ---
    def manejar_click(self, pos_mouse):
        if self.btn_musica.es_clickeado(pos_mouse):
            self.config["musica_activada"] = not self.config["musica_activada"]
            self.btn_musica.activo = self.config["musica_activada"]
            self.btn_musica.texto = f"Música: {'Activada' if self.config['musica_activada'] else 'Desactivada'}"

            if self.config["musica_activada"]:
                valor_restaurado = self.volumen_previo_musica if self.volumen_previo_musica > 0 else 1
                self.slider_musica.establecer_valor(valor_restaurado)
                pygame.mixer.music.set_volume(valor_restaurado / 10)
            else:
                self.volumen_previo_musica = self.slider_musica.obtener_valor()
                self.slider_musica.establecer_valor(0)
                pygame.mixer.music.set_volume(0)

        elif self.btn_efectos.es_clickeado(pos_mouse):
            self.config["efectos_activados"] = not self.config["efectos_activados"]
            self.btn_efectos.activo = self.config["efectos_activados"]
            self.btn_efectos.texto = f"Efectos: {'Activados' if self.config['efectos_activados'] else 'Desactivados'}"

            if self.config["efectos_activados"]:
                valor_restaurado = self.volumen_previo_efectos if self.volumen_previo_efectos > 0 else 1
                self.slider_efectos.establecer_valor(valor_restaurado)
                self.sonido_eliminated.set_volume(valor_restaurado / 10)
                self.sonido_eliminated.play()
            else:
                self.volumen_previo_efectos = self.slider_efectos.obtener_valor()
                self.slider_efectos.establecer_valor(0)

        elif self.btn_volver.es_clickeado(pos_mouse):
            self.guardar_configuracion()
            self.activo = False

    # --- Bucle principal ---
    def ejecutar(self):
        self.activo = True
        while self.activo:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif evento.type == pygame.MOUSEBUTTONDOWN:
                    if evento.button == 1:
                        self.manejar_click(evento.pos)

                self.slider_musica.manejar_evento(evento)
                self.slider_efectos.manejar_evento(evento)

                # Detectar si se soltó el slider de efectos para reproducir el sonido
                if evento.type == pygame.MOUSEBUTTONUP and self.slider_efectos.suelto:
                    self.slider_efectos.suelto = False
                    if self.config["efectos_activados"] and self.slider_efectos.obtener_valor() > 0:
                        self.sonido_eliminated.set_volume(self.slider_efectos.obtener_valor() / 10)
                        self.sonido_eliminated.play()

            # Actualizar volúmenes en tiempo real
            musica_valor = self.slider_musica.obtener_valor()
            efectos_valor = self.slider_efectos.obtener_valor()

            # Música
            if musica_valor == 0 and self.config["musica_activada"]:
                self.config["musica_activada"] = False
                self.btn_musica.activo = False
                self.btn_musica.texto = "Música: Desactivada"
                pygame.mixer.music.set_volume(0)
                self.volumen_previo_musica = 1
            elif musica_valor > 0 and not self.config["musica_activada"]:
                self.config["musica_activada"] = True
                self.btn_musica.activo = True
                self.btn_musica.texto = "Música: Activada"

            # Efectos
            if efectos_valor == 0 and self.config["efectos_activados"]:
                self.config["efectos_activados"] = False
                self.btn_efectos.activo = False
                self.btn_efectos.texto = "Efectos: Desactivados"
                self.volumen_previo_efectos = 1
            elif efectos_valor > 0 and not self.config["efectos_activados"]:
                self.config["efectos_activados"] = True
                self.btn_efectos.activo = True
                self.btn_efectos.texto = "Efectos: Activados"

            self.config["volumen_musica"] = musica_valor
            self.config["volumen_efectos"] = efectos_valor

            if self.config["musica_activada"]:
                pygame.mixer.music.set_volume(musica_valor / 10)
            else:
                pygame.mixer.music.set_volume(0)

            self.dibujar()
            self.reloj.tick(FPS)

        self.guardar_configuracion()
