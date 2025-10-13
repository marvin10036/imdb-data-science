from scores_processor import features_from_scores_map
from metacritic_scrapper import get_metacritic_critic_scores_from_id
import pandas as pd

if __name__ == "__main__":
    # Exemplo (substitua pelo seu dicionário real):
    scores_by_film = {}
    for id in ["tt7130300","tt0111161", "tt0068646", "tt0468569", "tt0071562"]:
        print(f"Procurando {id}")
        name, scores = get_metacritic_critic_scores_from_id(id)
        print(f"{name}: {scores}")
        scores_by_film[name] = scores

    df_features = features_from_scores_map(scores_by_film)
    # Visualização rápida
    pd.set_option("display.max_columns", None)
    print(df_features.round(3))