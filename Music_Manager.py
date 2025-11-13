import pygame
import json
import os

musica_actual = None

def reproducir_musica(ruta, volumen_config_path="settings.json"):
    global musica_actual
    if musica_actual == ruta:
        return  # Ya se está reproduciendo esa música, no hacer nada

    # Leer volumen
    if os.path.exists(volumen_config_path):
        with open(volumen_config_path, "r") as f:
            settings = json.load(f)
            volumen = settings.get("volumen_musica", 5) / 10
    else:
        volumen = 0.5

    # Cargar y reproducir música
    try:
        pygame.mixer.music.load(ruta)
        pygame.mixer.music.set_volume(volumen)
        pygame.mixer.music.play(-1)
        musica_actual = ruta
    except pygame.error as e:
        print(f"No se pudo cargar la música: {e}")

def detener_musica():
    global musica_actual
    pygame.mixer.music.stop()
    musica_actual = None
