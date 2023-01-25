from BaseCompetition import Competition

SOCCER_WORLD = "elsiros_game.wbt"
SOCCER_GAME_JSON = "controllers/referee/game.json"

TEAM_1_JSON = "controllers/referee/team_1.json"
TEAM_2_JSON = "controllers/referee/team_2.json"

class Penalty(Competition):
  def __init__(self, teams):
    super().__init__(teams, SOCCER_WORLD, SOCCER_GAME_JSON)

  def assign_all_teams(self):
    self.assign_team(TEAM_1_JSON, team[0])
    self.assign_team(TEAM_2_JSON, team[1])

  def generate_competition_title(self):
    return "C:/Elsiros/" + team[0]["name"] + team[1]["name"] + ".mp4"