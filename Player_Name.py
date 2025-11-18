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


class Slider:
    def __init__(self, x, y, ancho, valor_inicial=2, min_val=1, max_val=4):
        self.x = x
        self.y = y
        self.ancho = ancho
        self.altura = 10
        self.min_val = min_val
        self.max_val = max_val
        self.valor = valor_inicial
        self.handle_x = x + ((valor_inicial - min_val) / (max_val - min_val)) * ancho
        self.arrastrando = False

    def dibujar(self, ventana):
        pygame.draw.rect(ventana, GRIS, (self.x, self.y, self.ancho, self.altura))
        pygame.draw.circle(ventana, VERDE_CLARO, (int(self.handle_x), self.y + self.altura // 2), 10)

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if abs(evento.pos[0] - self.handle_x) < 15 and abs(evento.pos[1] - (self.y + self.altura // 2)) < 15:
                self.arrastrando = True
        elif evento.type == pygame.MOUSEBUTTONUP:
            self.arrastrando = False
        elif evento.type == pygame.MOUSEMOTION and self.arrastrando:
            self.handle_x = max(self.x, min(evento.pos[0], self.x + self.ancho))
            # Calcular valor basado en la posición
            porcentaje = (self.handle_x - self.x) / self.ancho
            self.valor = int(round(self.min_val + porcentaje * (self.max_val - self.min_val)))

    def obtener_valor(self):
        return self.valor


class SliderVelocidad:
    def __init__(self, x, y, ancho, valor_inicial=1.0):
        self.x = x
        self.y = y
        self.ancho = ancho
        self.altura = 10
        self.opciones = [1.0, 1.5, 2.0]
        self.indice = self.opciones.index(valor_inicial)
        self.valor = valor_inicial
        self.handle_x = x + (self.indice / (len(self.opciones) - 1)) * ancho
        self.arrastrando = False

    def dibujar(self, ventana):
        pygame.draw.rect(ventana, GRIS, (self.x, self.y, self.ancho, self.altura))
        
        # Dibujar marcas para cada opción
        for i in range(len(self.opciones)):
            x_marca = self.x + (i / (len(self.opciones) - 1)) * self.ancho
            pygame.draw.circle(ventana, BLANCO, (int(x_marca), self.y + self.altura // 2), 3)
        
        pygame.draw.circle(ventana, VERDE_CLARO, (int(self.handle_x), self.y + self.altura // 2), 10)

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if abs(evento.pos[0] - self.handle_x) < 15 and abs(evento.pos[1] - (self.y + self.altura // 2)) < 15:
                self.arrastrando = True
        elif evento.type == pygame.MOUSEBUTTONUP:
            if self.arrastrando:
                # Ajustar a la opción más cercana
                porcentaje = (self.handle_x - self.x) / self.ancho
                self.indice = round(porcentaje * (len(self.opciones) - 1))
                self.indice = max(0, min(self.indice, len(self.opciones) - 1))
                self.valor = self.opciones[self.indice]
                self.handle_x = self.x + (self.indice / (len(self.opciones) - 1)) * self.ancho
            self.arrastrando = False
        elif evento.type == pygame.MOUSEMOTION and self.arrastrando:
            self.handle_x = max(self.x, min(evento.pos[0], self.x + self.ancho))

    def obtener_valor(self):
        return self.valor


class PlayerNameScreen:
    def __init__(self, ventana, modo):
        self.ventana = ventana
        self.modo = modo
        self.reloj = pygame.time.Clock()
        self.corriendo = True
        self.volver_al_menu = False

        self.fuente_titulo = pygame.font.Font(None, 60)
        self.fuente_texto = pygame.font.Font(None, 40)
        self.fuente_pequeña = pygame.font.Font(None, 30)
        self.fuente_boton = pygame.font.Font(None, 40)

        # Entrada de texto
        self.nombre = ""
        self.input_rect = pygame.Rect(ANCHO_VENTANA // 2 - 200, 150, 400, 50)
        self.input_activo = False

        # Sliders de dificultad
        x_centro = ANCHO_VENTANA // 2 - 150
        self.slider_enemigos = Slider(x_centro, 270, 300, valor_inicial=2, min_val=1, max_val=4)
        self.slider_velocidad = SliderVelocidad(x_centro, 370, 300, valor_inicial=1.0)

        # Botones
        self.btn_volver = Boton(ANCHO_VENTANA // 2 - 125, 500, 250, 50, "VOLVER", self.fuente_boton)
        self.btn_jugar = Boton(ANCHO_VENTANA // 2 - 125, 430, 250, 50, "JUGAR", self.fuente_boton)

        reproducir_musica("ASSETS/OST/Mode_Selection.mp3")

    def dibujar(self):
        self.ventana.fill(NEGRO)

        # Título
        titulo = f"Modo {self.modo}"
        texto_titulo = self.fuente_titulo.render(titulo, True, BLANCO)
        rect_titulo = texto_titulo.get_rect(center=(ANCHO_VENTANA // 2, 60))
        self.ventana.blit(texto_titulo, rect_titulo)

        # Etiqueta del input
        etiqueta = self.fuente_texto.render("Ingresa tu nombre:", True, BLANCO)
        rect_etiqueta = etiqueta.get_rect(center=(ANCHO_VENTANA // 2, 120))
        self.ventana.blit(etiqueta, rect_etiqueta)

        # Caja de texto
        color_borde = VERDE_CLARO if self.input_activo else GRIS
        pygame.draw.rect(self.ventana, color_borde, self.input_rect, 3)

        # Texto dentro de la caja
        texto_surface = self.fuente_texto.render(self.nombre, True, BLANCO)
        self.ventana.blit(texto_surface, (self.input_rect.x + 10, self.input_rect.y + 5))

        # --- SLIDERS DE DIFICULTAD ---
        
        # Slider de enemigos
        etiqueta_enemigos = self.fuente_pequeña.render("Número de enemigos:", True, BLANCO)
        self.ventana.blit(etiqueta_enemigos, (ANCHO_VENTANA // 2 - etiqueta_enemigos.get_width() // 2, 230))
        
        self.slider_enemigos.dibujar(self.ventana)
        
        valor_enemigos = self.fuente_pequeña.render(f"{self.slider_enemigos.obtener_valor()}", True, VERDE_CLARO)
        self.ventana.blit(valor_enemigos, (ANCHO_VENTANA // 2 - valor_enemigos.get_width() // 2, 295))

        # Slider de velocidad
        etiqueta_velocidad = self.fuente_pequeña.render("Velocidad de enemigos:", True, BLANCO)
        self.ventana.blit(etiqueta_velocidad, (ANCHO_VENTANA // 2 - etiqueta_velocidad.get_width() // 2, 330))
        
        self.slider_velocidad.dibujar(self.ventana)
        
        valor_velocidad = self.fuente_pequeña.render(f"{self.slider_velocidad.obtener_valor()}x", True, VERDE_CLARO)
        self.ventana.blit(valor_velocidad, (ANCHO_VENTANA // 2 - valor_velocidad.get_width() // 2, 395))

        # Mostrar botones
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

            # Manejar sliders
            self.slider_enemigos.manejar_evento(evento)
            self.slider_velocidad.manejar_evento(evento)

            if evento.type == pygame.MOUSEBUTTONDOWN:
                if self.input_rect.collidepoint(evento.pos):
                    self.input_activo = True
                else:
                    self.input_activo = False

                if self.btn_volver.es_clickeado(evento.pos):
                    self.corriendo = False

                if self.nombre.strip() != "" and self.btn_jugar.es_clickeado(evento.pos):
                    detener_musica()
                    
                    # Obtener configuración de dificultad
                    num_enemigos = self.slider_enemigos.obtener_valor()
                    velocidad_enemigos = self.slider_velocidad.obtener_valor()
                    
                    if self.modo == "CAZADOR":
                        juego = HunterMode(self.ventana, self.nombre, num_enemigos, velocidad_enemigos)
                        volver = juego.ejecutar()
                    elif self.modo == "ESCAPE":
                        juego = EscapeMode(self.ventana, self.nombre, num_enemigos, velocidad_enemigos)
                        volver = juego.ejecutar()
                    
                    if volver:
                        self.volver_al_menu = True
                    
                    self.corriendo = False

            elif evento.type == pygame.KEYDOWN and self.input_activo:
                if evento.key == pygame.K_BACKSPACE:
                    self.nombre = self.nombre[:-1]
                elif evento.key == pygame.K_RETURN:
                    if self.nombre.strip() != "":
                        self.corriendo = False
                else:
                    if len(self.nombre) < 15:
                        self.nombre += evento.unicode

    def ejecutar(self):
        while self.corriendo:
            self.manejar_eventos()
        
            if not self.volver_al_menu:
                self.dibujar()
        
            self.reloj.tick(FPS)
    
        return self.volver_al_menu