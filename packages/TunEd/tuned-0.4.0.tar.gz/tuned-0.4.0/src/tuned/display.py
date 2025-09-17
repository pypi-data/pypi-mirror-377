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
import random
from .sound import Sound
from .chord import Chord
from .attack import Attack
from .color import Color
from .music_theory import CHORD_FORMULAS, frequency_to_midi

GRADIENTS = {
    5: Color.fg.green,
    10: Color.fg.rgb(63, 192, 0),
    15: Color.fg.rgb(127, 128, 0),
    20: Color.fg.rgb(192, 63, 0),
    21: Color.fg.red
}
LEVELS = [" ", " ", "▂", "▃", "▄", "▅", "▇", "█"]
EGGS = ['🯅', '🯆', '🯇', '🯈']

class TerminalDisplay:
    
    def __init__(self, to_display_items: list[str], detection_mode: str = 'note'):
        self.to_display_items = to_display_items
        self.detection_mode = detection_mode
        self.newline_needed = False # Pour savoir si on doit sauter une ligne

    def format_output(self, analysis_result: dict, execution_time: float) -> str:
        """
        Formate la chaîne de caractères complète pour la sortie.
        """
        # Extrait les données du dictionnaire de résultats
        sound = analysis_result.get('sound')
        chord = analysis_result.get('chord')
        attack = analysis_result.get('attack')
        attack_detected = attack.detected if attack else False

        self.newline_needed = False # Réinitialisé à chaque appel
        to_display = ""
        is_new_valid_attack = False

        # Logique principale d'affichage basée sur le mode et les données disponibles
        if self.detection_mode == 'chord' and chord:
            if attack_detected and chord.quality and chord.quality.strip():
                is_new_valid_attack = True
                self.newline_needed = True
            to_display = self.format_chord(chord, is_new_valid_attack)

        elif self.detection_mode == 'note' and sound:
            to_display = self.format_note(sound)
                            
        to_display_dict = {
            'attack': self._display_is_attack(attack_detected, attack),
            'execution_time': self._display_execution_time(execution_time),
            'egg': self._display_egg()
        }
        
        active_display_items = [f"[{to_display_dict[d]}]" for d in self.to_display_items if d in to_display_dict and to_display_dict[d]]
        
        output_str = f"{to_display} {''.join(active_display_items)}"

        # Si une attaque est détectée, on met un fond blanc sur toute la ligne.
        if attack_detected:
            output_str = output_str.replace(Color.reset, f"{Color.reset}{Color.bg.white}")
            return f"{Color.bg.white}{output_str}{Color.reset}"
        
        return output_str
    
    def format_note(self, sound: Sound) -> str:
        """
        Formate la chaîne de sortie complète pour le mode note.
        """
        to_display_dict = {
            'tuner': self._display_tuner(sound),
            'precision': self._display_precision(sound),
            'frequency': self._display_frequency(sound),
            'phase': self._display_phase(sound),
            'signal_level': self._display_signal_level(sound),
        }
        active_display_items = [f"[{to_display_dict[d]}]" for d in self.to_display_items if d in to_display_dict and to_display_dict[d]]
                
        return "".join(active_display_items)
    
    def format_chord(self, chord: Chord, attack_detected: bool) -> str:
        """
        Formate la chaîne de sortie complète pour le mode accord.
        """
        to_display_dict = {
            'chord': self._display_identified_chord(chord, attack_detected),
            'notes': self._display_chord_notes(chord)
        }
        
        active_display_items = [f"{to_display_dict[d]}" for d in self.to_display_items if d in to_display_dict and to_display_dict[d]]
        
        return "".join(active_display_items)
        
    def _display_tuner(self, sound: Sound) -> str:
        """
        Génère la chaîne de caractères de l'accordeur visuel.
        """
        abs_offset = abs(sound.offset)
        color = Color.fg.red
        if 0 <= abs_offset <= 5: color = GRADIENTS[5]
        elif 6 <= abs_offset <= 10: color = GRADIENTS[10]
        elif 11 <= abs_offset <= 15: color = GRADIENTS[15]
        elif 16 <= abs_offset <= 20: color = GRADIENTS[20]

        if abs_offset > 45: abs_offset = 45
        add = 45 - abs_offset
        left_offset = right_offset = 0
        right_add = left_add = 45
        l_arrow_color = l_max_color = r_max_color = r_arrow_color = Color.fg.darkgrey
        if sound.offset < 0:
            left_offset, right_offset = abs_offset, 0
            left_add, right_add = add, 45
            l_arrow_color = color
            if sound.offset <= -45: l_max_color = color
        elif sound.offset > 0:
            left_offset, right_offset = 0, abs_offset
            left_add, right_add = 45, add
            r_arrow_color = color
            if sound.offset >= 45: r_max_color = color

        l_arrow = f"{l_arrow_color}❱{Color.reset}"
        l_max = f"{l_max_color}₋₄₅{Color.reset}"
        l_offset = f"{Color.fg.darkgrey}{'│' * left_add}{color}{'┃' * left_offset}{Color.reset}"
        r_offset = f"{color}{'┃' * right_offset}{Color.fg.darkgrey}{'│' * right_add}{Color.reset}"
        c_note = f"{color}{sound.note:^2}{Color.reset}"
        c_octave = f"{color}{sound.octave:1}{Color.reset}"
        r_max = f"{r_max_color}₊₄₅{Color.reset}"
        r_arrow = f"{r_arrow_color}❰{Color.reset}"

        return f"{l_arrow} {l_max} {l_offset} {c_note}{c_octave} {r_offset} {r_max} {r_arrow}"
    
    def _display_identified_chord(self, chord: Chord, attack_detected: bool) -> str:
        """
        Formate la chaîne de sortie pour l'accord identifié.
        """
        chord_name = f"[{Color.fg.red}¯\\_(ツ)_/¯{Color.reset}]"
        
        if chord.quality and chord.quality.strip():
            chord_name_str = f"{chord.name:^10}"
            if attack_detected:
                chord_name = f"[{Color.fg.green}{chord_name_str}{Color.reset}]"
            else:
                chord_name = f"[{chord_name_str}]"
            
        return f"{Color.bold}{chord_name}{Color.reset}"
    
    def _display_chord_notes(self, chord: Chord) -> str:
        """
        Formate la chaîne de sortie pour les notes composant l'accord.
        Affiche d'abord les notes de l'accord triées, puis les notes restantes.
        """
        notes_to_display = chord.notes

        # On ne peut trier que si on a une fondamentale et une qualité d'accord identifiées.
        if chord.root and chord.quality and chord.quality in CHORD_FORMULAS:
            try:
                root_midi = frequency_to_midi(chord.root.frequency, chord.ref_freq)
                formula = CHORD_FORMULAS[chord.quality]

                # Crée un dictionnaire qui mappe chaque intervalle (en demi-tons) à la note correspondante.
                interval_map = {
                    (frequency_to_midi(s.frequency, chord.ref_freq) - root_midi) % 12: s
                    for s in chord.notes
                }

                # Récupère les notes de l'accord, triées selon la formule.
                sorted_chord_notes = [interval_map[interval] for interval in formula if interval in interval_map]

                # Récupère les notes qui ne font PAS partie de l'accord.
                chord_notes_set = set(sorted_chord_notes)
                other_notes = [s for s in chord.notes if s not in chord_notes_set]
                other_notes.sort(key=lambda s: s.frequency)  # On trie les notes restantes par fréquence.

                # La liste finale est la concaténation des deux.
                notes_to_display = sorted_chord_notes + other_notes

            except Exception:
                # En cas d'erreur inattendue, on se rabat sur l'affichage par défaut (trié par fréquence).
                notes_to_display = sorted(chord.notes, key=lambda s: s.frequency)

        chord_parts = []
        for sound in notes_to_display:
            abs_offset = abs(sound.offset)
            color = Color.fg.red
            if 0 <= abs_offset <= 5: color = GRADIENTS[5]
            elif 6 <= abs_offset <= 10: color = GRADIENTS[10]
            elif 11 <= abs_offset <= 15: color = GRADIENTS[15]
            elif 16 <= abs_offset <= 20: color = GRADIENTS[20]

            note_str = f"{Color.bold}{color}{sound.note:^2}{sound.octave:1}{Color.reset}"

            to_display_dict = {
                'precision': self._display_precision(sound),
                'frequency': self._display_frequency(sound),
                'phase': self._display_phase(sound),
                'signal_level': self._display_signal_level(sound),
            }

            active_display_items = [f"{to_display_dict[d]}" for d in self.to_display_items if d in to_display_dict and to_display_dict[d]]
            chord_parts.append(f"[{note_str} {' '.join(active_display_items)}]")

        notes_display = "".join(chord_parts)

        return f"{notes_display}"
    
    @staticmethod
    def _display_precision(sound: Sound) -> str:
        """
        Formate la chaîne de sortie pour la précision.
        """
        abs_offset = abs(sound.offset)
        color = Color.fg.red
        if 0 <= abs_offset <= 5: color = GRADIENTS[5]
        elif 6 <= abs_offset <= 10: color = GRADIENTS[10]
        elif 11 <= abs_offset <= 15: color = GRADIENTS[15]
        elif 16 <= abs_offset <= 20: color = GRADIENTS[20]
        
        return f"{color}{sound.offset:+3}¢{Color.reset}"
    
    @staticmethod
    def _display_frequency(sound: Sound) -> str:
        """
        Formate la chaîne de sortie pour la fréquence.
        """
        return f"∿ {sound.frequency:6}㎐"
    
    @staticmethod
    def _display_signal_level(sound: Sound) -> str:
        """
        Formate la chaîne de sortie pour le niveau du signal.
        """
        db = round(sound.magnitude_to_db, 0)
        level_index = min(int(abs(db // 15)), len(LEVELS) - 1)
        
        return f"{LEVELS[level_index]} {db:5}㏈"
    
    @staticmethod
    def _display_is_attack(attack_detected, attack) -> str:
        """
        Formate la chaîne de sortie pour la détection d'une attaque.
        """
        attack_str = f" "
        if attack_detected:
            attack_str = f"{Color.fg.red}🗲 {round(attack.novelty_score, 1):+3}{Color.reset}"
        return f"{attack_str:5}"
    
    @staticmethod    
    def _display_phase(sound: Sound) -> str:
        """
        Formate la chaîne de sortie pour la phase.
        """
        return f"φ {round(sound.phase, 0):+2}㎭"
    
    @staticmethod
    def _display_execution_time(execution_time) -> str:
        """
        Formate la chaîne de sortie pour le temps d'exécution.
        """
        return f"⧖ {execution_time:8}″"
    
    @staticmethod
    def _display_egg() -> str:
        """
        Formate la chaîne de sortie pour l'easter egg.
        """
        return f"{random.choice(list(GRADIENTS.values()))}{random.choice(EGGS)}{Color.reset}"
    
    def print_line(self, text: str):
        """Affiche une ligne de texte dans la console, en écrasant la ligne actuelle."""
        # Utilise le code d'échappement ANSI \033[K pour effacer la ligne du curseur à la fin
        print(f"\r{text}\033[K", end='')

    def end_current_line(self):
        """Force le curseur à passer à la ligne suivante."""
        print()

    def print_startup_message(self, ref_freq: int):
        """Affiche le message initial au démarrage de l'application."""
        print(f"{Color.bold} {self.detection_mode} @ {ref_freq}㎐{Color.reset}")
