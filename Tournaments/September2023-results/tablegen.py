import json
import pandas as pd

name = input()

DESTINATION = 'Robofest_2023_sprint_universe9.xlsx'

with open(name + ".json") as f:
    results = json.load(f)


df = pd.DataFrame({
                "Дисциплина":   [result["discipline"] for result in results],
                "Команда #1":      [result["teams"][1]["name"] for result in results],
                "Команда #2":      [result["teams"][0]["name"] for result in results],
                "Счет": [result["results"][0] for result in results],
                })

df.to_excel(name + ".xlsx")


