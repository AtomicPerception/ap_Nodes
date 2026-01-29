'''
    Schedule Wan Prompts
    Atom. 01/29/26.
'''

VERSION = "1.0"
import torch
from comfy import model_management

class ap_WanScheduledConditioning:
    def __init__(self):
        pass
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "clip": ("CLIP",),
                "prompts": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "a red dog | a blue cat | a pink elephant"
                    }
                ),
            }
        }

    RETURN_TYPES = ("CONDITIONING",)
    FUNCTION = "schedule"
    CATEGORY = "conditioning"
    OUTPUT_TOOLTIPS = ("Allows multiple prompts separated by the | pipe character.",)

    def schedule(self, clip, prompts):
        prompt_list = [p.strip() for p in prompts.split("|") if p.strip()]
        count = len(prompt_list)

        if count == 0:
            return ([],)

        conditioning = []

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

