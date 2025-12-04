-- Criar tipos enumerados para função de pessoas
CREATE TYPE movie_role AS ENUM ('director', 'writer', 'cast');

-- Tabela principal de filmes
CREATE TABLE movies (
    imdb_id            VARCHAR(15) PRIMARY KEY,
    original_title     TEXT NOT NULL,
    br_title           TEXT,
    release_year       INT NOT NULL,
    imdb_rating        DECIMAL(3,1) CHECK (imdb_rating BETWEEN 0 AND 10),
    imdb_votes         INT CHECK (imdb_votes >= 0),
    runtime_minutes    INT CHECK (runtime_minutes > 0),
    nominated_oscar    BOOLEAN NOT NULL,
    won_oscar          BOOLEAN NOT NULL,
    oscar_ceremony_year INT,
    oscar_status       TEXT,
    metascore          INT CHECK (metascore BETWEEN 0 AND 100),
    synopsis           TEXT
);

COMMENT ON TABLE movies IS 'Tabela central de filmes, identificada pelo IMDb ID (chave natural).';

-- Tabela de orçamento e bilheteria (1:1 com movies)
CREATE TABLE movie_box_office (
    movie_id          VARCHAR(15) PRIMARY KEY REFERENCES movies (imdb_id) ON DELETE CASCADE,
    budget            NUMERIC(18,2),
    worldwide_gross   NUMERIC(18,2),
    domestic_gross    NUMERIC(18,2)

);
COMMENT ON TABLE movie_box_office IS 'Armazena valores monetários (USD) de cada filme.';

-- Gêneros
CREATE TABLE genres (
    id      SERIAL PRIMARY KEY,
    name    TEXT NOT NULL UNIQUE
);

-- Associação filme ↔ gênero (N:N)
CREATE TABLE movie_genres (
    movie_id   VARCHAR(15) NOT NULL REFERENCES movies (imdb_id) ON DELETE CASCADE,
    genre_id   INT NOT NULL REFERENCES genres (id) ON DELETE CASCADE,
    PRIMARY KEY (movie_id, genre_id)
);

-- Pessoas (diretores, roteiristas, elenco)
CREATE TABLE people (
    id      SERIAL PRIMARY KEY,
    name    TEXT NOT NULL UNIQUE
);

-- Associação filme ↔ pessoa com papel específico
CREATE TABLE movie_people (
    movie_id   VARCHAR(15) NOT NULL REFERENCES movies (imdb_id) ON DELETE CASCADE,
    person_id  INT NOT NULL REFERENCES people (id) ON DELETE CASCADE,
    role       movie_role NOT NULL,
    cast_order INT,
    PRIMARY KEY (movie_id, person_id, role)
);

-- Países
CREATE TABLE countries (
    id      SERIAL PRIMARY KEY,
    name    TEXT NOT NULL UNIQUE
);

-- Associação filme ↔ país
CREATE TABLE movie_countries (
    movie_id   VARCHAR(15) NOT NULL REFERENCES movies (imdb_id) ON DELETE CASCADE,
    country_id INT NOT NULL REFERENCES countries (id) ON DELETE CASCADE,
    PRIMARY KEY (movie_id, country_id)
);

-- Idiomas
CREATE TABLE languages (
    id      SERIAL PRIMARY KEY,
    name    TEXT NOT NULL UNIQUE
);

-- Associação filme ↔ idioma
CREATE TABLE movie_languages (
    movie_id    VARCHAR(15) NOT NULL REFERENCES movies (imdb_id) ON DELETE CASCADE,
    language_id INT NOT NULL REFERENCES languages (id) ON DELETE CASCADE,
    PRIMARY KEY (movie_id, language_id)
);

-- Amostras de notas do JSON
CREATE TABLE rating_samples (
    id           SERIAL PRIMARY KEY,
    movie_id     VARCHAR(15) NOT NULL REFERENCES movies (imdb_id) ON DELETE CASCADE,
    score_value  SMALLINT NOT NULL CHECK (score_value BETWEEN 0 AND 100),
    sample_index INT NOT NULL,
    UNIQUE (movie_id, sample_index)
);

-- Estatísticas agregadas das amostras de nota (pré-calculadas para ML)
CREATE TABLE rating_sample_features (
    movie_id              VARCHAR(15) PRIMARY KEY REFERENCES movies (imdb_id) ON DELETE CASCADE,
    sample_count          INT NOT NULL CHECK (sample_count >= 0),
    mean_score            NUMERIC(10,4),
    median_score          NUMERIC(10,4),
    mode_score            SMALLINT,
    mode_frequency        INT,
    variance_score        NUMERIC(12,6),
    stddev_score          NUMERIC(12,6),
    geometric_mean_score  NUMERIC(12,6),
    harmonic_mean_score   NUMERIC(12,6),
    min_score             SMALLINT,
    max_score             SMALLINT,
    p10_score             NUMERIC(10,4),
    p25_score             NUMERIC(10,4),
    p75_score             NUMERIC(10,4),
    p90_score             NUMERIC(10,4),
    iqr_score             NUMERIC(10,4),
    range_score           NUMERIC(10,4),
    unique_scores         INT,
    created_at            TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);
COMMENT ON TABLE rating_sample_features IS 'Estatísticas agregadas das amostras de notas por filme (média, mediana, moda, variância, quantis, etc.)';

-- Índices auxiliares para performance
CREATE INDEX idx_movie_people_person ON movie_people (person_id);
CREATE INDEX idx_movie_genres_genre ON movie_genres (genre_id);
CREATE INDEX idx_movie_countries_country ON movie_countries (country_id);
CREATE INDEX idx_movie_languages_language ON movie_languages (language_id);
CREATE INDEX idx_rating_samples_movie ON rating_samples (movie_id);

-- View de estatísticas das amostras
CREATE OR REPLACE VIEW movie_rating_stats AS
SELECT
    m.imdb_id AS movie_id,
    COUNT(rs.score_value)                         AS n_samples,
    AVG(rs.score_value)                           AS mean_score,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY rs.score_value) AS median_score,
    STDDEV_POP(rs.score_value)                   AS stddev_score,
    percentile_cont(0.9) WITHIN GROUP (ORDER BY rs.score_value) AS p90_score,
    MIN(rs.score_value)                           AS min_score,
    MAX(rs.score_value)                           AS max_score
FROM movies m
LEFT JOIN rating_samples rs ON m.imdb_id = rs.movie_id
GROUP BY m.imdb_id;

COMMENT ON VIEW movie_rating_stats IS 'Estatísticas das amostras de notas: média, mediana, desvio‑padrão populacional, percentil 90, mínimo, máximo e número de amostras.';

-- View para geração de dataset de treinamento de ML
-- Concatena features numéricas, contagens de atributos categóricos e features derivadas
CREATE OR REPLACE VIEW ml_training_dataset AS
SELECT
    m.imdb_id,
    m.original_title,
    m.release_year,
    m.imdb_rating,
    m.imdb_votes,
    m.runtime_minutes,
    m.metascore,

    -- Feature derivada: Box Office Rank in Year (posição relativa de bilheteria no ano)
    RANK() OVER (PARTITION BY m.release_year ORDER BY mbo.worldwide_gross DESC NULLS LAST) AS box_office_rank_in_year,
    
    -- Feature derivada: Votes Normalized by Year (z-score de imdb_votes por ano)
    (CASE 
        WHEN STDDEV(m.imdb_votes) OVER (PARTITION BY m.release_year) > 0 
        THEN (m.imdb_votes - AVG(m.imdb_votes) OVER (PARTITION BY m.release_year)) 
             / STDDEV(m.imdb_votes) OVER (PARTITION BY m.release_year)
        ELSE NULL 
    END) AS votes_normalized_by_year,
    
    -- Feature derivada: Rating Normalized by Year (z-score de imdb_rating por ano)
    (CASE 
        WHEN STDDEV(m.imdb_rating) OVER (PARTITION BY m.release_year) > 0 
        THEN (m.imdb_rating - AVG(m.imdb_rating) OVER (PARTITION BY m.release_year)) 
             / STDDEV(m.imdb_rating) OVER (PARTITION BY m.release_year)
        ELSE NULL 
    END) AS rating_normalized_by_year,
    
    -- Estatísticas de rating samples (Metacritic) - Nulos viram 0
    COALESCE(rf.sample_count, rs.n_samples, 0)          AS n_samples,
    COALESCE(rf.mean_score, rs.mean_score, 0)            AS mean_score,
    COALESCE(rf.median_score, rs.median_score, 0)        AS median_score,
    COALESCE(rf.mode_score, 0)            AS mode_score,
    COALESCE(rf.mode_frequency, 0)        AS mode_frequency,
    COALESCE(rf.variance_score, 0)        AS variance_score,
    COALESCE(rf.stddev_score, rs.stddev_score, 0)        AS stddev_score,
    COALESCE(rf.geometric_mean_score, 0)  AS geometric_mean_score,
    COALESCE(rf.harmonic_mean_score, 0)   AS harmonic_mean_score,
    COALESCE(rf.p10_score, 0)             AS p10_score,
    COALESCE(rf.p25_score, 0)             AS p25_score,
    COALESCE(rf.p75_score, 0)             AS p75_score,
    COALESCE(rf.p90_score, rs.p90_score, 0)             AS p90_score,
    COALESCE(rf.iqr_score, 0)             AS iqr_score,
    COALESCE(rf.range_score, 0)           AS range_score,
    COALESCE(rf.min_score, rs.min_score, 0)             AS min_score,
    COALESCE(rf.max_score, rs.max_score, 0)             AS max_score,
    COALESCE(rf.unique_scores, 0)         AS unique_scores,
    
    -- Contagens de atributos categóricos
    (SELECT COUNT(*) FROM movie_genres     mg WHERE mg.movie_id = m.imdb_id) AS num_genres,
    (SELECT COUNT(*) FROM movie_countries  mc WHERE mc.movie_id = m.imdb_id) AS num_countries,
    (SELECT COUNT(*) FROM movie_languages  ml WHERE ml.movie_id = m.imdb_id) AS num_languages,
    (SELECT COUNT(*) FROM movie_people     mp WHERE mp.movie_id = m.imdb_id AND mp.role = 'director') AS num_directors,
    (SELECT COUNT(*) FROM movie_people     mp WHERE mp.movie_id = m.imdb_id AND mp.role = 'writer')   AS num_writers,
    (SELECT COUNT(*) FROM movie_people     mp WHERE mp.movie_id = m.imdb_id AND mp.role = 'cast')    AS num_cast,
    
    -- Feature 1: Pedigree (Diretor) - Quantos filmes anteriores indicados o diretor tem
    (
        SELECT COUNT(DISTINCT m2.imdb_id)
        FROM movie_people mp1
        JOIN movie_people mp2 ON mp1.person_id = mp2.person_id
        JOIN movies m2 ON mp2.movie_id = m2.imdb_id
        WHERE mp1.movie_id = m.imdb_id
          AND mp1.role = 'director'
          AND m2.release_year < m.release_year
          AND m2.nominated_oscar = TRUE
    ) AS director_prev_nominations,

    -- Feature 1: Pedigree (Elenco) - Quantos filmes anteriores indicados o elenco tem
    (
        SELECT COUNT(DISTINCT m2.imdb_id)
        FROM movie_people mp1
        JOIN movie_people mp2 ON mp1.person_id = mp2.person_id
        JOIN movies m2 ON mp2.movie_id = m2.imdb_id
        WHERE mp1.movie_id = m.imdb_id
          AND mp1.role = 'cast'
          AND m2.release_year < m.release_year
          AND m2.nominated_oscar = TRUE
    ) AS cast_prev_nominations,

    -- Feature 2: Buzz (Gêneros Oscar-Bait)
    (CASE WHEN EXISTS (SELECT 1 FROM movie_genres mg JOIN genres g ON mg.genre_id = g.id WHERE mg.movie_id = m.imdb_id AND g.name = 'Drama') THEN 1 ELSE 0 END) AS is_drama,
    (CASE WHEN EXISTS (SELECT 1 FROM movie_genres mg JOIN genres g ON mg.genre_id = g.id WHERE mg.movie_id = m.imdb_id AND g.name = 'Biography') THEN 1 ELSE 0 END) AS is_biography,
    (CASE WHEN EXISTS (SELECT 1 FROM movie_genres mg JOIN genres g ON mg.genre_id = g.id WHERE mg.movie_id = m.imdb_id AND g.name = 'History') THEN 1 ELSE 0 END) AS is_history,
    
    -- Rótulo (label) para ML
    m.nominated_oscar::INT AS label -- rótulo binário (1=indicado, 0=não indicado)
FROM movies m
LEFT JOIN movie_box_office mbo ON m.imdb_id = mbo.movie_id
LEFT JOIN rating_sample_features rf ON m.imdb_id = rf.movie_id
LEFT JOIN movie_rating_stats rs ON m.imdb_id = rs.movie_id;

COMMENT ON VIEW ml_training_dataset IS 'Dataset para treinamento de modelo de classificação de indicação ao Oscar. Inclui features numéricas, features derivadas (ROI, market share, z-scores, rank), estatísticas de ratings (incluindo moda, variância e quantis), contagens de categorias e o rótulo binário.';

-- ==============================================================================
-- VIEWS DE SPLIT TEMPORAL (CRÍTICO PARA EVITAR DATA LEAKAGE)
-- ==============================================================================

-- 1. Conjunto de Treino (2000-2019) - 20 anos
-- Usado para treinar os modelos
CREATE OR REPLACE VIEW ml_split_train AS
SELECT * FROM ml_training_dataset
WHERE release_year BETWEEN 2000 AND 2019;

COMMENT ON VIEW ml_split_train IS 'Conjunto de Treino (2000-2019). Usado para treinar os modelos.';

-- 2. Conjunto de Validação (2020-2022) - 3 anos
-- Usado para tunar hiperparâmetros e avaliar métricas durante desenvolvimento
CREATE OR REPLACE VIEW ml_split_validation AS
SELECT * FROM ml_training_dataset
WHERE release_year BETWEEN 2020 AND 2022;

COMMENT ON VIEW ml_split_validation IS 'Conjunto de Validação (2020-2022). Usado para tuning e avaliação preliminar.';

-- 3. Conjunto de Teste (2023-2024) - 2 anos
-- Usado APENAS para avaliação final do modelo escolhido
CREATE OR REPLACE VIEW ml_split_test AS
SELECT * FROM ml_training_dataset
WHERE release_year BETWEEN 2023 AND 2024;

COMMENT ON VIEW ml_split_test IS 'Conjunto de Teste (2023-2024). Usado apenas para avaliação final (holdout).';

-- 4. Conjunto de Predição (2025) - Futuro
-- Dados onde aplicaremos o modelo para gerar as predições do Oscar 2025
CREATE OR REPLACE VIEW ml_split_prediction_2025 AS
SELECT * FROM ml_training_dataset
WHERE release_year = 2025;

COMMENT ON VIEW ml_split_prediction_2025 IS 'Conjunto de Predição (2025). Filmes alvo para predição do Oscar.';
