from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import csv
import json
import os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserData(BaseModel):
    phq9_score: int
    typing_text: str
    keystrokes: list
    features: dict

@app.post("/submit")
def submit(data: UserData):
    file_exists = os.path.isfile("data.csv")

    with open("data.csv", "a", newline="") as csvfile:
        writer = csv.writer(csvfile)

        if not file_exists:
            writer.writerow([
                "phq9_score",
                "typing_text",
                "keystrokes",
                "features"
            ])

        writer.writerow([
            data.phq9_score,
            data.typing_text,
            json.dumps(data.keystrokes),
            json.dumps(data.features)
        ])

    return {"status": "Data saved successfully"}
