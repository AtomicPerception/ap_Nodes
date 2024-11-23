'''
    Directly schedule audio weights.
    Atom. 10/24/24.
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

class AudioWeightsSchedule:
    RETURN_TYPES = ("STRING", "FLOAT", "FLOAT", "FLOAT", "FLOAT")
    RETURN_NAMES = ("schedule", "processed_weights", "inverted_weights", "MIN", "MAX")
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
                "threshold": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01}),
                "skip": ("INT", {"default": 1, "min": 1, "max": 12, "step": 1}),
                "weight_boost": ("FLOAT", {"default": 0.0, "min": 0.0,  "max": 2.0, "step": 0.01}),
                "not_less_than_one": ("BOOLEAN", {"default": True}),
                "export_zeros": ("BOOLEAN", {"default": True}),
                "prompt": ("STRING", {"multiline": True, "dynamicPrompts": False, "default": ""}),
                "normalize_weights": ("BOOLEAN", {"default": False}),
                "range_MIN": ("FLOAT", {"default": 0.68, "min": 0.0, "max": 2.0, "step": 0.01}),
                "range_MAX": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 3.0, "step": 0.01}),
            },
        }
   
    def node_update(self, audio_weights, threshold, skip, weight_boost, not_less_than_one,export_zeros, prompt, normalize_weights, range_MIN, range_MAX):
        lst_prompts = []
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
        def extract_index(passedString):
            # Expect: "117": "adorable",
            result = 0
            e = passedString.find('": "')
            s = 1
            result = passedString[s:e]
            #print (f"{passedString}, {result}, {s} to {e}")
            return result
        def extract_value(passedString):
            # Expect: "117": "adorable",
            result = 0
            s = passedString.find('": "')+4
            e = len(passedString)-1
            result = passedString[s:e]
            #print (f"{passedString}, {result}, {s} to {e}")
            return result
        def find_index(passedList, passedIndex):
            for i,item in enumerate(passedList):
                current_index = extract_index(item)
                if current_index == passedIndex:
                    return i
            return -1
        def remove_duplicates(l):
            return list(set(l)) 
   
        if not isinstance(audio_weights, list) and not isinstance(audio_weights, np.ndarray):
            print("AudioWeightsSchedule: Invalid audio_weights input")
            return None, 

        if normalize_weights==True:
            # Normalize audio_weights
            audio_weights = np.array(audio_weights, dtype=np.float32)
            weight_min = np.min(audio_weights)
            weight_max = np.max(audio_weights)
            weights_range = weight_max - weight_min
            weights_normalized = (audio_weights - weight_min) / weights_range if weights_range > 0 else audio_weights - weight_min
            processed_weights = [fit(w, 0.0,1.0, range_MIN, range_MAX) for w in weights_normalized]
            weights_inverted = [fit(w, 0.0,1.0, range_MAX, range_MIN) for w in weights_normalized]
        else:
            # Raw processing.
            # Detect input min/max.
            weight_min = 10000.0
            weight_max = -1.0
            for w in audio_weights:
                if (w<weight_min): weight_min = w
                if (w>weight_max): weight_max = w
            processed_weights = [fit(w, weight_min,weight_max, range_MIN, range_MAX) for w in audio_weights]
            weights_inverted = [fit(w, weight_min,weight_max, range_MAX, range_MIN) for w in audio_weights]
        
        # Detect peaks
        distance = 1.0
        prominence = 0.1
        peaks, _ = find_peaks(processed_weights, height=threshold, distance=distance, prominence=prominence)

        # Generate indices based on peaks
        indices = []
        index_value = 0
        peak_set = set(peaks)
        for i in range(len(processed_weights)):
            if i in peak_set:
                index_value += 1
            indices.append(index_value)

        total_frames = len(indices)
        
        # Map weights to a string.
        result = ""
        for index in range(0,len(processed_weights),skip):
            w = processed_weights [index]
            if w > threshold:
                s = prompt
                s = s.replace("{FRAME}", str(index))
                
                # Initial weight in range 0-1.
                n = fit(w,threshold,1,0,np.pi*2)    	# Normalization to full raidans range.
                wc = fit(np.cos(n),-1.0,1.0,0.0,1.0)	# Map result back to 0-1.
                ws = fit(np.sin(n),-1.0,1.0,0.0,1.0)	# Map result back to 0-1.
                w = w+weight_boost
                wc = wc+weight_boost
                ws = ws+weight_boost
                if not_less_than_one and w < 1.0: w = 1.0
                if not_less_than_one and wc < 1.0: wc = 1.0
                if not_less_than_one and ws < 1.0: ws = 1.0
                s = s.replace("{WEIGHT}", str(w))
                s = s.replace("{WEIGHTCOS}", str(wc))
                s = s.replace("{WEIGHTSIN}", str(ws))
                result += f'{s}, \n'
            else:
                if export_zeros:
                    s = prompt
                    s = s.replace("{FRAME}", str(index))
                    s = s.replace("{WEIGHT}", str(0.0))
                    s = s.replace("{WEIGHTCOS}", str(0.0))
                    s = s.replace("{WEIGHTSIN}", str(0.0))
                    result += f'{s}, \n'
        return(result, processed_weights,weights_inverted,weight_min,weight_max)
        
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {"AudioWeightsSchedule": AudioWeightsSchedule}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {"AudioWeightsSchedule": "Audio Weights Schedule %s" % VERSION}
