import pygame
import json
import os
import Music_Manager  # NUEVO

ANCHO_VENTANA = 800
ALTO_VENTANA = 600

class EndingScreen:
    def __init__(self, ventana, nombre_jugador, puntaje, modo):
        self.ventana = ventana
        self.player_name = nombre_jugador
        self.player_score = puntaje
        self.modo = modo
        self.volver_al_menu = False

        self.font_big = pygame.font.Font(None, 70)
        self.font_med = pygame.font.Font(None, 40)
        self.font_small = pygame.font.Font(None, 30)

        # ARCHIVO CORRECTO SEGÚN EL MODO
        self.archivo = f"scores_{modo}.json"

        self.scores = self.cargar_scores()
        self.actualizar_scores()
        
        # NUEVO: Reproducir música de ending al entrar (solo una vez, no loop)
        try:
            pygame.mixer.music.load("ASSETS/OST/Ending.mp3")
            
            # Cargar configuración de volumen
            if os.path.exists("settings.json"):
                with open("settings.json", "r") as f:
                    settings = json.load(f)
                    if settings.get("musica_activada", True):
                        volumen = settings.get("volumen_musica", 5) / 10
                        pygame.mixer.music.set_volume(volumen)
                        pygame.mixer.music.play(0)  # 0 = reproducir solo una vez (no loop)
        except Exception as e:
            print(f"Error al cargar música de ending: {e}")

    def cargar_scores(self):
        if not os.path.exists(self.archivo):
            return []

        with open(self.archivo, "r") as f:
            try:
                return json.load(f)
            except:
                return []

    def actualizar_scores(self):
        # Si el archivo no existe, inicializa una lista vacía
        if os.path.exists(self.archivo):
            with open(self.archivo, "r") as f:
                data = json.load(f)
        else:
            data = []

        # Agregar el puntaje actual
        data.append({"name": self.player_name, "score": self.player_score})

        # Ordenar y conservar solo top 5
        data = sorted(data, key=lambda x: x["score"], reverse=True)[:5]

        # Guardar
        with open(self.archivo, "w") as f:
            json.dump(data, f, indent=4)

        # Actualizar la lista interna
        self.scores = data

    def run(self):
        corriendo = True
        while corriendo:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_RETURN or evento.key == pygame.K_ESCAPE:
                        self.volver_al_menu = True
                        corriendo = False

            self.dibujar()
            pygame.display.flip()
        
        # NUEVO: Detener música al salir
        Music_Manager.detener_musica()
        
        return self.volver_al_menu

    def dibujar(self):
        self.ventana.fill((0, 0, 0))

        # Texto principal
        titulo = self.font_big.render("¡FIN DEL JUEGO!", True, (255, 255, 255))
        self.ventana.blit(titulo, (ANCHO_VENTANA//2 - titulo.get_width()//2, 40))

        # Puntaje del jugador
        score_text = self.font_med.render(f"Puntaje: {self.player_score}", True, (255, 255, 0))
        self.ventana.blit(score_text, (ANCHO_VENTANA//2 - score_text.get_width()//2, 120))

        top_title = self.font_med.render(f"TOP 5 - MODO {self.modo.upper()}", True, (0, 255, 255))
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
        texto = self.font_small.render("Presiona ENTER para volver al menú principal...", True, (200, 200, 200))
        self.ventana.blit(texto, (ANCHO_VENTANA//2 - texto.get_width()//2, 520))