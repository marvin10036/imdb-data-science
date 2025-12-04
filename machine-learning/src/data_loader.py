"""
Utility functions for database connection and data loading.
"""

import os
from sqlalchemy import create_engine, text
import pandas as pd
from dotenv import load_dotenv
from typing import Optional, List
import warnings

# Load environment variables
load_dotenv()


def get_db_connection():
    """
    Create and return a SQLAlchemy database engine.
    
    Returns:
        sqlalchemy.engine.Engine: Database engine
        
    Raises:
        ValueError: If database credentials are not found in .env
    """
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'moviesdb')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'postgres')
    if not db_user or not db_password:
        raise ValueError(
            "Database credentials not found. "
            "Please set DB_USER and DB_PASSWORD in .env file"
        )
    
    connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(connection_string, pool_pre_ping=True)
    
    return engine


def test_connection():
    """
    Test database connection and print basic info.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        engine = get_db_connection()
        with engine.connect() as conn:
            # Get PostgreSQL version
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print("✅ Database connection successful!")
            print(f"PostgreSQL version: {version[:50]}...")
            
            # Count movies
            result = conn.execute(text("SELECT COUNT(*) FROM movies;"))
            movie_count = result.fetchone()[0]
            print(f"Total movies in database: {movie_count:,}")
            
            # Count nominated
            result = conn.execute(text("SELECT COUNT(*) FROM movies WHERE nominated_oscar = TRUE;"))
            nominated_count = result.fetchone()[0]
            print(f"Oscar nominated movies: {nominated_count}")
            
            # Count by year range
            result = conn.execute(text("SELECT MIN(release_year), MAX(release_year) FROM movies;"))
            min_year, max_year = result.fetchone()
            print(f"Year range: {min_year} - {max_year}")
            
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def load_ml_dataset(cache_csv: bool = False, show_columns: bool = False, sample_rows: int | None = None):
    """
    Load the ml_training_dataset view directly from database.
    
    Args:
        cache_csv: If True, saves a cached CSV copy (default: False)
        show_columns: If True, prints the column list for quick inspection
        sample_rows: If set, prints the first N rows as a table (use small N to avoid flooding output)
    
    Returns:
        pandas.DataFrame: ML training dataset with all features
    """
    print("📊 Loading ML dataset from database...")
    engine = get_db_connection()
    query = "SELECT * FROM ml_training_dataset ORDER BY release_year, imdb_id;"
    df = pd.read_sql(query, engine)
    
    print(f"✅ Loaded {len(df):,} movies from database")
    print(f"   Features: {len(df.columns)}")
    print(f"   Period: {df['release_year'].min()} - {df['release_year'].max()}")
    
    if show_columns:
        print("   Column list:")
        for idx, col in enumerate(df.columns, start=1):
            print(f"     {idx:02d}. {col}")
    
    if sample_rows:
        n = max(1, sample_rows)
        print(f"\n🔎 Preview (first {n} rows):")
        print(df.head(n).to_string(index=False))
    
    # Optional: cache to CSV for faster subsequent loads
    if cache_csv:
        cache_path = 'data/processed/ml_dataset_cache.csv'
        os.makedirs('data/processed', exist_ok=True)
        df.to_csv(cache_path, index=False)
        print(f"💾 Cached to {cache_path}")
    
    return df


def load_genres_data():
    """
    Load genres and movie-genre relationships from database.
    
    Returns:
        tuple: (genres_df, movie_genres_df)
    """
    print("🎬 Loading genres data from database...")
    engine = get_db_connection()
    
    # Load genres
    genres_df = pd.read_sql("SELECT * FROM genres ORDER BY name;", engine)
    
    # Load movie-genre relationships
    query = """
        SELECT mg.movie_id, g.name as genre_name, g.id as genre_id
        FROM movie_genres mg
        JOIN genres g ON mg.genre_id = g.id
        ORDER BY mg.movie_id, g.name;
    """
    movie_genres_df = pd.read_sql(query, engine)
    
    print(f"✅ Loaded {len(genres_df)} genres, {len(movie_genres_df):,} relationships")
    return genres_df, movie_genres_df


def load_people_data():
    """
    Load people (directors, writers, cast) and relationships from database.
    
    Returns:
        tuple: (people_df, movie_people_df)
    """
    print("👥 Loading people data from database...")
    engine = get_db_connection()
    
    # Load people
    people_df = pd.read_sql("SELECT * FROM people ORDER BY name;", engine)
    
    # Load movie-people relationships
    query = """
        SELECT 
            mp.movie_id, 
            p.name as person_name,
            p.id as person_id,
            mp.role, 
            mp.cast_order
        FROM movie_people mp
        JOIN people p ON mp.person_id = p.id
        ORDER BY mp.movie_id, mp.role, mp.cast_order;
    """
    movie_people_df = pd.read_sql(query, engine)
    
    print(f"✅ Loaded {len(people_df):,} people, {len(movie_people_df):,} relationships")
    print(f"   Directors: {len(movie_people_df[movie_people_df['role'] == 'director']):,}")
    print(f"   Writers: {len(movie_people_df[movie_people_df['role'] == 'writer']):,}")
    print(f"   Cast: {len(movie_people_df[movie_people_df['role'] == 'cast']):,}")
    
    return people_df, movie_people_df


def load_countries_data():
    """
    Load countries and movie-country relationships from database.
    
    Returns:
        tuple: (countries_df, movie_countries_df)
    """
    print("🌍 Loading countries data from database...")
    engine = get_db_connection()
    
    countries_df = pd.read_sql("SELECT * FROM countries ORDER BY name;", engine)
    
    query = """
        SELECT mc.movie_id, c.name as country_name, c.id as country_id
        FROM movie_countries mc
        JOIN countries c ON mc.country_id = c.id
        ORDER BY mc.movie_id, c.name;
    """
    movie_countries_df = pd.read_sql(query, engine)
    
    print(f"✅ Loaded {len(countries_df)} countries, {len(movie_countries_df):,} relationships")
    return countries_df, movie_countries_df


def load_languages_data():
    """
    Load languages and movie-language relationships from database.
    
    Returns:
        tuple: (languages_df, movie_languages_df)
    """
    print("🗣️ Loading languages data from database...")
    engine = get_db_connection()
    
    languages_df = pd.read_sql("SELECT * FROM languages ORDER BY name;", engine)
    
    query = """
        SELECT ml.movie_id, l.name as language_name, l.id as language_id
        FROM movie_languages ml
        JOIN languages l ON ml.language_id = l.id
        ORDER BY ml.movie_id, l.name;
    """
    movie_languages_df = pd.read_sql(query, engine)
    
    print(f"✅ Loaded {len(languages_df)} languages, {len(movie_languages_df):,} relationships")
    return languages_df, movie_languages_df


def run_custom_query(query: str, params: Optional[dict] = None):
    """
    Execute a custom SQL query and return results as DataFrame.
    
    Args:
        query: SQL query string
        params: Optional dictionary of query parameters
        
    Returns:
        pandas.DataFrame: Query results
    """
    engine = get_db_connection()
    df = pd.read_sql(query, engine, params=params)
    print(f"✅ Query returned {len(df):,} rows")
    print(df)
    return df


def export_to_csv(df, filename, directory='data/processed'):
    """
    Export DataFrame to CSV file (use sparingly, prefer database queries).
    
    Args:
        df: pandas DataFrame to export
        filename: Name of the CSV file
        directory: Directory to save the file (default: data/processed)
        
    Note:
        This should only be used for final processed datasets ready for model training.
        For data exploration, use direct database queries instead.
    """
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, filename)
    df.to_csv(filepath, index=False)
    print(f"💾 Exported to {filepath}")
    
    # Warn if exporting to data/raw (should use database instead)
    if directory == 'data/raw':
        warnings.warn(
            "Exporting to data/raw is discouraged. "
            "Consider using direct database queries instead.",
            UserWarning
        )


def load_all_data():
    """
    Convenience function to load all data at once.
    
    Returns:
        dict: Dictionary with all DataFrames
    """
    print("\n" + "="*60)
    print("LOADING ALL DATA FROM DATABASE")
    print("="*60 + "\n")
    
    data = {
        'ml_dataset': load_ml_dataset(),
        'genres': load_genres_data()[0],
        'movie_genres': load_genres_data()[1],
        'people': load_people_data()[0],
        'movie_people': load_people_data()[1],
        'countries': load_countries_data()[0],
        'movie_countries': load_countries_data()[1],
        'languages': load_languages_data()[0],
        'movie_languages': load_languages_data()[1],
    }
    
    print("\n" + "="*60)
    print("✅ ALL DATA LOADED SUCCESSFULLY")
    print("="*60 + "\n")
    
    return data


if __name__ == "__main__":
    # Test connection when script is run directly
    print("Testing database connection...")
    test_connection()
    
    print("\n" + "="*60)
    print("Available functions:")
    print("="*60)
    print("• load_ml_dataset() - Main ML dataset")
    print("• load_genres_data() - Genres and relationships")
    print("• load_people_data() - People and relationships")
    print("• load_countries_data() - Countries and relationships")
    print("• load_languages_data() - Languages and relationships")
    print("• run_custom_query(query) - Run any SQL query")
    print("• load_all_data() - Load everything at once")
    print("="*60)


run_custom_query("SELECT * FROM ml_split_prediction_2025")