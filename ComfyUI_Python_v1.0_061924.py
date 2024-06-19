'''
    ComfyUI_Python_v1.0_061924
    A node to execute python.
    The resulting print() statement ends up as the output, if any.
    (c) 2024 Atom.
'''

import subprocess
from time import gmtime, strftime

#from PIL import Image, ImageOps, ImageSequence, ImageFile
#from PIL.PngImagePlugin import PngInfo

#import folder_paths
#import comfy
#print(dir(comfy))


# This is the default code placed in the new textbox.
def code ():
    """#https://gist.github.com/laundmo/b224b1f4c8ef6ca5fe47e132c8deab56
def lerp(a: float, b: float, t: float) -> float:
    return (1 - t) * a + t * b
def inv_lerp(a: float, b: float, v: float) -> float:
    return (v - a) / (b - a)
def fit(v: float, i_min: float, i_max: float, o_min: float, o_max: float) -> float:
    bias = v
    if bias>i_max: bias = i_max
    if bias<i_min: bias = i_min
    return lerp(o_min, o_max, inv_lerp(i_min, i_max, bias))
        
current_frame = PYTHON_CODE_BOX_SEED

# Animate value using fit.
value = fit(current_frame, 0, 120, 0.3, 0.6)
print(value)
"""

class PythonSnippet:
    #RETURN_TYPES = ("STRING",)
    #RETURN_NAMES = ("text",)
    
    RETURN_TYPES = ("STRING","FLOAT", "INT",)
    RETURN_NAMES = ("text", "float", "int",)
    
    FUNCTION = "node_update"
    CATEGORY = "Scripting"
    
    def __init__(self):
        #print("__init__")

        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "dynamicPrompts": False, "default": code.__doc__}),
                "seed": ("INT", {"default": 311, "step": 1, "display": "number"})
            },
        }
   
    def node_update(self, text, seed):
        # Grab the seed from the node to set initial random seed.
        code = "import random; random;PYTHON_CODE_BOX_SEED=%s;random.seed(PYTHON_CODE_BOX_SEED);%s" %(seed,text)
        proc = subprocess.Popen(["python", "-c", code], stdout=subprocess.PIPE)
        code_result = proc.communicate()[0]
        
        # Fix up result.
        convert_result = code_result.decode()
        convert_result = "".join(convert_result.rstrip()) 
        
        # Attempt numeric conversion of result.
        try:
            rf= float(code_result.decode())		# float output.
        except:
            rf = 0.0
        try:
            ri = int(code_result.decode())		# int output.
        except:
            ri = 0

        t = strftime("%m-%d-%Y %H:%M:%S", gmtime())
        print("\033[36m[%s] PCB--> %s\033[0m" % (t,code_result.decode()))

        return (convert_result, rf, ri,)
        #return (convert_result, )

    @classmethod
    def IS_CHANGED(self, text, seed):
        node_update(self, text, seed)
        return ("",)
        
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {"PythonSnippet": PythonSnippet}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {"PythonSnippet": "Python Code Box"}
