from competitions_launcher import TournamentLauncher
import json
import sys

if __name__ == "__main__":
  
  tournament_path = "Robofest_2023/marathon_relaunch.json"
  teams_path = "Робофест_Решения/"
  
  launcher = TournamentLauncher(tournament_path, teams_path)
  results = launcher.launch()
  
  with open("results.json", "w") as f:
    json.dump(results, f, indent=4)