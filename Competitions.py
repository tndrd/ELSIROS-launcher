from base_competition import Competition, elsiros
from distutils.dir_util import copy_tree
import json

PENALTY_OLD_WORLD = "elsiros_game.wbt"
PENALTY_WORLD = "Robofest_2023_penalty.wbt"
SPRINT_WORLD  = "Robofest_2023_sprint.wbt"
MARATHON_WORLD = "Robofest_2023_marathon.wbt"

class Soccer(Competition):
  def __init__(self, teams):
    super().__init__(teams, PENALTY_OLD_WORLD)
    if len(teams) != 2:
      raise ValueError("Teams length must be 2")
  
  def assign_team(self, team_number, team):
    #print(team)

    DEFAULT_TEAM = f"{elsiros.base_path}controllers/SAMPLE_TEAM/"

    elsiros.write_to_json(self.current_json(team_number), {"name" : team["name"]})#, "robotStartCmd" : team["path"]})
    from_path = team["path"]
    to_path = f"{elsiros.base_path}controllers/TEAM_{team_number + 1}/"
    print(from_path, to_path)
    copy_tree(DEFAULT_TEAM, to_path)
    copy_tree(from_path, to_path)

  def current_json(self, team_number):
    return elsiros.base_path + f"controllers/referee/team_{team_number+1}.json"

  def game_json(self):
    return f"controllers/referee/game.json"

  def title(self):
    return f"Soccer_{self.teams[0]['name']}_{self.teams[1]['name']}"

  def check_finish(self, line):
    END_LINE = "Info: End of the game"
    if line[:len(END_LINE)] == END_LINE: 
      line = [linel.strip() for linel in line.split(",")]

      red_score  = int(line[1].split("=")[1])
      blue_score = int(line[2].split("=")[1])

      return True, f"{blue_score}:{red_score}" 
    return False, None

class Penalty(Competition):
  def __init__(self, teams):
    super().__init__(teams, PENALTY_WORLD)
    if len(teams) != 1:
      raise ValueError("Teams length must be 1")
    
  def assign_team(self, team_number, team):
    with open(team["path"]) as f:
      data = json.load(f)
      elsiros.write_to_json(self.current_json(team_number), data)

  def current_json(self, team_number):
    return elsiros.base_path + f"controllers/Robofest_TEAM/Init_params/strategy_data.json"

  def game_json(self):
    return f"controllers/referee_Robofest/game.json"

  def title(self):
    return f"Penalty_{self.teams[0]['name']}"

  def check_finish(self, line):
    END_LINE = "Info: End of the game"
    if line[:len(END_LINE)] == END_LINE: 
      line = [linel.strip() for linel in line.split(",")]

      red_score  = int(line[1].split("=")[1])
      blue_score = int(line[2].split("=")[1])

      return True, f"{blue_score}:{red_score}" 
    return False, None

class Sprint(Competition):
  def __init__(self, teams):
    super().__init__(teams, SPRINT_WORLD)
    if len(teams) != 1:
      raise ValueError("Teams length must be 1")
  
  def assign_team(self, team_number, team):
    with open(team["path"]) as f:
      data = json.load(f)
      elsiros.write_to_json(self.current_json(team_number), data)

  def current_json(self, team_number):
    return elsiros.base_path + f"controllers/Robofest_TEAM/Init_params/Sprint_params.json"

  def check_finish(self, line): 
    line = [linel.strip() for linel in line.split(":")]
    check  = False
    result = None
    if len(line) == 4:
      result = int(line[3])
      check = True 
    return check, result

  def title(self):
    return f"Sprint_{self.teams[0]['name']}"

class Marathon(Competition):
  def __init__(self, teams):
    super().__init__(teams, MARATHON_WORLD)
    if len(teams) != 1:
      raise ValueError("Teams length must be 1")
  
  def assign_team(self, team_number, team):
    with open(team["path"]) as f:
      data = json.load(f)
      elsiros.write_to_json(self.current_json(team_number), data)

  def check_finish(self, line): 
    line = [linel.strip() for linel in line.split(":")]
    check  = False
    result = None
    if len(line) == 4:
      result = int(line[3])
      check = True 
    return check, result

  def current_json(self, team_number):
    return elsiros.base_path + f"controllers/Robofest_TEAM/Init_params/Marathon_params.json"

  def title(self):
    return f"Marathon_{self.teams[0]['name']}"