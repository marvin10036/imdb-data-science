from metacritic_scrapper import get_metacritic_critic_scores_from_id
from pandas import read_csv
import json

from concurrent.futures import ThreadPoolExecutor, as_completed
from scores_processor import features_from_scores_map
from metacritic_scrapper import get_metacritic_critic_scores_from_id
import pandas as pd
from datetime import datetime


def fetch_one(imdb_id: str):
    # print(f"Procurando {imdb_id}")
    name, scores = get_metacritic_critic_scores_from_id(imdb_id)
    return imdb_id, name, scores


csv = read_csv("movies_catalog_oscar_and_popular_2000_2025.csv")
imdb_id_list = csv.get("ID IMDb").to_list()
scores_by_film = {}

# Ajuste o max_workers se o site for sensível a carga; 4–8 costuma ser seguro para scraping
max_workers = min(8, len(imdb_id_list))
now = datetime.now()
current_json = {}
error_count = 0
error_list = []

with ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = {executor.submit(fetch_one, imdb_id): imdb_id for imdb_id in imdb_id_list}
    for future in as_completed(futures):
        imdb_id = futures[future]
        try:
            imdb_id, name, scores = future.result()
            # print(f"{name}: {scores}")
            current_json[imdb_id] = scores
            if imdb_id:
                scores_by_film[imdb_id] = scores
            with open("movie_scores.json", "w") as file:
                file.write(json.dumps(current_json))
            print(f"Tamanho json: {len(current_json)}  número de erros: {error_count}")
        except Exception as e:
            print(f"Erro ao processar {imdb_id}: {e}")
            error_count += 1
            with open("error_list.json", "w") as file:
                error_list.append(imdb_id)
                file.write(json.dumps(error_list))
                print(f"Tamanho json: {len(current_json)}  número de erros: {error_count}")
