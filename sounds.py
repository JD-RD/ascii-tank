"""Procedural sound effects using pygame mixer."""

import pygame
import numpy as np


def _make_sound(frequency, duration, sample_rate=22050, wave_type="square", volume=0.3):
    frames = int(duration * sample_rate)
    arr = np.zeros(frames, dtype=np.float32)
    t = np.linspace(0, duration, frames, False)
    if wave_type == "square":
        arr = np.sign(np.sin(2 * np.pi * frequency * t))
    elif wave_type == "sawtooth":
        arr = 2 * (t * frequency - np.floor(0.5 + t * frequency))
    elif wave_type == "noise":
        arr = np.random.uniform(-1, 1, frames)
    elif wave_type == "sine":
        arr = np.sin(2 * np.pi * frequency * t)
    arr *= volume
    arr = (arr * 32767).astype(np.int16)
    arr = np.column_stack((arr, arr))
    sound = pygame.sndarray.make_sound(arr)
    return sound


def make_shoot_sound():
    return _make_sound(800, 0.08, wave_type="square", volume=0.15)


def make_explosion_sound():
    return _make_sound(80, 0.3, wave_type="noise", volume=0.25)


def make_hit_sound():
    return _make_sound(200, 0.15, wave_type="sawtooth", volume=0.2)
