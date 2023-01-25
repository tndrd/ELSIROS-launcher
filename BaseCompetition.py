import os

class Competition:
  def __init__(self, teams, world, game_json):
    self.world = world
    self.game_json = game_json
    self.teams = teams 

  def launch(self):
    self.assign_all_teams()
    self.record_video()

    os.chdir("worlds")
    os.system(self.world)
    os.chdir("..")

  def assign_team(self, team_json, team):
    write_to_json(team_json, {"name" : team["name"], "robotStartCmd" : team["path"]})

  def generate_competition_title(self): return None

  def assign_all_teams(self): return None

  def record_video(self):
    write_to_json(game_json, {"record_simulation" : "C:/Elsiros/" + self.generate_competition_title() + ".mp4"})