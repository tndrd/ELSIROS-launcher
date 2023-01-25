import json
import os
from multiprocessing import Process
ELSIROS_PATH = "C:/Elsiros/"

class ElsirosInterface:
    def __init__(self, base_path):
        self.base_path = base_path
    
    def write_to_json(self, filename, elements):
        with open(filename) as file:
            data = json.load(file)

        for k, v in elements.items():
            data[k] = v

        with open(filename, 'w') as outfile:
            json.dump(data, outfile, indent=4)

    def game_json(self):
        return self.base_path + f"controllers/referee_Robofest/game.json"

    def assign_video_record(self, title):
        path = self.base_path + "videos/" + title + ".mp4"
        print(path)
        self.write_to_json(self.game_json(), {"record_simulation" : self.base_path + "videos/" + title + ".mp4"})

    def launch(self, world):
        proc = Process(target=os.system, args=(self.base_path + "worlds/" + world,))
        proc.start()
        return proc

elsiros = ElsirosInterface(ELSIROS_PATH)