from typing import Callable, Dict, List, Optional, Tuple, Any
from .yaml_loader import load_from_yaml

class State:
    """ 
    Represents a state in a state machine. 
    
    Each state has an entry and exit action that are executed when the state is entered and exited, respectively. 
    The entry and exit actions default to no action and can be overridden by passing a function to the constructor.
    """
    
    def __init__(self, name: str, 
                 entry_action: Optional[Callable[[Any], None]] = None, 
                 exit_action: Optional[Callable[[Any], None]] = None):
        """
        __init__ method for State class.

        Arguments:
            name {str} -- The name of the state.

        Keyword Arguments:
            entry_action {(Any) -> None} -- Entry action (default: empty function)
            exit_action {(Any) -> None} -- Exit action (default: empty function)
        """
        self.name: str = name
        self.entry_action = entry_action or self._no_action
        self.exit_action = exit_action or self._no_action

    def _no_action(self, context: Any = None) -> None:
        pass

    def __repr__(self) -> str:
        return self.name

class Transition:
    """
    Represents a transition to a state in a state machine.
    
    Each transition has a destination state and an optional condition that must be met for the transition to occur.
    """
    
    def __init__(self, to_state: str, 
                 condition: Optional[Callable[[Any], bool]] = None):
        """
        __init__ method for Transition class.

        Arguments:
            to_state {str} -- The name of the destination state.

        Keyword Arguments:
            condition {(Any) -> bool} -- Condition to trigger the transition (default: always True)
        """
        
        self.to_state: str = to_state
        self.condition: Callable[[Any], bool] = condition or (lambda _: True)
    
    def is_triggered(self, context: Any = None) -> bool:
        """
        Checks if the transition is triggered based on the condition.

        Arguments:
            context {Any} -- Optional context to pass to the condition function (default: None)

        Returns:
            bool -- True if the transition is triggered, False otherwise.
        """
        
        return self.condition(context)

class StateMachine:
    """
    Represents a state machine that manages states and transitions between them.
    
    The state machine has a current state and a dictionary of states and transitions.
    The state machine can add states, add transitions between states, set the current state, and update the state machine.
    """
    
    def __init__(self, initial_state: State, context: Any = None, s0_action_flag: bool = True):
        """
        __init__ method for StateMachine class.

        Arguments:
            initial_state {State} -- The initial state of the state machine.
            context {Any} -- The context for the first state action.
            s0_action_flag {bool} -- Whether to perform the initial state entry action on startup.
        """
        
        self.states: Dict[str, State] = {}
        self.transitions: Dict[str, List[Transition]] = {}
        self.current_state: State = initial_state
        if s0_action_flag and context is not None:
            self.current_state.entry_action(context)
        self.previous_state: Optional[State] = None
    
    @classmethod
    def from_yaml(cls, path: str, context: Any, s0_action_flag: bool = True):
        """
        Creates a StateMachine instance from a YAML file.
        
        Arguments:
            path {str} -- Path to the YAML file.
            context {Any} -- Context to pass to the initial state's entry action.
            s0_action_flag {bool} -- Whether to perform the initial state entry action on startup (default: True).
        
        Returns:
            StateMachine -- The created StateMachine instance.
        """
        states_raw, transitions, initial_state = load_from_yaml(path)
        
        states = {}
        for name, entry, exit in states_raw:
            states[name] = State(name, entry, exit)

        sm = cls(states[initial_state], context, s0_action_flag)
        for st in states.values():
            sm.add_state(st)

        for frm, to, cond in transitions:
            sm.add_transition(frm, to, cond)

        return sm
        
    def add_state(self, state: State) -> None:
        """
        Adds a state to the state machine.

        Arguments:
            state {State} -- The state to add to the state machine.
        """
        
        self.states[state.name] = state

    def add_transition(self, from_state: str, to_state: str, 
                       condition: Callable[[Any], bool] = lambda _: True) -> None:
        """
        Adds a transition between two states in the state machine.

        Arguments:
            from_state {str} -- starting state
            to_state {str} -- ending state
            condition {() -> bool} -- condition to transition from from_state to to_state
        """
        
        if from_state not in self.transitions:
            self.transitions[from_state] = []
        self.transitions[from_state].append(Transition(to_state, condition))

    def set_state(self, state_name: str, context: Any) -> None:
        """
        Sets the current state of the state machine to a new state.
        This method also executes the exit action of the current state and the entry action of the new state.

        Arguments:
            state_name {str} -- The name of the new state to set as the current state.
            context {Any} -- The context to pass to the entry and exit actions.

        Raises:
            ValueError: If the state name does not exist in the state machine.
        """
        if state_name in self.states:
            self.previous_state = self.current_state
            self.current_state.exit_action(context)
            self.current_state = self.states[state_name]
            self.current_state.entry_action(context)
        else:
            raise ValueError(f"State {state_name} does not exist in the state machine")

    def update(self, context: Any = None) -> None:
        """
        Updates the state of the state machine based on the transitions defined.
        
        Arguments:
            context {Any} -- Optional context to pass to the condition functions (default: None)
        """
        # wildcard first
        candidates = self.transitions.get("*", []) + \
                    self.transitions.get(self.current_state.name, [])

        for tr in candidates:
            if tr.condition(context):
                self.set_state(tr.to_state, context)
                break

