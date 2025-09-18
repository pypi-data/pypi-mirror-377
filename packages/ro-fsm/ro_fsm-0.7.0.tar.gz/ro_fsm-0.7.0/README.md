# Ro FSM Library

A **lightweight, context-driven finite state machine (FSM) library** for Python that supports:

- States with **entry and exit actions**.
- **Transitions with conditions** based on a user-defined context.
- **Wildcard transitions** for global state changes.
- **YAML-based configuration** for declarative FSM definitions.
- Safe evaluation of actions and conditions (only allowing context-based access).

---

## Installation

```bash
pip install ro_fsm
```

Requires Python ≥3.8 and PyYAML for YAML parsing.

# Overview

A state machine consists of:

- States – Named entities with optional entry/exit actions.
- Transitions – Connections between states, each with a boolean condition evaluated against a context object.
- Context – User-defined object containing the data and methods that drive FSM logic.

# Python API
## State

Represents a single state in the FSM.

```python
State(name: str, entry_action: Optional[Callable[[Any], None]] = None,
      exit_action: Optional[Callable[[Any], None]] = None)
```

- name – Unique string identifier for the state.
- entry_action – Function called when the state is entered (receives context).
- exit_action – Function called when the state is exited (receives context).

Example:

```python
idle = State(
    "Idle",
    entry_action=lambda ctx: print("Entering Idle"),
    exit_action=lambda ctx: print("Exiting Idle")
)
```
## Transition

Encapsulates a transition to another state.
```python
Transition(to_state: str, condition: Optional[Callable[[Any], bool]] = None)
```

- to_state – Destination state name.
- condition – Function returning a boolean; triggers transition if True.

## StateMachine

Manages states, transitions, and context-driven updates.
```python
StateMachine(initial_state: State, context: Any = None, s0_action_flag: bool = True)
```

- initial_state – Starting state of the FSM.
- context – Object passed to all actions and conditions.
- s0_action_flag – Whether to run the entry action of the initial state immediately.

Methods

- add_state(state: State) – Add a new state.
- add_transition(from_state: str, to_state: str, condition: Callable[[Any], bool]) – Add a transition between states.
- set_state(state_name: str, context: Any) – Force a state change.
- update(context: Any = None) – Evaluate transitions and update the state.

### YAML Constructor
```python
StateMachine.from_yaml(path: str, context: Any, s0_action_flag: bool = True)
```

- Loads states, transitions, and initial state from a YAML file.
- Wildcard transitions (from: "*") have priority over state-specific transitions.

# YAML Configuration

Define your FSM declaratively:

```yaml
initial_state: Idle

states:
  - name: Idle
    entry_action: context.log("Idle state")
    exit_action: context.cleanup()
    transitions:
      - to: Active
        condition: context.ready()

  - name: Active
    entry_action: context.start()
    transitions:
      - to: Finished
        condition: context.done()

  - name: Finished

# Wildcard transitions apply globally
transitions:
  - from: "*"
    to: OutOfOrder
    condition: context.error
```

Rules:
1. States cannot be named `"*"`.
2. Actions and conditions must only reference `context`.
3. Top-level transitions (wildcards) override state-specific transitions.
4. Expression evaluation is sandboxed via AST parsing to prevent unsafe code execution.

# Example Usage
```python
from fsm import StateMachine
from context import Context  # user-defined context class

ctx = Context()
sm = StateMachine.from_yaml("vending_machine.yaml", ctx)

# Initial state
print(sm.current_state.name)

# Step through FSM
while sm.current_state.name != "Finished":
    sm.update(ctx)
```

# Best Practices

- Keep actions and conditions pure: avoid side effects outside the context object.
- Use wildcard transitions for emergency/error handling.
- Validate YAML using schema tools to prevent misconfigurations.
- Use entry_action and exit_action for logging, resource management, or triggering side effects.

# Safety & Security

- Conditions and actions are evaluated in a sandbox.
- Only context and its attributes/methods can be accessed in YAML expressions.
- AST parsing prevents arbitrary code execution.

# License

MIT License.