from .level import LevelLoader


class Server:
    def __init__(self, app_path):
        self.level_loader = LevelLoader(app_path)
        self.current_level_idx = 0
        self.current_level = None
        self.selected_character = None
        self.user_events = []

    def __repr__(self):
        return f"Server(Level: {self.current_level})"

    def start_level(self):
        self.current_level = self.level_loader[self.current_level_idx]
        self.selected_character = self.current_level.hero

    def add_event(self, event):
        self.user_events.append(event)

    def update(self, dt):
        self.process_user_events()
        game_result = self.current_level.step(dt)
        if not game_result:
            self.end_level(game_result)
        return game_result  # and state

    def process_user_events(self):
        for event in self.user_events:
            # Process HUD EVENTS
            self.current_level.update(self.selected_character, event)
        self.user_events = []

    def end_level(self, game_result):
        if game_result.won:
            self.current_level_idx += 1
