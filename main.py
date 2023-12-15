from competitions_launcher import TournamentLauncher
import json
import sys

if __name__ == "__main__":
  
  tournament_path = "September2023-tournament/final.json"
  teams_path = "September2023-teams/"
  #teams_path = ""

  launcher = TournamentLauncher(tournament_path, teams_path)
  results = launcher.launch()
  
  with open("final.json", "w") as f:
    json.dump(results, f, indent=4)