from metacritic_scrapper import get_metacritic_critic_scores_from_id
from pandas import read_csv
import json

from urllib3.exceptions import ConnectTimeoutError

from concurrent.futures import ThreadPoolExecutor, as_completed
from scores_processor import features_from_scores_map
from metacritic_scrapper import get_metacritic_critic_scores_from_id
import pandas as pd
from datetime import datetime


def fetch_one(imdb_id: str):
    # print(f"Procurando {imdb_id}")
    name, scores = get_metacritic_critic_scores_from_id(imdb_id)
    return imdb_id, name, scores



def get_all_movies_scores():
# Ajuste o max_workers se o site for sensível a carga; 4–8 costuma ser seguro para scraping
    csv = read_csv("movies_catalog_oscar_and_popular_2000_2025.csv")
    imdb_id_list = csv.get("ID IMDb").to_list()
    scores_by_film = {}

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


def get_movies_scores_that_return_an_error():
    with open("error_list_from_error_list.json", "rb") as file:
        erro_list_json: list = json.loads(file.read())

    scores_by_film = {}

    max_workers = min(8, len(erro_list_json))
    current_json = {}
    error_count = 0
    error_list = []

    while len(erro_list_json) > 0:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(fetch_one, imdb_id): imdb_id for imdb_id in erro_list_json}
            for future in as_completed(futures):
                imdb_id = futures[future]
                try:
                    imdb_id, name, scores = future.result()
                    # print(f"{name}: {scores}")
                    current_json[imdb_id] = scores
                    if imdb_id:
                        scores_by_film[imdb_id] = scores
                    with open("movie_scores_from_error_list.json", "w") as file:
                        file.write(json.dumps(current_json))
                    print(f"Tamanho json: {len(current_json)}  número de erros: {error_count}")
                    erro_list_json.remove(imdb_id)
                except ConnectTimeoutError as e:
                    print(f"Erro de conexão ao processar {imdb_id}: {e}")
                except Exception as e:
                    print(f"Erro ao processar {imdb_id}: {e}")
                    error_count += 1
                    with open("error_list_from_error_list.json", "w") as file:
                        error_list.append(imdb_id)
                        file.write(json.dumps(error_list))
                        print(f"Tamanho json: {len(current_json)}  número de erros: {error_count}")
                        erro_list_json.remove(imdb_id)

get_movies_scores_that_return_an_error()