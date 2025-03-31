class GameState:
    def __init__(self):
        self.score = 0
        self.entities = {}

    def update(self, changes):
        # Update logic here
        pass

    def update_score(self, increment):
        self.score += increment

    def is_game_over(self):
        # Determine if the game should end
        return False
