import json

class CompetitionsLauncher:
  def __init__(self, competitions_type, description_path):
    self.competitions_type = competition_type
    self.games = None
    self.teams = None
    self.description_path = description_path

  def load(self):
    with open(self.description_f) as f:
      description = json.load(f)
      self.teams = description["teams"]
      self.games = description["games"]



