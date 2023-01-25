from elsiros_interface import elsiros

class Competition:
  def __init__(self, teams, world):
    self.world = world
    self.teams = teams 

  def launch(self):
    for i in range(len(self.teams)):
      self.assign_team(i + 1, self.teams[i])
    
    elsiros.assign_video_record(self.title())
    return elsiros.launch(self.world)

  def title(self): return "UNDEFINED"