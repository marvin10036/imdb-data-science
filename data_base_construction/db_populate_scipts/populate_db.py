import pandas as pd
import json
import re
import psycopg2
from psycopg2 import extras
from decimal import Decimal

# Função utilitária para converter strings monetárias em Decimal(18,2)
def parse_money(value: str) -> Decimal | None:
    if pd.isna(value) or value == "":
        return None
    # remover moeda (USD) e separadores de milhar
    clean = re.sub(r"[^0-9.]", "", value)
    try:
        return Decimal(clean)
    except:
        return None

# Conexão com o banco (ajustar host, dbname, usuário e senha conforme o ambiente)
conn = psycopg2.connect(
    host="localhost",
    dbname="moviesdb",
    user="postgres",
    password="postgres",
)

# Carregar CSV com pandas
df = pd.read_csv("data/raw/movies_catalog_oscar_and_popular_2000_2025.csv")

# Carregar JSON das amostras de nota
with open("data/processed/movie_scores.json", "r", encoding="utf-8") as f:
    rating_data = json.load(f)

# Carregar lista de IDs com erro que devem ser ignorados
with open("data/errors/error_list_from_error_list.json", "r", encoding="utf-8") as f:
    error_list = json.load(f)
    # Criar um set para lookup O(1)
    error_imdb_ids = set(error_list.keys())

# Criar cursores
cur = conn.cursor()

# Pré-carregar dicionários de domínios para evitar consultas repetidas
def load_lookup(table_name):
    cur.execute(f"SELECT id, name FROM {table_name}")
    return {name: id for id, name in cur.fetchall()}

genre_lookup = load_lookup("genres")
country_lookup = load_lookup("countries")
language_lookup = load_lookup("languages")
people_lookup = load_lookup("people")

# Função para obter ou inserir um domínio e retornar o id
def get_or_create(name, table, lookup):
    if name in lookup:
        return lookup[name]
    cur.execute(f"INSERT INTO {table} (name) VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING id", (name,))
    res = cur.fetchone()
    if res:
        lookup[name] = res[0]
        return res[0]
    # se houve conflito, fazer SELECT
    cur.execute(f"SELECT id FROM {table} WHERE name = %s", (name,))
    id_row = cur.fetchone()
    lookup[name] = id_row[0]
    return id_row[0]

# Converter linhas do CSV em estruturas para inserção
movie_rows = []
box_rows = []
genre_rows = []
country_rows = []
language_rows = []
people_rows = []

for idx, row in df.iterrows():
    imdb_id = row["ID IMDb"]
    
    # Validação: ignorar registros que estão na lista de erros
    if imdb_id in error_imdb_ids:
        print(f"Pulando filme com erro: {imdb_id} - {row['Título Original']}")
        continue
    
    # Filme
    movie_rows.append((
        imdb_id,
        row["Título Original"],
        row["Título Brasileiro"] if not pd.isna(row["Título Brasileiro"]) else None,
        int(row["Ano Lançamento"]),
        float(row["Nota IMDb"]) if not pd.isna(row["Nota IMDb"]) else None,
        int(row["Votos"]) if not pd.isna(row["Votos"]) else None,
        int(row["Duração (min)"]) if not pd.isna(row["Duração (min)"]) else None,
        True if str(row["Indicado Oscar"]).strip().lower() == "sim" else False,
        True if str(row["Vencedor Oscar"]).strip().lower() == "sim" else False,
        int(row["Ano Cerimônia Oscar"]) if not pd.isna(row["Ano Cerimônia Oscar"]) else None,
        row["Status Oscar"] if not pd.isna(row["Status Oscar"]) else None,
        int(row["Metascore"]) if not pd.isna(row["Metascore"]) else None,
        row["Sinopse"]
    ))

    # Box office
    box_rows.append((
        imdb_id,
        parse_money(row["Orçamento"]),
        parse_money(row["Bilheteria Mundial"]),
        parse_money(row["Bilheteria Doméstica"])
    ))

    # Gêneros
    for genre in str(row["Gêneros"]).split(","):
        g = genre.strip()
        if g:
            gid = get_or_create(g, "genres", genre_lookup)
            genre_rows.append((imdb_id, gid))

    # Países
    for country in str(row["Países"]).split(","):
        c = country.strip()
        if c:
            cid = get_or_create(c, "countries", country_lookup)
            country_rows.append((imdb_id, cid))

    # Idiomas
    for lang in str(row["Idiomas"]).split(","):
        l = lang.strip()
        if l:
            lid = get_or_create(l, "languages", language_lookup)
            language_rows.append((imdb_id, lid))

    # Pessoas – diretores, roteiristas e elenco
    for person in str(row["Diretores"]).split(","):
        p = person.strip()
        if p:
            pid = get_or_create(p, "people", people_lookup)
            people_rows.append((imdb_id, pid, 'director', None))
    for person in str(row["Roteiristas"]).split(","):
        p = person.strip()
        if p:
            pid = get_or_create(p, "people", people_lookup)
            people_rows.append((imdb_id, pid, 'writer', None))
    # Elenco principal com ordem
    cast_list = [p.strip() for p in str(row["Elenco Principal"]).split(",") if p.strip()]
    for order, actor in enumerate(cast_list, start=1):
        pid = get_or_create(actor, "people", people_lookup)
        people_rows.append((imdb_id, pid, 'cast', order))

# Inserir dados em lote usando execute_values para melhor performance:contentReference[oaicite:2]{index=2}.
# Inserir filmes
extras.execute_values(cur,
    "INSERT INTO movies (imdb_id, original_title, br_title, release_year, imdb_rating, imdb_votes, runtime_minutes, "
    "nominated_oscar, won_oscar, oscar_ceremony_year, oscar_status, metascore, synopsis) "
    "VALUES %s ON CONFLICT (imdb_id) DO NOTHING",
    movie_rows
)

# Inserir box office
extras.execute_values(cur,
    "INSERT INTO movie_box_office (movie_id, budget, worldwide_gross, domestic_gross) VALUES %s "
    "ON CONFLICT (movie_id) DO NOTHING",
    box_rows
)

# Inserir relações N:N
extras.execute_values(cur,
    "INSERT INTO movie_genres (movie_id, genre_id) VALUES %s ON CONFLICT DO NOTHING",
    genre_rows
)
extras.execute_values(cur,
    "INSERT INTO movie_countries (movie_id, country_id) VALUES %s ON CONFLICT DO NOTHING",
    country_rows
)
extras.execute_values(cur,
    "INSERT INTO movie_languages (movie_id, language_id) VALUES %s ON CONFLICT DO NOTHING",
    language_rows
)
extras.execute_values(cur,
    "INSERT INTO movie_people (movie_id, person_id, role, cast_order) VALUES %s ON CONFLICT DO NOTHING",
    people_rows
)

# Inserir amostras de notas do JSON
rating_rows = []
for imdb_id, samples in rating_data.items():
    for idx, score in enumerate(samples, start=1):
        rating_rows.append((imdb_id, int(score), idx))

extras.execute_values(cur,
    "INSERT INTO rating_samples (movie_id, score_value, sample_index) VALUES %s "
    "ON CONFLICT (movie_id, sample_index) DO NOTHING",
    rating_rows
)

conn.commit()
cur.close()
conn.close()
print("ETL concluído com sucesso!")
