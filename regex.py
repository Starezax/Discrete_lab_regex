from __future__ import annotations
from abc import ABC, abstractmethod


class State(ABC):
    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def check_self(self, char: str) -> bool:
        """
        function checks whether occured character is handled by current ctate
        """
        pass

    def check_next(self, text: str, index: int) -> bool:
        if index >= len(text):
            return isinstance(self.next_state, TerminationState)
        if self.check_self(text[index]):
            if self.next_state:
                return self.next_state.check_next(text, index + 1)
            return index + 1 == len(text)
        return False


class StartState(State):
    def __init__(self):
        super().__init__()

    def check_self(self, char):
        return True


class TerminationState(State):
    def __init__(self):
        super().__init__()

    def check_self(self, char: str) -> bool:
        return False

    def check_next(self, text: str, index: int):
        return index == len(text)


class DotState(State):
    def __init__(self):
        super().__init__()

    def check_self(self, char: str):
        return True


class AsciiState(State):
    def __init__(self, symbol: str) -> None:
        super().__init__()
        self.curr_sym = symbol

    def check_self(self, curr_char: str):
        return self.curr_sym == curr_char


class StarState(State):
    def __init__(self, checking_state: State):
        super().__init__()
        self.next_state = None
        self.checking_state = checking_state

    def check_self(self, char):
        return self.checking_state.check_self(char)

    def check_next(self, text: str, index: int) -> bool:
        if self.next_state and self.next_state.check_next(text, index):
            return True

        if index < len(text) and self.check_self(text[index]):
            return self.check_next(text, index + 1)

        return False


class PlusState(State):
    def __init__(self, checking_state: State):
        super().__init__()
        self.next_state = None
        self.checking_state = checking_state

    def check_self(self, char):
        return self.checking_state.check_self(char)

    def check_next(self, text: str, index: int):
        if index < len(text) and self.check_self(text[index]):
            if self.next_state and self.next_state.check_next(text, index + 1):
                return True
            return self.check_next(text, index + 1)
        return False


class RegexFSM:
    def __init__(self, regex_expr: str) -> None:
        self.curr_state = StartState()
        states = []
        i = 0
        while i < len(regex_expr):
            char = regex_expr[i]
            match char:
                case "*":
                    if not states:
                        break
                    last_state = states.pop()
                    star_state = StarState(last_state)
                    states.append(star_state)
                    i += 1
                    continue

                case "+":
                    if not states:
                        break
                    last_state = states.pop()
                    plus_state = PlusState(last_state)
                    states.append(plus_state)
                    i += 1
                    continue

                case ".":
                    new_state = DotState()
                case char if char.isascii():
                    new_state = AsciiState(char)
                case _:
                    raise AttributeError("Character is not supported")

            states.append(new_state)
            i += 1

        for j in range(len(states) - 1):
            states[j].next_state = states[j + 1]

        if states:
            states[-1].next_state = TerminationState()
            self.curr_state.next_state = states[0]
        else:
            self.curr_state.next_state = TerminationState()

    def check_string(self, text):
        return self.curr_state.next_state.check_next(text, 0)


if __name__ == "__main__":
    regex_pattern = "a*4.+hi"
    regex_compiled = RegexFSM(regex_pattern)

    print(regex_compiled.check_string("aaaaaa4uhi"))  # True
    print(regex_compiled.check_string("4uhi"))        # True
    print(regex_compiled.check_string("meow"))        # False
