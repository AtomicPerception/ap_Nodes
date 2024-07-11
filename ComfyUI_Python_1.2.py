'''
    A node to execute python.
    The resulting print() statement ends up as the output, if any.
    Version 1.2
        New code injection input and companion output.
        Access to last generated value through PREVIOUS_OUTPUT constant.
    (c) 2024 Atom. 06/24/24.
'''

VERSION = "1.2"

import subprocess
from time import gmtime, strftime

# Taken from Anything nodes.
class AlwaysEqualProxy(str):
    def __eq__(self, _):
        return True
    def __ne__(self, _):
        return False

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

# Special CONSTANTS made available to the code box.
in1 = IN1.decode()        
current_frame = PYTHON_CODE_BOX_SEED

'''
index = int(current_frame/hold_frames)
hold_start = hold_frames * index
hold_end = hold_start + hold_frames
# Percentage traveled through hold time.
bias = fit(current_frame,hold_start,hold_end,1.0,0.0)
'''

# Animate value using fit.
# frame, input min, input max, output min, output max
value = fit(current_frame, 0, 120, 0.3, 0.6)
print(value)
"""

class PythonSnippet:
    RETURN_TYPES = ("STRING", "STRING", "FLOAT", "INT",)
    RETURN_NAMES = ("code", "string", "float", "int",)
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
                "text": ("STRING", {"multiline": True, "dynamicPrompts": False, "default": code.__doc__}),
                "seed": ("INT", {"default": 311, "step": 1, "display": "number"}),
                
            },
            "optional": {
                "code_inject": (AlwaysEqualProxy("*"), ),
                "in1": (AlwaysEqualProxy("*"), ),
                "in2": (AlwaysEqualProxy("*"), ),
                "in3": (AlwaysEqualProxy("*"), ),
            }
        }
   
    def node_update(self, text, seed, code_inject=None, in1=None, in2=None, in3=None):
        # Make the input values available inside the code box.
        s1 = ""
        s2 = ""
        s3 = ""
        if (in1!=None):
            s1 = str(in1)
        if (in2!=None):
            s2 = str(in2)
        if (in3!=None):
            s3 = str(in3)
        code_string = 'import random; PYTHON_CODE_BOX_SEED={};random.seed(PYTHON_CODE_BOX_SEED);IN1={};IN2={};IN3={};PREVIOUS_OUTPUT={};\n{}'.format(seed,s1.encode(),s2.encode(),s3.encode(),self.last_output.encode(),text)
        if code_inject!=None:
            # Grab code from the input to prefix the user's text box.
            code = code_inject
            code += "\n" + code_string
        else:
            # Grab the seed from the node to set initial random seed.
            code = code_string
        #print("[%s]" %code)
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
        print("\033[36m[{}] PCB--> {}\033[0m".format(t,convert_result))
        #return (code, convert_result, rf, ri,)
        return {"ui": {
            "text": [f"{rf}x{ri}"]}, 
            "result": (code, convert_result, rf, ri,) 
        }
        
    @classmethod
    def IS_CHANGED(self, text, seed, code_inject = None, in1=None, in2=None, in3=None):
        #node_update(self, text, seed, code_inject, in1, in2, in3)
        return ("",)
        
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {"PythonSnippet": PythonSnippet}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {"PythonSnippet": "Python Code Box %s" % VERSION}
