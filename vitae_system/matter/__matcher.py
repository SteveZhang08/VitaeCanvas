from __seq import ESeq
from typing import Set, Tuple, List
from Constants import FunctionRule, E_ProteinFunc


class ProteinFunctionMatcher:
    def __init__(self, rules: Set[FunctionRule]):
        self.rules = sorted(rules, key=lambda r: r.priority)  # Sort by priority

    def match(self, sequence: ESeq) -> Tuple[E_ProteinFunc, ...]:
        matched: List[E_ProteinFunc] = []
        i = 0
        while i < len(sequence):
            for rule in self.rules:
                slice_seq = sequence.slice(i, i + len(rule.seq))
                if slice_seq == rule.seq:
                    matched.append(rule.function)
                    if rule.exclusive:
                        i += len(rule.seq)  # Skip matched section
                    break
            else:
                i += 1  # Nothing matched
        return tuple(matched)
