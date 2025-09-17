"""
Copyright (C) 2025 drd <drd.ltt000@gmail.com>

This file is part of TunEd.

TunEd is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

TunEd is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from dataclasses import field
from collections import deque
import numpy as np
import scipy.fft
from scipy.signal import find_peaks
import librosa

from tuned.chord import Chord
from tuned.sound import Sound
from tuned.music_theory import frequency_to_midi, midi_to_ansi_note, midi_to_frequency


class AudioAnalyzer:
    """
    Une classe dédiée à l'analyse du signal audio pour détecter les notes de musique.
    Cette classe est conçue pour être utilisée dans un thread de traitement séparé.
    Elle prend des données audio brutes, les traite et renvoie des informations sur les notes.
    Elle ne gère pas le streaming audio ou le threading elle-même.
    """

    ZERO_PADDING = 3  # fois la longueur du tampon
    NUM_HPS = 3  # Harmonic Product Spectrum (Spectre de Produit Harmonique)

    def __init__(self,
                 detection_mode='note',  # 'note' ou 'chord'
                 ref_freq=440,
                 sampling_rate=48000,
                 chunk_size=1024,
                 buffer_times=50,
                 identify_harmonics=True):
        """
        Initialise l'analyseur avec les paramètres de traitement audio.
        """
        if detection_mode not in ['note', 'chord']:
            raise ValueError("detection_mode doit être 'note' ou 'chord'")
        self.detection_mode = detection_mode
        self.ref_freq = ref_freq
        self.SAMPLING_RATE = sampling_rate
        self.CHUNK_SIZE = chunk_size
        self.BUFFER_TIMES = buffer_times
        self.identify_harmonics = identify_harmonics

        # Initialise le tampon, la fenêtre de Hanning et les fréquences FFT
        self.buffer = np.zeros(self.CHUNK_SIZE * self.BUFFER_TIMES)
        self.hanning_window = np.hanning(len(self.buffer))
        fft_len = len(self.buffer) * (1 + self.ZERO_PADDING)
        self.frequencies = scipy.fft.fftfreq(fft_len, 1. / self.SAMPLING_RATE)

        # --- NOUVEAUX ATTRIBUTS POUR LA DÉTECTION D'ATTAQUE (ONSET) ---
        self.novelty_history = deque(maxlen=10)
        self.moving_avg_history = deque(maxlen=100)
        self.threshold_offset = 0.8  # À ajuster
        self.cooldown_frames = 15
        self.cooldown_counter = 0

    def attack_detection(self, audio_chunk) -> bool:
        """
        Analyse un segment audio et renvoie True si une attaque est détectée.
        """
        # Gère le temps de recharge pour éviter les détections multiples
        if self.cooldown_counter > 0:
            self.cooldown_counter -= 1
            return False

        # Calcule l'enveloppe de nouveauté spectrale (onset strength)
        onset_env = librosa.onset.onset_strength(y=audio_chunk, sr=self.SAMPLING_RATE, n_fft=1024)
        current_novelty = np.max(onset_env)

        # Met à jour les historiques
        self.novelty_history.append(current_novelty)
        self.moving_avg_history.append(current_novelty)

        # Attend que l'historique court soit rempli pour commencer
        if len(self.novelty_history) < self.novelty_history.maxlen:
            return False

        # Logique de détection de pic
        is_peak = current_novelty >= max(self.novelty_history)
        threshold = np.mean(self.moving_avg_history) + self.threshold_offset
        is_above_threshold = current_novelty > threshold

        if is_peak and is_above_threshold:
            self.cooldown_counter = self.cooldown_frames  # Active le temps de recharge
            return True

        return False

    def analyze(self, decoded_frame):
        """
        Traite un segment de données audio pour détecter les informations musicales.
        C'est la méthode principale à appeler par le thread de traitement.
        """
        # 1. Met à jour le tampon interne avec le nouveau segment
        self.buffer = np.roll(self.buffer, -self.CHUNK_SIZE)
        self.buffer[-self.CHUNK_SIZE:] = decoded_frame

        # 2. Détecte une attaque sur la partie la plus récente du tampon
        attack_detected = self.attack_detection(decoded_frame)

        # 3. Applique le fenêtrage, le padding et effectue la FFT sur tout le tampon
        pad = np.pad(self.buffer * self.hanning_window, (0, len(self.buffer) * self.ZERO_PADDING), "constant")
        fft = scipy.fft.fft(pad)
        magnitude_data = abs(fft)
        magnitude_data = magnitude_data[:len(magnitude_data) // 2]

        # 4. Applique le Spectre de Produit Harmonique (HPS)
        magnitude_data_orig = magnitude_data.copy()
        for i in range(2, self.NUM_HPS + 1, 1):
            hps_len = int(np.ceil(len(magnitude_data) / i))
            magnitude_data[:hps_len] *= magnitude_data_orig[::i]

        # 5. Détecte la note/l'accord à partir du spectre traité
        if self.detection_mode == 'note':
            sounds = self.note_detection(magnitude_data, self.frequencies, fft)
        else:  # 'chord'
            sounds = self.chord_detection(magnitude_data, self.frequencies, fft)

        return {
            "sounds": sounds,
            "attack_detected": attack_detected
        }

    def note_detection(self, magnitude_data, frequencies, fft_data) -> Sound:
        """
        Trouve la fréquence la plus forte et la convertit en note de musique.
        """
        magnitude = np.max(magnitude_data)
        magnitude_to_db = 20 * np.log10(magnitude + 1e-9)
        index_loudest = np.argmax(magnitude_data)
        frequency = round(frequencies[index_loudest], 2)
        phase = np.angle(fft_data[index_loudest])
        midi_note = frequency_to_midi(frequency, self.ref_freq)
        note, octave = midi_to_ansi_note(midi_note)
        offset = self.compute_frequency_offset(frequency, midi_note)
        return Sound(
            magnitude=magnitude,
            magnitude_to_db=0 if np.isnan(magnitude_to_db) else magnitude_to_db,
            phase=phase,
            frequency=frequency,
            note=note,
            octave=octave,
            offset=offset
        )

    def chord_detection(self, magnitude_data, frequencies, fft_data) -> Chord:
        """
        Trouve toutes les fréquences proéminentes et les transmet à la classe Chord pour analyse.
        """
        peaks, _ = find_peaks(magnitude_data, prominence=10000, distance=50)

        detected_sounds = []
        for peak_index in peaks:
            frequency = round(frequencies[peak_index], 2)
            if frequency == 0:
                continue

            magnitude = magnitude_data[peak_index]
            magnitude_to_db = 20 * np.log10(magnitude + 1e-9)
            phase = np.angle(fft_data[peak_index])
            midi_note = frequency_to_midi(frequency, self.ref_freq)
            note, octave = midi_to_ansi_note(midi_note)
            offset = self.compute_frequency_offset(frequency, midi_note)

            sound = Sound(
                magnitude=magnitude,
                magnitude_to_db=0 if np.isnan(magnitude_to_db) else magnitude_to_db,
                phase=phase,
                frequency=frequency,
                note=note,
                octave=octave,
                offset=offset
            )
            detected_sounds.append(sound)

        return Chord(detected_sounds, ref_freq=self.ref_freq, identify_harmonics=self.identify_harmonics)

    def compute_frequency_offset(self, frequency, midi_note):
        """
        Calcule le décalage d'une fréquence par rapport au demi-ton parfait le plus proche.
        """
        nearest_midi_note_frequency = midi_to_frequency(midi_note, self.ref_freq)
        frequency_offset = nearest_midi_note_frequency - frequency
        if frequency_offset == 0:
            return 0
        next_note = midi_note
        if frequency_offset > 0:
            next_note += 1
        elif frequency_offset < 0:
            next_note -= 1
        semitone_step = abs((nearest_midi_note_frequency - midi_to_frequency(next_note, self.ref_freq)) / 100)
        if semitone_step == 0:
            return 0
        offset = round(frequency_offset / semitone_step)
        return offset
