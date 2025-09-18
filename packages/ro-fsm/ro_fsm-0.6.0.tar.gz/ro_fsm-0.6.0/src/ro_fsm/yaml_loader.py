import yaml
import ast
from typing import Any, Callable

class SafeExpressionEvaluator(ast.NodeVisitor):
    """
    Validates that expressions only reference `context`.
    Supports attribute access and calls like `context.foo()`, `context.bar < 5`, etc.
    """
    def __init__(self, source: str):
        self.source = source

    def validate(self):
        tree = ast.parse(self.source, mode="eval")
        self.visit(tree)
        return compile(tree, "<expr>", "eval")

    def visit_Name(self, node):
        if node.id != "context":
            raise ValueError(f"Illegal name '{node.id}' in expression '{self.source}'")
        self.generic_visit(node)

    def visit_Call(self, node):
        if not (isinstance(node.func, ast.Attribute) and self._is_context_base(node.func)):
            raise ValueError(f"Function calls must be accessed from 'context' in expression '{self.source}'")
        self.generic_visit(node)

    def _is_context_base(self, attr):
        while isinstance(attr, ast.Attribute):
            attr = attr.value
        return isinstance(attr, ast.Name) and attr.id == "context"


def _make_action(expr: str) -> Callable[[Any], None]:
    compiled = SafeExpressionEvaluator(expr).validate()
    return lambda context: eval(compiled, {}, {"context": context})


def _make_condition(expr: str) -> Callable[[Any], bool]:
    compiled = SafeExpressionEvaluator(expr).validate()
    return lambda context: eval(compiled, {}, {"context": context})


def load_from_yaml(path: str):
    """
    Load states and transitions from a YAML file.
    Returns: (states_list, transitions_list, initial_state_name)
    """
    with open(path) as f:
        config = yaml.safe_load(f)

    states = []
    transitions = []

    for s in config.get("states", []):
        if s["name"] == "*":
            raise ValueError("State name '*' is reserved for wildcard transitions")

        entry = _make_action(s["entry_action"]) if "entry_action" in s else None
        exit = _make_action(s["exit_action"]) if "exit_action" in s else None
        states.append((s["name"], entry, exit))

        # collect transitions defined inside this state
        for t in s.get("transitions", []):
            if t["to"] == "*":
                raise ValueError("Wildcard '*' cannot be used as a destination state")
            cond = _make_condition(t["condition"]) if "condition" in t else None
            transitions.append((s["name"], t["to"], cond))

    # keep backward compatibility: also allow top-level transitions
    for t in config.get("transitions", []):
        if t["to"] == "*":
            raise ValueError("Wildcard '*' cannot be used as a destination state")
        cond = _make_condition(t["condition"]) if "condition" in t else None
        transitions.append((t["from"], t["to"], cond))

    initial_state = config.get("initial_state")
    if initial_state is None:
        raise ValueError("YAML file must specify an initial_state")

    return states, transitions, initial_state
