'''
    Schedule Wan Prompts
    Atom. 01/29/26.
'''

VERSION = "1.0"
import torch
import re
import json
from comfy import model_management

def process_input_text(text: str) -> dict:
    # From FizzNodes.
    input_text = text.replace('\n', '')
    input_text = "{" + input_text + "}"
    input_text = re.sub(r',\s*}', '}', input_text)
    animation_prompts = json.loads(input_text.strip())
    return animation_prompts
    
class ap_WanScheduledConditioning:
    def __init__(self):
        pass
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "clip": ("CLIP",),
                "prompts": ("STRING", {"multiline": True,"default": "a red dog | a blue cat | a pink elephant"}),
                "delimiter": ("STRING", {"multiline": False, "default": "|"}),
                "emulate_fizznode": ("BOOLEAN", {"default": False}),
                "batch_length": ("INT", {"default": 25, "min": 1, "max": 1661, "step": 4}),
            }
        }

    RETURN_TYPES = ("CONDITIONING",)
    FUNCTION = "schedule"
    CATEGORY = "conditioning"
    OUTPUT_TOOLTIPS = ("Conditions multiple prompts separated by the delimiting token.",)

    def schedule(self, clip, prompts, delimiter="|", emulate_fizznode=False, batch_length=25):
        conditioning = []
        if emulate_fizznode:
            # Process prompt info using FizzleDorf method.
            animation_prompts = process_input_text(prompts)
            for i, key in enumerate(animation_prompts.keys()):
                frame_now = int(key)
                if i == len(animation_prompts.keys())-1:
                    # No next frame available, hit the wall with batch_length.
                    frame_next = batch_length
                else:
                    frame_next = int(list(animation_prompts.keys())[i+1])
                if frame_now <= batch_length:
                    start = frame_now/batch_length
                    end = frame_next/batch_length
                    prompt = list(animation_prompts.values())[i]

                    cond = clip.encode_from_tokens_scheduled(clip.tokenize(prompt))

                    # cond is [[tokens, {pooled_output}]]
                    tokens, meta = cond[0]

                    conditioning.append([
                        tokens,
                        {
                            "pooled_output": meta.get("pooled_output"),
                            "start_percent": start,
                            "end_percent": end
                        }
                    ])
        else:
            # Evenly distributed through time.
            prompt_list = [p.strip() for p in prompts.split(delimiter) if p.strip()]
            count = len(prompt_list)

            if count == 0:
                return ([],)

            for i, prompt in enumerate(prompt_list):
                start = i / count
                end = (i + 1) / count

                cond = clip.encode_from_tokens_scheduled(clip.tokenize(prompt))

                # cond is [[tokens, {pooled_output}]]
                tokens, meta = cond[0]

                conditioning.append([
                    tokens,
                    {
                        "pooled_output": meta.get("pooled_output"),
                        "start_percent": start,
                        "end_percent": end
                    }
                ])

        return (conditioning,)

# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {"ap_WanScheduledConditioning": ap_WanScheduledConditioning}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {"ap_WanScheduledConditioning": "Wan Scheduled Conditioning %s" % VERSION}

