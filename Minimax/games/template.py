
# The State class for your game
# The State class must implement get_moves() and get_evaluation()
class State:
    def __init__(self):
        self.evaluation = None
        # Initial value of self.branches must be None
        # If set as an empty list, minimax will treat the state as a leaf/terminal state with no branches
        self.branches = None 

    # ======== REQUIRED METHODS ======== #

    # To use the minimax.print_tree() method, the State class must implement __repr__ 
    def __repr__(self) -> str:
        # ...
        return f"State()"

    # Returns a list of State objects
    def get_moves(self) -> list[State]:
        if self.branches is None:
            self.branches = []
        # ...
        return self.branches

    # Returns a floating number representing the evaluation of this State
    def get_evaluation(self) -> float:
        if self.evaluation is None:
            self.evaluation = 0.0
        # ...
        return self.evaluation
