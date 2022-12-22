import functools
from typing import Any, Callable, Dict


class Step:
    def __init__(self, number: int, description: str, func: Callable):
        self.number = number
        self.description = description
        self.func = func


class StepManager:
    def __init__(self, transition_duration: float = 3, highlights: Dict[str, Any] = {}):
        self.current_step: int = 0
        self.highlights = highlights
        self.steps: Dict[int, Step] = {}
        self.transition_duration = transition_duration

    def register(self, description: str):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                print("Something is happening before the function is called.")
                # foo = func(*args, **kwargs)
                self.steps[len(self.steps)] = Step(
                    number=len(self.steps),
                    description=description,
                    func=func,
                )
                print("Something is happening after the function is called.")
                # return foo

            return wrapper

        return decorator

    def next(self):
        self.current_step += 1

    def run(self):
        for _, step in self.steps.items():
            step.func()
