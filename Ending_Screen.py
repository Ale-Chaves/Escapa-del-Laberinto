import pygame
import json
import os

ANCHO_VENTANA = 800
ALTO_VENTANA = 600

class EndingScreen:
    def __init__(self, ventana, nombre_jugador, puntaje):
        self.ventana = ventana
        self.player_name = nombre_jugador
        self.player_score = puntaje

        self.font_big = pygame.font.Font(None, 70)
        self.font_med = pygame.font.Font(None, 40)
        self.font_small = pygame.font.Font(None, 30)

        self.scores_file = "scores_escape.json"
        self.scores = self.cargar_scores()
        self.actualizar_scores()

    def cargar_scores(self):
        if not os.path.exists(self.scores_file):
            return []

        with open(self.scores_file, "r") as f:
            try:
                return json.load(f)
            except:
                return []

    def actualizar_scores(self):
        # Agregar puntaje del jugador
        self.scores.append({"name": self.player_name, "score": self.player_score})

        # Ordenar de mayor a menor
        self.scores = sorted(self.scores, key=lambda x: x["score"], reverse=True)

        # Solo mantener Top 5
        self.scores = self.scores[:5]

        # Guardar
        with open(self.scores_file, "w") as f:
            json.dump(self.scores, f, indent=4)

    def run(self):
        corriendo = True
        while corriendo:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    corriendo = False
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_RETURN or evento.key == pygame.K_ESCAPE:
                        corriendo = False

            self.dibujar()
            pygame.display.flip()

    def dibujar(self):
        self.ventana.fill((0, 0, 0))

        # Texto principal
        titulo = self.font_big.render("¡FIN DEL JUEGO!", True, (255, 255, 255))
        self.ventana.blit(titulo, (ANCHO_VENTANA//2 - titulo.get_width()//2, 40))

        # Puntaje del jugador
        score_text = self.font_med.render(f"Puntaje: {self.player_score}", True, (255, 255, 0))
        self.ventana.blit(score_text, (ANCHO_VENTANA//2 - score_text.get_width()//2, 120))

        top_title = self.font_med.render("TOP 5 - MODO ESCAPA", True, (0, 255, 255))
        self.ventana.blit(top_title, (ANCHO_VENTANA//2 - top_title.get_width()//2, 200))

        # Mostrar Top 5
        y = 260
        for idx, datos in enumerate(self.scores):
            nombre = datos["name"]
            puntaje = datos["score"]
            linea = self.font_small.render(f"{idx+1}. {nombre} - {puntaje}",True,(255, 255, 255))
            self.ventana.blit(linea, (ANCHO_VENTANA//2 - linea.get_width()//2, y))
            y += 40

        # Instrucción
        texto = self.font_small.render("Presiona ENTER para continuar...", True, (200, 200, 200))
        self.ventana.blit(texto, (ANCHO_VENTANA//2 - texto.get_width()//2, 520))