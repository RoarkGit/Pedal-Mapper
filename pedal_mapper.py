from collections import namedtuple
from enum import Enum
from evdev import UInput, ecodes as e
import hid
import json

# Elgato Stream Deck Pedal Vendor / Product IDs
VENDOR_ID = 0x0FD9
PRODUCT_ID = 0x0086

# Represents a key combination of mods, which are held for the whole
# combination, and keys, which are pressed and released.
KeyCombo = namedtuple("KeyCombo", ["mods", "keys"], defaults=([], []))

# Simple enum that represents the three buttons.
class Button(Enum):
    LEFT = 0
    MIDDLE = 1
    RIGHT = 2

class PedalMapper:
    def __init__(self, config):
        self.button_key_mappings = (
            self.parse_key_combos(config.get("left_keys", [])),
            self.parse_key_combos(config.get("middle_keys", [])),
            self.parse_key_combos(config.get("right_keys", []))
        )
        self.button_state = [False, False, False]
        self.polling_rate = config.get("polling_rate", 10)
        self.dev = hid.device()
        self.dev.open(VENDOR_ID, PRODUCT_ID)
        self.dev.set_nonblocking(1)

        # Register keys in UInput capabilities.
        reg_keys = set()
        for key_combos in self.button_key_mappings:
            for combo in key_combos:
                reg_keys.update(combo.mods)
                reg_keys.update(combo.keys)
        cap = {e.EV_KEY: reg_keys}
        self.ui = UInput(cap, name="Pedal Mapper Virtual Input")

    def parse_key_combos(self, key_combos):
        parsed_combos = []
        for combo in key_combos:
            mods = [getattr(e, mod) for mod in combo.get("mods", [])]
            keys = [getattr(e, key) for key in combo["keys"]]
            parsed_combos.append(KeyCombo(mods, keys))
        return parsed_combos

    def get_event(self):
        # We're non-blocking, so wait for a poll. This could just be changed to
        # blocking instead without issues, but it is non-blocking in case it's
        # actually needed in the future (e.g. handling multiple devices).
        read = self.dev.read(8, self.polling_rate)
        if not read:
            return
        button = None
        if read[4] != self.button_state[0]:
            button = Button.LEFT
        elif read[5] != self.button_state[1]:
            button = Button.MIDDLE
        elif read[6] != self.button_state[2]:
            button = Button.RIGHT
        else:
            return
        self.button_state[button.value] = not self.button_state[button.value]
        return button, self.button_state[button.value]

    def handle_key(self, button, state):
        key_combos = self.button_key_mappings[button.value]
        for combo in key_combos:
            # Press mods first
            if state:
                for mod in combo.mods:
                    self.write_key(mod, state)
                for key in combo.keys:
                    self.write_key(key, state)
            # Release mods last
            else:
                for key in combo.keys:
                    self.write_key(key, state)
                for mod in combo.mods:
                    self.write_key(mod, state)

    # Writes a key to uinput and then syncs.
    def write_key(self, key, state):
        self.ui.write(e.EV_KEY, key, state)
        self.ui.syn()

def load_config(default_path="config.default.json", user_path="config.json"):
    with open(default_path, "r") as f:
        config = json.load(f)

    try:
        with open(user_path, "r") as f:
            user_config = json.load(f)
        config.update(user_config)
    except FileNotFoundError:
        pass

    return config

if __name__ == "__main__":
    # Load the config
    config = load_config()

    # Create Pedal
    pm = PedalMapper(config)

    # Loop to get events and handle them accordingly.
    while True:
        ev = pm.get_event()
        if ev:
            pm.handle_key(ev[0], ev[1])