from elsiros_interface import elsiros
import json

class Competition:
  def __init__(self, teams, world):
    self.world = world
    self.teams = teams

    #for team in self.teams:
    #  f = open(team["path"])
    #  f.close()

  def game_json(self):
    return f"controllers/Robofest_TEAM/game.json"

  def launch(self, postfix):
    for i in range(len(self.teams)):
      self.assign_team(i, self.teams[i])
    
    elsiros.assign_video_record(self.title() + "_" + postfix, self.game_json())
    return elsiros.launch(self.world)

  def get_teams_weights(self):
    weights = []
    print(self.teams)
    for i in range(len(self.teams)):
      team_weights = dict()
      team_weights["team"] = self.teams[i]["name"]
      with open(self.current_json(i)) as f:
        team_weights["data"] = json.load(f)
      weights.append(team_weights)
    return weights
          

  def title(self): return "UNDEFINED"