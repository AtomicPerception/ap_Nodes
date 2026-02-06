'''
    Process Yvann Audio Reactive Peak Frame List.
    Atom. 02/06/26.
'''

VERSION = "1.0"

class ap_AudioFrameSchedule:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "values": (
                    "STRING",
                    {
                        "default": "0, 3, 25, 38",
                        "multiline": False,
                    },
                ),
                "index": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "step": 1,
                    },
                ),
            }
        }

    RETURN_TYPES = ("INT", "INT", "INT")
    RETURN_NAMES = ("value", "distance", "count")
    FUNCTION = "get_value"
    CATEGORY = "utils"

    def get_value(self, values: str, index: int):
        # Parse comma-delimited string into integers
        try:
            int_list = [int(v.strip()) for v in values.split(",") if v.strip() != ""]
        except ValueError:
            raise ValueError("Values must be a comma-delimited list of integers")

        if not int_list:
            raise ValueError("No valid integers found in input string")

        count = len(int_list)

        # Clamp index to valid range
        index = max(0, min(index, count - 1))

        current_value = int_list[index]

        if index == 0:
            distance = 0
        else:
            previous_value = int_list[index - 1]
            distance = abs(current_value - previous_value)

        return (current_value, distance, count)


NODE_CLASS_MAPPINGS = {
    "ap_AudioFrameSchedule": ap_AudioFrameSchedule,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ap_AudioFrameSchedule": f"Audio Frame Schedule {VERSION}",
}
