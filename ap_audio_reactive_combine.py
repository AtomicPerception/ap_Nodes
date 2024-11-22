'''
    A node combine three scheduled prompt lists.
    Atom. 10/24/24.
'''

import json

VERSION = "1.0"

class AlwaysEqualProxy(str):
    def __eq__(self, _):
        return True
    def __ne__(self, _):
        return False

class AudioReactiveCombine:
    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("Schedule",)
    
    FUNCTION = "node_update"
    CATEGORY = "ap_Nodes"
    
    def __init__(self):
        self.last_output = ""
        pass   
        
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "dynamicPrompts": False, "default": ""}),
                "skip": ("INT", {"default": 1, "min": 1, "max": 48, "step": 1}),
                "seed": ("INT", {"default": 311, "step": 1, "display": "number"}),
            },
            "optional": {
                "in1": (AlwaysEqualProxy("*"), ),
                "in2": (AlwaysEqualProxy("*"), ),
                "in3": (AlwaysEqualProxy("*"), ),
            }
        }
   
    def node_update(self, prompt, skip, seed, in1=None, in2=None, in3=None):
        def extract_index(passedString):
            if not passedString or len(passedString.strip()) == 0:
                return None
            try:
                # Extract everything between first quote and ": "
                s = passedString.find('"') + 1
                e = passedString.find('": "')
                if e == -1 or s == 0:  # If format doesn't match
                    return None
                result = passedString[s:e]
                return result.strip()
            except:
                return None

        def extract_value(passedString):
            if not passedString or len(passedString.strip()) == 0:
                return ""
            try:
                s = passedString.find('": "') + 4
                if s < 4:  # If format doesn't match
                    return ""
                e = passedString.rfind('"')  # Find last quote
                if e == -1:
                    e = len(passedString)
                return passedString[s:e]
            except:
                return ""

        def clean_split(text):
            if not text:
                return []
            # Split by comma and filter out empty strings
            parts = [p.strip() for p in text.split(',')]
            return [p for p in parts if p]

        # Process inputs
        s1 = clean_split(''.join(in1)) if in1 is not None else []
        s2 = clean_split(''.join(in2)) if in2 is not None else []
        s3 = clean_split(''.join(in3)) if in3 is not None else []
        
        # Collect all valid indices
        all_indices = set()
        for item in s1 + s2 + s3:
            idx = extract_index(item)
            if idx is not None and idx.isdigit():
                all_indices.add(int(idx))
        
        # Ensure we have frame 0
        all_indices.add(0)
        
        # Sort indices
        sorted_indices = sorted(all_indices)
        
        # Create result
        result = ""
        prev_prompt = None
        
        for ndx in sorted_indices:
            val1 = val2 = val3 = ""
            str_ndx = str(ndx)
            
            # Find matching values for each input
            for item in s1:
                if extract_index(item) == str_ndx:
                    val1 = extract_value(item)
                    break
            
            for item in s2:
                if extract_index(item) == str_ndx:
                    val2 = extract_value(item)
                    break
                    
            for item in s3:
                if extract_index(item) == str_ndx:
                    val3 = extract_value(item)
                    break
            
            # Replace placeholders in prompt
            s = prompt
            s = s.replace("{IN1}", val1)
            s = s.replace("{IN2}", val2)
            s = s.replace("{IN3}", val3)
            
            # Only add if the prompt is different from the previous one
            if s != prev_prompt:
                result += f'"{str_ndx}": "{s}",\n'
                prev_prompt = s
            
        # Ensure the result isn't empty
        if not result.strip():
            result = '"0": "",\n'
            
        return (result,)
        
    @classmethod
    def IS_CHANGED(self, prompt, skip, seed, in1=None, in2=None, in3=None):
        return ("",)

# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {"AudioReactiveCombine": AudioReactiveCombine}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {"AudioReactiveCombine": "Audio Reactive Combine %s" % VERSION}
