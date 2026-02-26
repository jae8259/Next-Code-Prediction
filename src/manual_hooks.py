import subprocess
from abc import ABC, abstractmethod


class ManualHook(ABC):
    @abstractmethod
    def execute(self, answer: str) -> str:
        pass


class ManManualHook(ManualHook):
    def execute(self, answer: str) -> str:
        try:
            process = subprocess.run(
                ["man", answer], capture_output=True, text=True, check=True)
            return process.stdout
        except (subprocess.CalledProcessError, FileNotFoundError):
            return f"No manual provided for '{answer}'."


class ManualHookFactory:
    def get_hook(self, hook_type: str) -> ManualHook:
        if hook_type == "man":
            return ManManualHook()
        else:
            raise ValueError(f"Unknown hook type: {hook_type}")
