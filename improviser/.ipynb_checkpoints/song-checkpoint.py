import numpy as np
from midiutil import MIDIFile
import pygame
import pandas as pd
from collections import deque 
from functools import reduce

class Note:

    def __init__(self,name=None,n=None,shift=0):
        """
        name is the note of a chord.
        n represent relative location in the twelve equal temperament
        shift = 0 means 4th octave.
        """
        note_name_l = ['C','C#','Db','D','D#',\
                              'Eb','E','F','F#','Gb','G','G#','Ab','A','A#','Bb','B']
        note_loc_l = [0, 1, 1, 2, 3, 3, 4, 5, 6, 6, 7, 8, 8, 9, 10, 10, 11]
        convert_dict = dict(zip(note_name_l,note_loc_l))
        rev_convert_dict = dict(zip(note_loc_l,note_name_l))
        if name and (n is None):
            self.name = name
            self.shift = shift
            self.n = convert_dict[self.name]+(self.shift+5)*12
        elif n and (name is None):
            self.n = n%12
            self.shift = n//12-5
            self.name = rev_convert_dict[self.n]
            
        self.repr_str = f"Note: {self.name} - Octave: {self.shift+4}"
        self.spectrum = [self.n+k for k in [12*(i-3) for i in range(7)]]
            
    def __repr__(self):
        return self.repr_str 
    
    def __str__(self):
        return self.repr_str 
    
    def __sub__(self,other_note):
        """
        measure the distance of two notes. Important right?
        
        other_note is always the chord notes (or extensions); self note is the root.
        """
        
        return (other_note.n%12-self.n)%12
        
class Mode:
    def __init__(self,key,mode_name=None):
        self.key = key
        self.mode_name = mode_name

        
        mode_name_l = ['Ionian','Dorian','Phrygian','Lydian','Mixolydian','Aeolian','Locrian']
        sequence_l = [0,1,2,3,4,5,6]
        name_dict = dict(zip(mode_name_l,sequence_l))
        
        self.sequence = name_dict[self.mode_name]
        
        self.key_note = Note(self.key).n
        
        circle_of_fifth_distance = [2,2,1,2,2,2,1]
        
        mode_distance = deque(circle_of_fifth_distance)
        mode_distance.rotate(-1*self.sequence)
        
        self.current_spin = mode_distance
        mode_distance = [0]+list(self.current_spin)[:-1]

        self.note_n_l = np.cumsum(mode_distance)+self.key_note
        self.note_l = [Note(n=i) for i in self.note_n_l]
        self.repr_str = f"Key: {self.key} - {self.mode_name}\nNotes: {','.join([i.name for i in self.note_l])}"
        
        self.scale = dict(zip(range(1,8),self.note_l))
            
    def __repr__(self):
        return self.repr_str
    
    def __str__(self):
        return self.repr_str

class Chord:
    """
    degree: 1,2,3,4,5,6,7
    1. specify root
    2. specify one of: quality, mode_name, other_notes
    or mode_name and degree (of the bar)
    """
    def __init__(self,root=None,quality=None, other_notes = None):

        self.root = root
        self.root_note = Note(self.root)
        
        quality_list = ['Maj7','m7','dominant7','m7b5','dim']
        mode_list = ['Ionian','Dorian','Mixolydian','Locrian','others']
        distance_list = [frozenset([4,7,11]),frozenset([3,7,10]),frozenset([4,7,10]),frozenset([3,6,10]),frozenset([3,6,9])]
        
        quality2mode_d = dict(zip(quality_list,mode_list))
        distance2quality_d = dict(zip(distance_list,quality_list))

        if quality is not None:
            self.quality = quality
            self.mode_name = quality2mode_d[self.quality]
            self.mode = Mode(key=self.root,mode_name=self.mode_name)
        elif other_notes:
            distance_set = frozenset([self.root_note - other_note for other_note in other_notes])
            self.quality = distance2quality_d[distance_set]
            self.mode_name = quality2mode_d[self.quality]
            self.mode = Mode(key=self.root,mode_name=self.mode_name)
            
        self.scale = self.mode.scale
        self.chord7 = [self.scale[i] for i in [1,3,5,7]]
        self.name = f'{self.root}{self.quality}'
        
    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name
    
class FunctionalChord(Mode):
    """
    given a mode and its degree, get the right chord under the framework of functional harmony.
    """
    def __init__(self,key=None,mode_name=None,degree=1):
        
        super().__init__(key, mode_name)
        self.degree = degree
        
        note_deque = deque(self.note_l)
        note_deque.rotate(-1*(self.degree-1))
        
        note_l = list(note_deque)
        
        self.note_l = [note_l[i-1] for i in [1,3,5,7]]
        
        self.chord = Chord(root=self.note_l[0].name,other_notes=self.note_l[1:])
        
                