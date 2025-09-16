from typing import Any


class Runner:
    """Base class to run other programs"""

    PASS = "PASS"
    FAIL = "FAIL"
    UNRESOLVED = "UNRESOLVED"

    def __init__(self) -> None:
        pass

    def run(self, inp: str) -> Any:
        return (inp, Runner.UNRESOLVED)
