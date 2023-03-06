import json
import pandas as pd

DESTINATION = 'Robofest_2023_sprint_universe9.xlsx'

with open("results.json") as f:
    results = json.load(f)


df = pd.DataFrame({
                "Дисциплина":   [result["discipline"] for result in results],
                "Команда":      [result["teams"][0]["name"] for result in results],
                "Результат #1": [result["results"][0] for result in results],
                "Результат #2": [result["results"][1] for result in results],
                "Результат #3": [result["results"][2] for result in results]
                })

df.to_excel(DESTINATION)


