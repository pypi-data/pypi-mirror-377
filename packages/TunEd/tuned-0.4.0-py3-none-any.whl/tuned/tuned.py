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

import argparse
import sys
import threading
import time
from datetime import timedelta
from queue import Queue, Empty

import numpy as np
import sounddevice as sd

from tuned.audio_analyzer import AudioAnalyzer
from tuned.display import TerminalDisplay
from tuned.detection_strategies import (
    NoteDetectionStrategy,
    ChordDetectionStrategy,
    AttackAnalysisStrategy,
    AmplitudeAttackStrategy,
    HybridAttackStrategy,
    AubioAttackStrategy,
    SpectrumAnalysisStrategy
)

# --- Constantes et Configuration ---
SAMPLING_RATE = 48000
CHUNK_SIZE = 1024
# Un long tampon pour l'analyse spectrale, un court pour l'attaque
SPECTRAL_BUFFER_TIMES = 50
ATTACK_BUFFER_TIMES = 2

# Fenêtre temporelle (en secondes) après une attaque pour valider un accord.
# Basée sur la durée du buffer spectral + une marge de 20% pour le traitement.
SPECTRAL_BUFFER_DURATION = (SPECTRAL_BUFFER_TIMES * CHUNK_SIZE) / SAMPLING_RATE
ANALYSIS_WINDOW_SECONDS = SPECTRAL_BUFFER_DURATION * 1.4  # 1.2

# --- Analyse des Arguments ---
parser = argparse.ArgumentParser(prog='TunEd', description='Accordeur en ligne de commande', epilog='')
parser.add_argument('--version', action='version', version='%(prog)s 0.4.0')
parser.add_argument('--verbose', '-v', action='count', default=0, help='Niveau de verbosité.')
parser.add_argument('--frequency', '-f', action='store', default=440, type=int, help='Fréquence de référence (La).')
parser.add_argument('--mod', '-m', action='store', default='note', choices=['note', 'chord'],
                    help='Mode de détection (note ou accord).')
parser.add_argument('--no-harmonics-identification', '-nohi', action='store_false', dest='identify_harmonics',
                    help="Désactive l'identification des harmoniques pour les accords.")

args = parser.parse_args()

VERBOSE = args.verbose if args.verbose in [0, 1, 2, 3, 4, 6] else 4
REF_FREQ = args.frequency
DETECTION_MODE = args.mod
IDENTIFY_HARMONICS = args.identify_harmonics

# --- Profils de Détection d'Attaque par Instrument ---
INSTRUMENT_PROFILES = {
    'guitar': {
        'amplitude_settings': {'db_threshold': 40.0, 'cooldown_frames': 3, 'peak_window_size': 3},
        'spectral_settings': {'threshold_offset': 0.1}  # Très sensible pour capter les nuances
    },
    'bass': {
        'amplitude_settings': {'db_threshold': 25.0, 'cooldown_frames': 8, 'peak_window_size': 5},
        'spectral_settings': {'threshold_offset': 0.5}  # Moins sensible pour ignorer les bruits de frette
    }
}

if DETECTION_MODE == 'chord':
    default_display = ['chord', 'notes']
else:
    default_display = ['tuner']
    
verbosity_display = {
    0: [], 1: ['precision'], 2: ['precision', 'frequency'],
    3: ['precision', 'frequency', 'signal_level', 'attack'],
    4: ['precision', 'frequency', 'signal_level', 'attack', 'execution_time'],
    6: ['precision', 'frequency', 'signal_level', 'attack', 'execution_time', 'egg']
}
to_display = [*default_display, *verbosity_display[VERBOSE]]


# --- Classes de l'Application ---

class AudioStreamReader:
    """
    Gère le flux audio de sounddevice. Sa seule responsabilité est de lire les
    données audio brutes et leur timestamp, et de les placer dans les files d'attente
    pour les threads d'analyse.
    """
    def __init__(self, data_queues: list[Queue]):
        self.data_queues = data_queues
        self.running = False
        self.stream = sd.InputStream(
            samplerate=SAMPLING_RATE, blocksize=CHUNK_SIZE,
            channels=1, dtype='float32', callback=self._callback)

    def _callback(self, indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        if self.running:
            # Place le segment audio et son timestamp dans chaque file d'attente
            for q in self.data_queues:
                q.put((indata.copy(), time.inputBufferAdcTime))

    def start(self):
        self.running = True
        self.stream.start()

    def stop(self):
        self.running = False
        time.sleep(0.1)
        self.stream.stop()
        self.stream.close()


class AnalysisThread(threading.Thread):
    """
    Un thread de travail générique qui consomme des données audio d'une file,
    les traite via un AudioAnalyzer, et place les résultats dans une autre file.
    """
    def __init__(self, data_queue: Queue, results_queue: Queue, analyzer: AudioAnalyzer):
        super().__init__()
        self.data_queue = data_queue
        self.results_queue = results_queue
        self.analyzer = analyzer
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            try:
                raw_frame, timestamp = self.data_queue.get(timeout=0.1)
                decoded_frame = raw_frame.squeeze()
                analysis_result = self.analyzer.analyze(decoded_frame, timestamp)
                self.results_queue.put(analysis_result)
            except Empty:
                continue

    def stop(self):
        self.running = False


# --- Logique Principale ---

def tuned():
    """Fonction principale de l'application en ligne de commande TunEd."""
    # Files de communication entre les threads
    spectral_data_queue = Queue()
    attack_data_queue = Queue()
    results_queue = Queue()
    
    stream_reader = None
    spectral_thread = None
    attack_thread = None
    display = TerminalDisplay(to_display, DETECTION_MODE)

    try:
        # 1. Sélection et création de la stratégie d'analyse spectrale
        spectral_strategy: SpectrumAnalysisStrategy
        if DETECTION_MODE == 'note':
            spectral_strategy = NoteDetectionStrategy(ref_freq=REF_FREQ)
        else: # 'chord'
            spectral_strategy = ChordDetectionStrategy(ref_freq=REF_FREQ, identify_harmonics=IDENTIFY_HARMONICS)

        # 2. Création de la stratégie d'analyse d'attaque

        # Crée les deux sous-stratégies avec les réglages du profil
        # amplitude_strategy = AmplitudeAttackStrategy(**profile['amplitude_settings'])
        # spectral_attack_strategy = AttackAnalysisStrategy(sampling_rate=SAMPLING_RATE, **profile['spectral_settings'])

        # Injecte les deux stratégies dans la stratégie hybride (méthode recommandée)
        # attack_strategy = HybridAttackStrategy(
        #     spectral_strategy=spectral_attack_strategy,
        #     amplitude_strategy=amplitude_strategy
        # )

        # --- AUTRES STRATÉGIES (POUR TESTS) ---
        # Stratégie basée sur la nouveauté spectrale seule
        # attack_strategy = AttackAnalysisStrategy(sampling_rate=SAMPLING_RATE, **profile['spectral_settings'])
        
        # Stratégie basée sur le volume seul
        # attack_strategy = AmplitudeAttackStrategy(**profile['amplitude_settings'])

        # --- NOUVELLE STRATÉGIE AUBIO (POUR TESTS) ---
        attack_strategy = AubioAttackStrategy(
            sampling_rate=SAMPLING_RATE,
            win_s=CHUNK_SIZE,
            hop_s=CHUNK_SIZE,
            method="specdiff"  # Options: "hfc", "complex", "phase", "specdiff", etc.
        )

        # 3. Création des deux moteurs AudioAnalyzer avec leurs stratégies respectives
        spectral_analyzer = AudioAnalyzer(
            strategy=spectral_strategy, sampling_rate=SAMPLING_RATE,
            chunk_size=CHUNK_SIZE, buffer_times=SPECTRAL_BUFFER_TIMES)
        
        attack_analyzer = AudioAnalyzer(
            strategy=attack_strategy, sampling_rate=SAMPLING_RATE,
            chunk_size=CHUNK_SIZE, buffer_times=ATTACK_BUFFER_TIMES)

        # 4. Création et démarrage des threads
        stream_reader = AudioStreamReader([spectral_data_queue, attack_data_queue])
        spectral_thread = AnalysisThread(spectral_data_queue, results_queue, spectral_analyzer)
        attack_thread = AnalysisThread(attack_data_queue, results_queue, attack_analyzer)

        spectral_thread.start()
        attack_thread.start()
        stream_reader.start()

        display.print_startup_message(REF_FREQ)

        # 5. Boucle principale : gestion de la fenêtre temporelle post-attaque
        last_analysis_results = {}
        last_attack_timestamp = 0.0  # Timestamp de la dernière attaque valide
        while True:
            new_result_part = results_queue.get()
            last_analysis_results.update(new_result_part)

            # --- Logique de corrélation temporelle ---

            # 1. Une attaque est détectée : on enregistre son timestamp comme point de départ.
            if 'attack' in new_result_part and new_result_part['attack'].detected:
                last_attack_timestamp = new_result_part['attack'].timestamp

            # 2. Un résultat d'accord arrive : on le compare à l'attaque en attente.
            if DETECTION_MODE == 'chord' and 'chord' in new_result_part and last_attack_timestamp > 0:
                
                current_chord = new_result_part['chord']
                current_timestamp = current_chord.timestamp

                # Condition : le résultat est DANS la fenêtre d'analyse
                if current_timestamp <= last_attack_timestamp + ANALYSIS_WINDOW_SECONDS:
                    # Condition supplémentaire : l'accord doit avoir un nom valide pour sauter la ligne.
                    if current_chord.quality and current_chord.quality.strip():
                        display.end_current_line()
                    
                    # Qu'il y ait un nom ou non, l'attaque est consommée car le résultat d'analyse est arrivé.
                    last_attack_timestamp = 0.0

                # Condition : le résultat est arrivé TROP TARD
                elif current_timestamp > last_attack_timestamp + ANALYSIS_WINDOW_SECONDS:
                    last_attack_timestamp = 0.0  # L'attaque est manquée, on réinitialise

            # On affiche toujours l'état le plus récent
            execution_time = 0
            output_string = display.format_output(last_analysis_results, execution_time)
            display.print_line(output_string)

    except KeyboardInterrupt:
        print("\nSortie.")
    except Exception as e:
        print(f"\nUne erreur est survenue: {e}")
    finally:
        # 6. Arrêt propre des threads et des ressources
        if spectral_thread: spectral_thread.stop()
        if attack_thread: attack_thread.stop()
        if stream_reader: stream_reader.stop()
        if spectral_thread: spectral_thread.join()
        if attack_thread: attack_thread.join()
        sys.exit()