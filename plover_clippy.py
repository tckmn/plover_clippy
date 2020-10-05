import re
import os
from datetime import datetime

from plover import log
from plover.engine import StenoEngine
from plover.formatting import RetroFormatter
from plover.oslayer.config import CONFIG_DIR

class Clippy:
    fname = os.path.join(CONFIG_DIR, 'clippy.txt')

    @staticmethod
    def tails(ls):
        for i in reversed(range(len(ls))): yield ls[i:]

    def __init__(self, engine: StenoEngine) -> None:
        super().__init__()
        self.engine: StenoEngine = engine

    def start(self) -> None:
        self.engine.hook_connect('translated', self.on_translation)
        self.f = open(self.fname, 'a')

    def stop(self) -> None:
        self.engine.hook_disconnect('translated', self.on_translation)
        self.f.close()

    def on_translation(self, old, new):

        # verify new output exists
        for a in reversed(new):
            if a.text and not a.text.isspace(): break
        else: return

        # check for optimality
        last = None
        for phrase in self.tails(self.engine.translator_state.translations[-10:]):
            english = ''.join(RetroFormatter(phrase).last_fragments(999))
            if english == last: continue
            last = english
            stroked = [y for x in phrase for y in x.rtfcre]
            suggestions = [y for x in self.engine.get_suggestions(english) for y in x.steno_list if len(y) < len(stroked)]
            if suggestions:
                self.f.write(f'[{datetime.now().strftime("%F %T")}] {english:15} || {"/".join(stroked)} -> {", ".join("/".join(x) for x in suggestions)}\n')
                self.f.flush()
