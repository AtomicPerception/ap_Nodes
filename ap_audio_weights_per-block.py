'''
    Generated an AnimateDiff per-block schedule from audio weights.
    Atom. 12/03/24.
'''
from scipy.signal import find_peaks
import numpy as np
import json

VERSION = "1.0"


# Taken from Anything nodes.
class AlwaysEqualProxy(str):
    def __eq__(self, _):
        return True
    def __ne__(self, _):
        return False

class AudioWeightsPerBlock:
    RETURN_TYPES = ("STRING", "STRING", "STRING",)
    RETURN_NAMES = ("per-block_schedule", "inverted_schedule", "temporally_reversed_per-block_schedule")
    #RETURN_NAMES = ("code", "string", "float", "int", "list")
    #OUTPUT_IS_LIST = (False, False, False, False, True,)
    
    FUNCTION = "node_update"
    CATEGORY = "ap_Nodes"
    
    def __init__(self):
        self.last_output = ""
        pass   
        
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "audio_weights": ("FLOAT", {"forceInput": True}),
                "range_MIN": ("FLOAT", {"default": 0.70, "min": 0.0, "max": 2.0, "step": 0.01}),
                "range_MAX": ("FLOAT", {"default": 1.10, "min": 0.0, "max": 3.0, "step": 0.01}),
            },
        }
   
    def node_update(self, audio_weights, range_MIN, range_MAX):
         #https://gist.github.com/laundmo/b224b1f4c8ef6ca5fe47e132c8deab56
        def lerp(a: float, b: float, t: float) -> float:
            return (1 - t) * a + t * b
        def inv_lerp(a: float, b: float, v: float) -> float:
            return (v - a) / (b - a)
        def fit(v: float, i_min: float, i_max: float, o_min: float, o_max: float) -> float:
            bias = v
            if bias>i_max: bias = i_max
            if bias<i_min: bias = i_min
            return lerp(o_min, o_max, inv_lerp(i_min, i_max, bias))
   
        if not isinstance(audio_weights, list) and not isinstance(audio_weights, np.ndarray):
            print("AudioWeightsFit: Invalid audio_weights input")
            return None, 

        # Raw processing.
        # Detect input min/max.
        weight_min = 10000.0
        weight_max = -1.0
        for w in audio_weights:
            if (w<weight_min): weight_min = w
            if (w>weight_max): weight_max = w
        processed_weights = [fit(w, weight_min,weight_max, range_MIN, range_MAX) for w in audio_weights]
        weights_inverted = [fit(w, weight_min,weight_max, range_MAX, range_MIN) for w in audio_weights]
        
        #Build string-based schedule.
        frame = 0
        s = ""
        for weight in processed_weights:
            s += f"{frame}={weight},\n"
            frame +=1
        frame = 0
        si = ""
        for weight in weights_inverted:
            si += f"{frame}={weight},\n"
            frame +=1
        frame = 0
        sti = ""
        for weight in reversed(processed_weights):
            sti += f"{frame}={weight},\n"
            frame +=1

        return(s, si, sti)
        
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {"AudioWeightsPerBlock": AudioWeightsPerBlock}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {"AudioWeightsPerBlock": "Audio Weights Per-Block %s" % VERSION}
