import subprocess
from typing import List, Tuple, Union
from .runner import Runner

Outcome = str


class ProgramRunner(Runner):
    """Class that take in a program and runs it"""

    def __init__(self, program: Union[str, List[str]]) -> None:
        self.program = program

    def run_process(self, inp: str = "") -> subprocess.CompletedProcess:
        return subprocess.run(
            self.program,
            input=inp,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

    def run(self, inp: str = "") -> Tuple[subprocess.CompletedProcess, Outcome]:
        result = self.run_process(inp)
        if result.returncode == 0:
            outcome = self.PASS
        elif result.returncode < 0:
            outcome = self.FAIL
        else:
            outcome = self.UNRESOLVED
        return (result, outcome)
