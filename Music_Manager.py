import pygame
import json
import os

musica_actual = None
efectos_cargados = {}

def cargar_configuracion(config_path="settings.json"):
    """Carga la configuración de audio desde settings.json"""
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return json.load(f)
    return {
        "musica_activada": True,
        "efectos_activados": True,
        "volumen_musica": 5,
        "volumen_efectos": 5
    }

def reproducir_musica(ruta, volumen_config_path="settings.json"):
    global musica_actual
    if musica_actual == ruta:
        return

    # Leer configuración
    settings = cargar_configuracion(volumen_config_path)
    
    # Verificar si la música está activada
    if not settings.get("musica_activada", True):
        return
    
    volumen = settings.get("volumen_musica", 5) / 10

    # Cargar y reproducir música
    try:
        pygame.mixer.music.load(ruta)
        pygame.mixer.music.set_volume(volumen)
        pygame.mixer.music.play(-1)
        musica_actual = ruta
    except pygame.error as e:
        print(f"No se pudo cargar la música: {e}")

def detener_musica():
    """Detiene la música actual"""
    global musica_actual
    pygame.mixer.music.stop()
    musica_actual = None

def pausar_musica():
    """Pausa la música actual"""
    pygame.mixer.music.pause()

def reanudar_musica():
    """Reanuda la música pausada"""
    pygame.mixer.music.unpause()

def reproducir_efecto(nombre_efecto, config_path="settings.json"):
    global efectos_cargados
    
    # Leer configuración
    settings = cargar_configuracion(config_path)
    
    # Verificar si los efectos están activados
    if not settings.get("efectos_activados", True):
        return
    
    volumen = settings.get("volumen_efectos", 5) / 10
    
    # Cargar efecto si no está en cache
    if nombre_efecto not in efectos_cargados:
        ruta = f"ASSETS/SOUND EFFECTS/{nombre_efecto}.mp3"
        try:
            efecto = pygame.mixer.Sound(ruta)
            efectos_cargados[nombre_efecto] = efecto
        except pygame.error as e:
            print(f"No se pudo cargar el efecto {nombre_efecto}: {e}")
            return
    
    # Reproducir efecto
    efecto = efectos_cargados[nombre_efecto]
    efecto.set_volume(volumen)
    efecto.play()

def actualizar_volumen_musica(config_path="settings.json"):
    """Actualiza el volumen de la música actual según la configuración"""
    if pygame.mixer.music.get_busy():
        settings = cargar_configuracion(config_path)
        if settings.get("musica_activada", True):
            volumen = settings.get("volumen_musica", 5) / 10
            pygame.mixer.music.set_volume(volumen)
        else:
            pygame.mixer.music.set_volume(0)