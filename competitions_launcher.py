import json
import competitions
import socket
from time import sleep

COMPETITION_NAMES = { "Penalty": competitions.Penalty,
                      "PenaltyOld": competitions.PenaltyOld,
                      "Sprint":  competitions.Sprint,
                      "Marathon":  competitions.Marathon }

class TournamentLauncher:
  def __init__(self, description_path, teams_path):
    self.games = []
    self.teams = []
    self.team_IDs = dict()
    self.description_path = description_path
    self.teams_path = teams_path
    self.repeats = None
    self.compt_t = None
    self._load()


  def _bind_socket(self):
      sock = socket.socket()
      #sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      sock.bind(('', 2323))
    
      sock.listen(1)
      print("Connecting to logger...")  
      conn, addr = sock.accept()
      print("Connected")
      return conn

  def _readloop(self, conn, competition):
      log = ""
      print("Waiting for game to finish...")
      while True:
        try:
          data = conn.recv(1).decode("utf-8")
        except Exception: continue

        if data == "\n":
          res, finish_data = competition.check_finish(log)
          if res:
            print(f"Finished with {finish_data}")
            return finish_data
          
          log = ""
        else:
          log = log + data
        if not data:
            break

  def _get_team(self, name):
    return self.teams[self.team_IDs[name]]

  def _load_teams(self):
    with open(self.description_path) as f:
      description = json.load(f)
      self.teams = description["teams"]
      
      for i in range(len(self.teams)):
        team = self.teams[i]
        team["path"] = self.teams_path + team["path"]
        self.team_IDs[team["name"]] = i
    
  def _load_games(self):
    with open(self.description_path) as f:
      description = json.load(f)
      self.compt_t = self._competition_type(description["competition"])
      self.repeats = int(description["repeats"])
      for game_description in description["games"]:
        teams = [self._get_team(team_name) for team_name in game_description]
        self.games.append(self.compt_t(teams))

  def _load(self):
    self._load_teams()
    self._load_games()
      
  def launch(self):
    for game in self.games:
      print("------------------------------")
      print(f"Launching teams: {game.teams} ({self.repeats} times)")
      for i in range(self.repeats):

        proc = game.launch()
        conn = self._bind_socket()
        
        self._readloop(conn, game)
        print("Terminating ELSIROS")
        proc.terminate()
        conn.close()
        print("------------------------------")
        sleep(2)

  def _competition_type(self, name):
    return COMPETITION_NAMES[name]

if __name__ == "__main__":
  tournament = "tournament.json" #input()
  test_tournament = "test_tournament.json" #input()
  marathon = "marathon.json"
  penalty = "penalty.json"
  sprint = "sprint.json"

  teams_path = "teams/"
  launcher = TournamentLauncher(marathon, teams_path)
  launcher.launch()