from pymongo import MongoClient
import pandas as pd
from config import config as cfg


def load_data() -> list[pd.DataFrame]:
    schedules = []

    URL = "https://www.fit.vut.cz/study/field/14985/.cs"

    schedules = pd.read_html(URL, header=0)[:6]
    return schedules
