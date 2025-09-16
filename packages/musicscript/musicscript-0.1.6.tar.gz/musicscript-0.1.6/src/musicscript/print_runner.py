from .runner import Runner
from typing import Any


class PrintRunner(Runner):
    """A program runner that simply prints out inputs provided to it"""

    def run(self, inp) -> Any:
        print(inp)
        return (inp, Runner.UNRESOLVED)
