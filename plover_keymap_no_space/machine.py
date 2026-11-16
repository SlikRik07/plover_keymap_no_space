from plover.machine.keyboard import Keyboard
from plover.machine.keymap import Keymap
import json
from collections import OrderedDict


ATTACH = "no-space"
ATTACH_STROKE = {"T-", "K-", "-L", "-S"}  # the stroke that is {^^} in your dictionary

# Make the Keymap accept the action (dropdown and validation).
_orig_init = Keymap.__init__

def _init(self, keys, actions):
    actions = tuple(actions)
    if "arpeggiate" in actions and ATTACH not in actions:  # keyboard machines only
        actions += (ATTACH,)
    _orig_init(self, keys, actions)

Keymap.__init__ = _init

# Expand the action into two strokes.
_orig_notify = Keyboard._notify

def _notify(self, steno_keys):
    if ATTACH in steno_keys:
        steno_keys = set(steno_keys) - {ATTACH}
        _orig_notify(self, set(ATTACH_STROKE))  # the {^^} stroke
    if steno_keys:
        _orig_notify(self, steno_keys)

Keyboard._notify = _notify
_orig_set_mappings = Keymap.set_mappings

# Prevents no-space is not bound warning.
def _set_mappings(self, mappings):
    if isinstance(mappings, str):
        mappings = json.loads(mappings)
    mappings = dict(mappings)
    if ATTACH in self._actions and not mappings.get(ATTACH):
        full = self._actions
        self._actions = OrderedDict((a, n) for a, n in full.items() if a != ATTACH)
        # Also drop the unbound entry, or it gets reported as an invalid action.
        mappings.pop(ATTACH, None)
        try:
            _orig_set_mappings(self, mappings)
        finally:
            self._actions = full
        self._mappings[ATTACH] = ()
    else:
        _orig_set_mappings(self, mappings)

Keymap.set_mappings = _set_mappings
