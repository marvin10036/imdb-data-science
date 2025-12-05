# frozen_string_literal: true


# Este código faz parte do projeto open-source em Ruby on Rails responsável por importar,
# tratar e estruturar no banco de dados os arquivos .tsv oficiais fornecidos pelo IMDb.
#
# O objetivo deste script é consumir esses dados já normalizados do banco local do IMDb
# e combiná-los com:
#   - a curadoria manual dos filmes indicados ao Oscar; e
#   - dados complementares obtidos pela Free IMDb API for Developers (ex.: orçamento e bilheterias).
#
# A partir dessa junção, o script gera um arquivo .csv consolidado contendo todas as
# informações essenciais, que posteriormente será utilizado por um script em Python
# para popular um novo banco de dados dedicado ao desenvolvimento do projeto.


class MovieCollector
  MIN_VOTES = 50_000 #100_000
  MIN_YEAR = 1999
  MAX_YEAR = 2024
  IMDB_API_BASE_URL = 'https://api.imdbapi.dev'

  def initialize
    @collected_movies = []
    @errors = []
    @api_client = setup_api_client
    @oscar_movies_map = build_oscar_movies_map
  end

  def collect_all_movies
    puts "🎬 Iniciando coleta COMPLETA de filmes..."
    puts "📊 Critério: Filmes com mais de #{MIN_VOTES.to_s.reverse.gsub(/(\d{3})(?=\d)/, '\\1.').reverse} votos"
    
    # 1. Buscar TODOS os filmes com votes > 100.000
    all_movies = fetch_all_movies_from_database
    
    puts "📊 Encontrados #{all_movies.size} filmes no banco"
    
    # 2. Processar cada filme e enriquecer com dados da IMDbAPI
    process_movies(all_movies)
    
    # 3. Gerar CSV final consolidado
    generate_csv
    
    print_summary
  end

  private

  def setup_api_client
    Faraday.new(url: IMDB_API_BASE_URL) do |conn|
      conn.request :json
      conn.response :json
      conn.adapter Faraday.default_adapter
      conn.options.timeout = 10
      conn.options.open_timeout = 5
    end
  end

  def build_oscar_movies_map
    # Mapa: { imdb_id => { year, brazilian_title, winner } }
    oscar_data = {}

    oscar_list = [
      # Oscar 2000 (filmes de 1999)
      ['tt0169547', '2000', 'American Beauty', 'Beleza Americana', true],
      ['tt0162222', '2000', 'The Cider House Rules', 'Regras da Vida', false],
      ['tt0120689', '2000', 'The Green Mile', 'À Espera de um Milagre', false],
      ['tt0140352', '2000', 'The Insider', 'O Informante', false],
      ['tt0167404', '2000', 'The Sixth Sense', 'O Sexto Sentido', false],
      
      # Oscar 2001 (filmes de 2000)
      ['tt0172495', '2001', 'Gladiator', 'Gladiador', true],
      ['tt0241303', '2001', 'Chocolat', 'Chocolate', false],
      ['tt0190332', '2001', 'Crouching Tiger, Hidden Dragon', 'O Tigre e o Dragão', false],
      ['tt0195685', '2001', 'Erin Brockovich', 'Erin Brockovich - Uma Mulher de Talento', false],
      ['tt0181865', '2001', 'Traffic', 'Traffic', false],
      
      # Oscar 2002 (filmes de 2001)
      ['tt0268978', '2002', 'A Beautiful Mind', 'Uma Mente Brilhante', true],
      ['tt0280707', '2002', 'Gosford Park', 'Assassinato em Gosford Park', false],
      ['tt0197182', '2002', 'In the Bedroom', 'Entre Quatro Paredes', false],
      ['tt0120737', '2002', 'The Lord of the Rings: The Fellowship of the Ring', 'O Senhor dos Anéis: A Sociedade do Anel', false],
      ['tt0203009', '2002', 'Moulin Rouge!', 'Moulin Rouge - Amor em Vermelho', false],
      
      # Oscar 2003 (filmes de 2002)
      ['tt0299658', '2003', 'Chicago', 'Chicago', true],
      ['tt0217505', '2003', 'Gangs of New York', 'Gangues de Nova York', false],
      ['tt0274558', '2003', 'The Hours', 'As Horas', false],
      ['tt0167261', '2003', 'The Lord of the Rings: The Two Towers', 'O Senhor dos Anéis: As Duas Torres', false],
      ['tt0253474', '2003', 'The Pianist', 'O Pianista', false],
      
      # Oscar 2004 (filmes de 2003)
      ['tt0167260', '2004', 'The Lord of the Rings: The Return of the King', 'O Senhor dos Anéis: O Retorno do Rei', true],
      ['tt0335266', '2004', 'Lost in Translation', 'Encontros e Desencontros', false],
      ['tt0311113', '2004', 'Master and Commander: The Far Side of the World', 'Mestre dos Mares - O Lado Mais Distante do Mundo', false],
      ['tt0327056', '2004', 'Mystic River', 'Sobre Meninos e Lobos', false],
      ['tt0329575', '2004', 'Seabiscuit', 'Seabiscuit - Alma de Herói', false],
      
      # Oscar 2005 (filmes de 2004)
      ['tt0405159', '2005', 'Million Dollar Baby', 'Menina de Ouro', true],
      ['tt0338751', '2005', 'The Aviator', 'O Aviador', false],
      ['tt0308644', '2005', 'Finding Neverland', 'Em Busca da Terra do Nunca', false],
      ['tt0350258', '2005', 'Ray', 'Ray', false],
      ['tt0375063', '2005', 'Sideways', 'Sideways - Entre Umas e Outras', false],
      
      # Oscar 2006 (filmes de 2005)
      ['tt0375679', '2006', 'Crash', 'Crash - No Limite', true],
      ['tt0388795', '2006', 'Brokeback Mountain', 'O Segredo de Brokeback Mountain', false],
      ['tt0379725', '2006', 'Capote', 'Capote', false],
      ['tt0433383', '2006', 'Good Night, and Good Luck.', 'Boa Noite, e Boa Sorte', false],
      ['tt0408306', '2006', 'Munich', 'Munique', false],
      
      # Oscar 2007 (filmes de 2006)
      ['tt0407887', '2007', 'The Departed', 'Os Infiltrados', true],
      ['tt0449467', '2007', 'Babel', 'Babel', false],
      ['tt0498380', '2007', 'Letters from Iwo Jima', 'Cartas de Iwo Jima', false],
      ['tt0449059', '2007', 'Little Miss Sunshine', 'Pequena Miss Sunshine', false],
      ['tt0436697', '2007', 'The Queen', 'A Rainha', false],
      
      # Oscar 2008 (filmes de 2007)
      ['tt0477348', '2008', 'No Country for Old Men', 'Onde os Fracos Não Têm Vez', true],
      ['tt0783233', '2008', 'Atonement', 'Desejo e Reparação', false],
      ['tt0467406', '2008', 'Juno', 'Juno', false],
      ['tt0465538', '2008', 'Michael Clayton', 'Conduta de Risco', false],
      ['tt0469494', '2008', 'There Will Be Blood', 'Sangue Negro', false],
      
      # Oscar 2009 (filmes de 2008)
      ['tt1010048', '2009', 'Slumdog Millionaire', 'Quem Quer Ser Um Milionário?', true],
      ['tt0976051', '2009', 'The Reader', 'O Leitor', false],
      ['tt0870111', '2009', 'Frost/Nixon', 'Frost/Nixon', false],
      ['tt0421715', '2009', 'The Curious Case of Benjamin Button', 'O Curioso Caso de Benjamin Button', false],
      ['tt1013753', '2009', 'Milk', 'Milk - A Voz da Igualdade', false],
      
      # Oscar 2010 (filmes de 2009)
      ['tt1655246', '2010', 'The Hurt Locker', 'Guerra ao Terror', true],
      ['tt0499549', '2010', 'Avatar', 'Avatar', false],
      ['tt0878804', '2010', 'The Blind Side', 'Um Sonho Possível', false],
      ['tt1136608', '2010', 'District 9', 'Distrito 9', false],
      ['tt1174732', '2010', 'An Education', 'Educação', false],
      ['tt0361748', '2010', 'Inglourious Basterds', 'Bastardos Inglórios', false],
      ['tt1019452', '2010', 'A Serious Man', 'Um Homem Sério', false],
      ['tt0929632', '2010', 'Precious', 'Preciosa: Uma História de Esperança', false],
      ['tt1049413', '2010', 'Up', 'Up: Altas Aventuras', false],
      ['tt1193138', '2010', 'Up in the Air', 'Amor Sem Escalas', false],
      
      # Oscar 2011 (filmes de 2010)
      ['tt1504320', '2011', "The King's Speech", 'O Discurso do Rei', true],
      ['tt1542344', '2011', '127 Hours', '127 Horas', false],
      ['tt0947798', '2011', 'Black Swan', 'Cisne Negro', false],
      ['tt1375666', '2011', 'Inception', 'A Origem', false],
      ['tt0964517', '2011', 'The Fighter', 'O Vencedor', false],
      ['tt1104001', '2011', 'The Kids Are All Right', 'Minhas Mães e Meu Pai', false],
      ['tt1285016', '2011', 'The Social Network', 'A Rede Social', false],
      ['tt0435761', '2011', 'Toy Story 3', 'Toy Story 3', false],
      ['tt1403865', '2011', 'True Grit', 'Bravura Indômita', false],
      ['tt1399683', '2011', "Winter's Bone", 'Inverno da Alma', false],
      
      # Oscar 2012 (filmes de 2011)
      ['tt1655442', '2012', 'The Artist', 'O Artista', true],
      ['tt1568911', '2012', 'War Horse', 'Cavalo de Guerra', false],
      ['tt1210166', '2012', 'Moneyball', 'O Homem que Mudou o Jogo', false],
      ['tt0477302', '2012', 'Extremely Loud and Incredibly Close', 'Tão Forte e Tão Perto', false],
      ['tt1454029', '2012', 'The Help', 'Histórias Cruzadas', false],
      ['tt0970179', '2012', 'Hugo', 'A Invenção de Hugo Cabret', false],
      ['tt1605783', '2012', 'Midnight in Paris', 'Meia-Noite em Paris', false],
      ['tt1033575', '2012', 'The Descendants', 'Os Descendentes', false],
      ['tt0478304', '2012', 'The Tree of Life', 'A Árvore da Vida', false],
      
      # Oscar 2013 (filmes de 2012)
      ['tt1024648', '2013', 'Argo', 'Argo', true],
      ['tt1602620', '2013', 'Amour', 'Amor', false],
      ['tt2125435', '2013', 'Beasts of the Southern Wild', 'Indomável Sonhadora', false],
      ['tt1853728', '2013', 'Django Unchained', 'Django Livre', false],
      ['tt1707386', '2013', 'Les Misérables', 'Os Miseráveis', false],
      ['tt0454876', '2013', 'Life of Pi', 'As Aventuras de Pi', false],
      ['tt0443272', '2013', 'Lincoln', 'Lincoln', false],
      ['tt1045658', '2013', 'Silver Linings Playbook', 'O Lado Bom da Vida', false],
      ['tt1790885', '2013', 'Zero Dark Thirty', 'A Hora Mais Escura', false],
      
      # Oscar 2014 (filmes de 2013)
      ['tt2024544', '2014', '12 Years a Slave', '12 Anos de Escravidão', true],
      ['tt1800241', '2014', 'American Hustle', 'Trapaça', false],
      ['tt1454468', '2014', 'Gravity', 'Gravidade', false],
      ['tt0993846', '2014', 'The Wolf of Wall Street', 'O Lobo de Wall Street', false],
      ['tt0790636', '2014', 'Dallas Buyers Club', 'Clube de Compras Dallas', false],
      ['tt1798709', '2014', 'Her', 'Ela', false],
      ['tt1535109', '2014', 'Captain Phillips', 'Capitão Phillips', false],
      ['tt1821549', '2014', 'Nebraska', 'Nebraska', false],
      ['tt2431286', '2014', 'Philomena', 'Philomena', false],
      
      # Oscar 2015 (filmes de 2014)
      ['tt2562232', '2015', 'Birdman or (The Unexpected Virtue of Ignorance)', 'Birdman ou (A Inesperada Virtude da Ignorância)', true],
      ['tt1065073', '2015', 'Boyhood', 'Boyhood: Da Infância à Juventude', false],
      ['tt2278388', '2015', 'The Grand Budapest Hotel', 'O Grande Hotel Budapeste', false],
      ['tt2084970', '2015', 'The Imitation Game', 'O Jogo da Imitação', false],
      ['tt2980516', '2015', 'The Theory of Everything', 'A Teoria de Tudo', false],
      ['tt1020072', '2015', 'Selma', 'Selma: Uma Luta Pela Igualdade', false],
      ['tt2179136', '2015', 'American Sniper', 'Sniper Americano', false],
      ['tt2582802', '2015', 'Whiplash', 'Whiplash: Em Busca da Perfeição', false],
      
      # Oscar 2016 (filmes de 2015)
      ['tt1895587', '2016', 'Spotlight', 'Spotlight: Segredos Revelados', true],
      ['tt1596363', '2016', 'The Big Short', 'A Grande Aposta', false],
      ['tt3682448', '2016', 'Bridge of Spies', 'Ponte dos Espiões', false],
      ['tt2381111', '2016', 'Brooklyn', 'Brooklyn', false],
      ['tt1392190', '2016', 'Mad Max: Fury Road', 'Mad Max: Estrada da Fúria', false],
      ['tt3659388', '2016', 'The Martian', 'Perdido em Marte', false],
      ['tt1663202', '2016', 'The Revenant', 'O Regresso', false],
      ['tt3170832', '2016', 'Room', 'O Quarto de Jack', false],
      
      # Oscar 2017 (filmes de 2016)
      ['tt4975722', '2017', 'Moonlight', 'Moonlight: Sob a Luz do Luar', true],
      ['tt2543164', '2017', 'Arrival', 'A Chegada', false],
      ['tt2671706', '2017', 'Fences', 'Um Limite Entre Nós', false],
      ['tt2119532', '2017', 'Hacksaw Ridge', 'Até o Último Homem', false],
      ['tt2582782', '2017', 'Hell or High Water', 'A Qualquer Custo', false],
      ['tt4846340', '2017', 'Hidden Figures', 'Estrelas Além do Tempo', false],
      ['tt3783958', '2017', 'La La Land', 'La La Land: Cantando Estações', false],
      ['tt3741834', '2017', 'Lion', 'Lion: Uma Jornada Para Casa', false],
      ['tt4034228', '2017', 'Manchester by the Sea', 'Manchester à Beira-Mar', false],
      
      # Oscar 2018 (filmes de 2017)
      ['tt5580390', '2018', 'The Shape of Water', 'A Forma da Água', true],
      ['tt5726616', '2018', 'Call Me by Your Name', 'Me Chame Pelo Seu Nome', false],
      ['tt4555426', '2018', 'Darkest Hour', 'O Destino de uma Nação', false],
      ['tt5013056', '2018', 'Dunkirk', 'Dunkirk', false],
      ['tt5052448', '2018', 'Get Out', 'Corra!', false],
      ['tt4925292', '2018', 'Lady Bird', 'Lady Bird: A Hora de Voar', false],
      ['tt5776858', '2018', 'Phantom Thread', 'Trama Fantasma', false],
      ['tt6294822', '2018', 'The Post', 'The Post: A Guerra Secreta', false],
      ['tt5027774', '2018', 'Three Billboards Outside Ebbing, Missouri', 'Três Anúncios Para um Crime', false],
      
      # Oscar 2019 (filmes de 2018)
      ['tt6966692', '2019', 'Green Book', 'Green Book: O Guia', true],
      ['tt1825683', '2019', 'Black Panther', 'Pantera Negra', false],
      ['tt7349950', '2019', 'BlacKkKlansman', 'Infiltrado na Klan', false],
      ['tt1727824', '2019', 'Bohemian Rhapsody', 'Bohemian Rhapsody', false],
      ['tt5083738', '2019', 'The Favourite', 'A Favorita', false],
      ['tt6155172', '2019', 'Roma', 'Roma', false],
      ['tt1517451', '2019', 'A Star Is Born', 'Nasce uma Estrela', false],
      ['tt6266538', '2019', 'Vice', 'Vice', false],
      
      # Oscar 2020 (filmes de 2019)
      ['tt6751668', '2020', 'Parasite', 'Parasita', true],
      ['tt8579674', '2020', '1917', '1917', false],
      ['tt1950186', '2020', 'Ford v Ferrari', 'Ford vs Ferrari', false],
      ['tt1302006', '2020', 'The Irishman', 'O Irlandês', false],
      ['tt2584384', '2020', 'Jojo Rabbit', 'Jojo Rabbit', false],
      ['tt7286456', '2020', 'Joker', 'Coringa', false],
      ['tt3281548', '2020', 'Little Women', 'Adoráveis Mulheres', false],
      ['tt7653254', '2020', 'Marriage Story', 'História de Um Casamento', false],
      ['tt7131622', '2020', 'Once Upon a Time in Hollywood', 'Era Uma Vez Em... Hollywood', false],
      
      # Oscar 2021 (filmes de 2020)
      ['tt9770150', '2021', 'Nomadland', 'Nomadland', true],
      ['tt10272386', '2021', 'The Father', 'Meu Pai', false],
      ['tt11083552', '2021', 'Judas and the Black Messiah', 'Judas e o Messias Negro', false],
      ['tt10618286', '2021', 'Mank', 'Mank', false],
      ['tt10633456', '2021', 'Minari', 'Minari: Em Busca da Felicidade', false],
      ['tt9620292', '2021', 'Promising Young Woman', 'Bela Vingança', false],
      ['tt5363618', '2021', 'Sound of Metal', 'O Som do Silêncio', false],
      ['tt1070874', '2021', 'The Trial of the Chicago 7', 'Os 7 de Chicago', false],
      
      # Oscar 2022 (filmes de 2021)
      ['tt10366460', '2022', 'CODA', 'No Ritmo do Coração', true],
      ['tt12789558', '2022', 'Belfast', 'Belfast', false],
      ['tt11286314', '2022', "Don't Look Up", 'Não Olhe Para Cima', false],
      ['tt14039582', '2022', 'Drive My Car', 'Drive My Car', false],
      ['tt1160419', '2022', 'Dune', 'Duna', false],
      ['tt9620288', '2022', 'King Richard', 'King Richard: Criando Campeãs', false],
      ['tt11271038', '2022', 'Licorice Pizza', 'Licorice Pizza', false],
      ['tt7740496', '2022', 'Nightmare Alley', 'O Beco do Pesadelo', false],
      ['tt10293406', '2022', 'The Power of the Dog', 'Ataque dos Cães', false],
      ['tt3581652', '2022', 'West Side Story', 'Amor, Sublime Amor', false],
      
      # Oscar 2023 (filmes de 2022)
      ['tt6710474', '2023', 'Everything Everywhere All at Once', 'Tudo em Todo Lugar ao Mesmo Tempo', true],
      ['tt1016150', '2023', 'All Quiet on the Western Front', 'Nada de Novo no Front', false],
      ['tt1630029', '2023', 'Avatar: The Way of Water', 'Avatar: O Caminho da Água', false],
      ['tt11813216', '2023', 'The Banshees of Inisherin', 'Os Banshees de Inisherin', false],
      ['tt3704428', '2023', 'Elvis', 'Elvis', false],
      ['tt14208870', '2023', 'The Fabelmans', 'Os Fabelmans', false],
      ['tt14444726', '2023', 'Tár', 'TÁR', false],
      ['tt1745960', '2023', 'Top Gun: Maverick', 'Top Gun: Maverick', false],
      ['tt7322224', '2023', 'Triangle of Sadness', 'Triângulo da Tristeza', false],
      ['tt13669038', '2023', 'Women Talking', 'Entre Mulheres', false],
      
      # Oscar 2024 (filmes de 2023)
      ['tt15398776', '2024', 'Oppenheimer', 'Oppenheimer', true],
      ['tt23561236', '2024', 'American Fiction', 'Ficção Americana', false],
      ['tt17009710', '2024', 'Anatomy of a Fall', 'Anatomia de uma Queda', false],
      ['tt1517268', '2024', 'Barbie', 'Barbie', false],
      ['tt14444933', '2024', 'The Holdovers', 'Os Rejeitados', false],
      ['tt5537002', '2024', 'Killers of the Flower Moon', 'Assassinos da Lua das Flores', false],
      ['tt5537380', '2024', 'Maestro', 'Maestro', false],
      ['tt13238346', '2024', 'Past Lives', 'Vidas Passadas', false],
      ['tt14230458', '2024', 'Poor Things', 'Pobres Criaturas', false],
      ['tt7160372', '2024', 'The Zone of Interest', 'Zona de Interesse', false],
      
      # Oscar 2025 (filmes de 2024)
      ['tt28607951', '2025', 'Anora', 'Anora', true],
      ['tt14444912', '2025', 'The Brutalist', 'O Brutalista', false],
      ['tt28239891', '2025', 'A Complete Unknown', 'Um Completo Desconhecido', false],
      ['tt22041854', '2025', 'Conclave', 'Conclave', false],
      ['tt15239678', '2025', 'Dune: Part Two', 'Duna: Parte Dois', false],
      ['tt21064584', '2025', 'Emilia Pérez', 'Emilia Pérez', false],
      ['tt22688572', '2025', 'Ainda Estou Aqui', 'Ainda Estou Aqui', false],
      ['tt23561236', '2025', 'Nickel Boys', 'O Reformatório Nickel', false],
      ['tt17526714', '2025', 'The Substance', 'A Substância', false],
      ['tt1262426', '2025', 'Wicked', 'Wicked', false]
    ]
    
    oscar_list.each do |imdb_id, year, original, brazilian, winner|
      oscar_data[imdb_id] = {
        oscar_year: year,
        original_title: original,
        brazilian_title: brazilian,
        winner: winner
      }
    end
    
    oscar_data
  end

  def fetch_all_movies_from_database
    puts "🔍 Buscando filmes com mais de #{MIN_VOTES} votos..."
    
    sql = <<-SQL
      SELECT 
        t.id,
        t.unique_id AS imdb_id,
        t.title AS titulo_original,
        t.original_title,
        t.start_year AS ano_lancamento,
        t.rating AS nota_imdb,
        t.votes AS votos,
        t.runtime AS duracao_minutos
      FROM titles t
      WHERE t.title_type = 'movie'
        AND t.votes >= #{MIN_VOTES}
        AND t.rating IS NOT NULL
        AND t.start_year BETWEEN #{MIN_YEAR} AND #{MAX_YEAR}
      ORDER BY t.votes DESC, t.rating DESC;
    SQL

    ActiveRecord::Base.connection.execute(sql).to_a
  end

  def process_movies(all_movies)
    puts "🔄 Processando filmes e enriquecendo dados..."
    
    total = all_movies.size
    all_movies.each_with_index do |movie_row, index|
      begin
        imdb_id = movie_row['imdb_id']
        
        # Buscar o objeto Title completo para acessar relacionamentos
        title = Title.includes(:genres, :directors, :title_writers, :title_principals)
                    .find(movie_row['id'])
        
        # Verificar se é filme do Oscar
        oscar_info = @oscar_movies_map[imdb_id]
        is_oscar = oscar_info.present?
        
        # Buscar título brasileiro
        brazilian_title = if is_oscar
          oscar_info[:brazilian_title]
        else
          get_brazilian_title(title)
        end
        
        movie_data = {
          imdb_id: imdb_id,
          titulo_original: movie_row['titulo_original'],
          titulo_brasileiro: brazilian_title,
          ano_lancamento: movie_row['ano_lancamento'],
          nota_imdb: movie_row['nota_imdb'],
          votos: movie_row['votos'],
          duracao_minutos: movie_row['duracao_minutos'],
          
          # Marcação Oscar
          indicado_oscar: is_oscar ? 'Sim' : 'Não',
          vencedor_oscar: is_oscar && oscar_info[:winner] ? 'Sim' : 'Não',
          ano_cerimonia_oscar: is_oscar ? oscar_info[:oscar_year] : '',
          status_oscar: if is_oscar
            oscar_info[:winner] ? '🏆 Vencedor' : '🎬 Indicado'
          else
            ''
          end,
          
          # Dados do banco
          generos: get_genres(title),
          diretores: get_directors(title),
          roteiristas: get_writers(title),
          elenco_principal: get_main_cast(title),
          
          # Dados da IMDbAPI
          paises: fetch_imdb_api_data(imdb_id, 'originCountries'),
          idiomas: fetch_imdb_api_data(imdb_id, 'spokenLanguages'),
          orcamento: fetch_imdb_api_data(imdb_id, 'boxOffice', 'productionBudget'),
          bilheteria_mundial: fetch_imdb_api_data(imdb_id, 'boxOffice', 'worldwideGross'),
          bilheteria_domestica: fetch_imdb_api_data(imdb_id, 'boxOffice', 'domesticGross'),
          metascore: fetch_imdb_api_data(imdb_id, 'metacritic', 'score'),
          sinopse: fetch_imdb_api_data(imdb_id, 'plot')
        }
        
        @collected_movies << movie_data
        
        if (index + 1) % 50 == 0
          puts "⏳ Processados #{index + 1}/#{total} filmes..."
        end
        
        # Rate limiting suave
        sleep(0.05)
        
      rescue => e
        @errors << "Erro ao processar filme ID #{movie_row['id']}: #{e.message}"
        puts "❌ Erro: #{movie_row['titulo_original']} - #{e.message}"
      end
    end
    
    puts "✅ Processamento concluído: #{@collected_movies.size} filmes"
  end

  def get_brazilian_title(title)
    # Buscar título brasileiro na tabela title_aliases
    alias_br = title.title_aliases
                   .where("region_id = ?", 15)
                   .first
    
    alias_br&.name || title.original_title
  rescue => e
    @errors << "Erro ao buscar título brasileiro para #{title.title}: #{e.message}"
    title.original_title
  end

  def get_genres(title)
    title.genres.pluck(:name).join(', ')
  rescue => e
    @errors << "Erro ao buscar gêneros para #{title.title}: #{e.message}"
    ''
  end

  def get_directors(title)
    title.directors.pluck(:name).join(', ')
  rescue => e
    @errors << "Erro ao buscar diretores para #{title.title}: #{e.message}"
    ''
  end

  def get_writers(title)
    title.title_writers
         .joins(:person)
         .pluck('people.name')
         .join(', ')
  rescue => e
    @errors << "Erro ao buscar roteiristas para #{title.title}: #{e.message}"
    ''
  end

  def get_main_cast(title)
    title.title_principals
         .where(principal_category: ['actor', 'actress'])
         .order(:ordering)
         .limit(5)
         .joins(:person)
         .pluck('people.name')
         .join(', ')
  rescue => e
    @errors << "Erro ao buscar elenco para #{title.title}: #{e.message}"
    ''
  end

  def fetch_imdb_api_data(imdb_id, *fields)
    return nil if imdb_id.blank?
  
    # Caches separados: detalhes vs. box office
    @imdb_api_cache ||= {}
    @imdb_api_cache[:titles] ||= {}
    @imdb_api_cache[:box_office] ||= {}
  
    # Helper para GET com cache
    def cached_get(cache_bucket, cache_key)
      return cache_bucket[cache_key] if cache_bucket.key?(cache_key)
  
      begin
        response = yield
        if response.respond_to?(:success?) ? response.success? : (response.status.to_i / 100 == 2)
          body = response.respond_to?(:body) ? response.body : response
          cache_bucket[cache_key] = body || {}
        else
          cache_bucket[cache_key] = {}
        end
      rescue => e
        @errors << "Erro ao buscar IMDbAPI #{cache_key}: #{e.message}"
        cache_bucket[cache_key] = {}
      end
  
      cache_bucket[cache_key]
    end
  
    # Carrega detalhes gerais do título (sem box office)
    title_key = "titles:#{imdb_id}"
    title_data = cached_get(@imdb_api_cache[:titles], title_key) do
      @api_client.get("/titles/#{imdb_id}")
    end
  
    # Carrega box office em endpoint dedicado
    # Observação: seu YAML/screenshot mostra "boxOffice" (singular). Se no seu YAML estiver "boxOffices", mude a linha abaixo para "/titles/#{imdb_id}/boxOffices".
    box_key = "boxOffice:#{imdb_id}"
    box_data = cached_get(@imdb_api_cache[:box_office], box_key) do
      @api_client.get("/titles/#{imdb_id}/boxOffice")
    end
  
    # Se não foram solicitados fields específicos, retorne um merge dos dois blobs
    if fields.blank?
      return title_data.is_a?(Hash) && box_data.is_a?(Hash) ? title_data.merge('boxOffice' => box_data) : title_data
    end
  
    # Se o primeiro campo for "boxOffice", navegue dentro do payload do box office
    if fields.first == 'boxOffice'
      data = box_data
      fields[1..].each do |field|
        data = data[field] if data.is_a?(Hash)
      end
  
      # Formatações específicas de valores monetários
      case fields[1] # segundo nível dentro de boxOffice
      when 'worldwideGross', 'domesticGross', 'openingWeekendGross', 'productionBudget'
        if data.is_a?(Hash)
          amount = data['amount']
          currency = data['currency']
          amount ? "#{currency} #{format_money(amount)}" : nil
        else
          nil
        end
      when 'weekendEndDate'
        if data.is_a?(Hash) && data['year'] && data['month'] && data['day']
          "%04d-%02d-%02d" % [data['year'], data['month'], data['day']]
        else
          nil
        end
      else
        data
      end
    else
      # Navegação por campos dos detalhes gerais
      data = title_data
      fields.each do |field|
        data = data[field] if data.is_a?(Hash)
      end
  
      # Formatações específicas já existentes
      case fields.first
      when 'originCountries'
        data.is_a?(Array) ? data.map { |c| c['name'] }.join(', ') : nil
      when 'spokenLanguages'
        data.is_a?(Array) ? data.map { |l| l['name'] }.join(', ') : nil
      else
        data
      end
    end
  end

  def format_money(amount)
    amount.to_s.reverse.gsub(/(\d{3})(?=\d)/, '\\1,').reverse
  end

  def generate_csv
    puts "📄 Gerando arquivo CSV consolidado..."
    
    filename = "filmes_completo_#{Time.current.strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = Rails.root.join('tmp', filename)
    
    CSV.open(filepath, 'w', encoding: 'UTF-8') do |csv|
      # Cabeçalho
      csv << [
        'ID IMDb',
        'Título Original',
        'Título Brasileiro',
        'Ano Lançamento',
        'Nota IMDb',
        'Votos',
        'Duração (min)',
        'Indicado Oscar',
        'Vencedor Oscar',
        'Ano Cerimônia Oscar',
        'Status Oscar',
        'Gêneros',
        'Diretores',
        'Roteiristas',
        'Elenco Principal',
        'Países',
        'Idiomas',
        'Orçamento',
        'Bilheteria Mundial',
        'Bilheteria Doméstica',
        'Metascore',
        'Sinopse'
      ]
      
      # Dados
      @collected_movies.each do |movie|
        csv << [
          movie[:imdb_id],
          movie[:titulo_original],
          movie[:titulo_brasileiro],
          movie[:ano_lancamento],
          movie[:nota_imdb],
          movie[:votos],
          movie[:duracao_minutos],
          movie[:indicado_oscar],
          movie[:vencedor_oscar],
          movie[:ano_cerimonia_oscar],
          movie[:status_oscar],
          movie[:generos],
          movie[:diretores],
          movie[:roteiristas],
          movie[:elenco_principal],
          movie[:paises],
          movie[:idiomas],
          movie[:orcamento],
          movie[:bilheteria_mundial],
          movie[:bilheteria_domestica],
          movie[:metascore],
          movie[:sinopse]
        ]
      end
    end
    
    puts "✅ Arquivo CSV gerado: #{filepath}"
    puts "📊 Total de filmes no CSV: #{@collected_movies.size}"
  end

  def print_summary
    oscar_count = @collected_movies.count { |m| m[:indicado_oscar] == 'Sim' }
    winner_count = @collected_movies.count { |m| m[:vencedor_oscar] == 'Sim' }
    regular_count = @collected_movies.size - oscar_count
    
    puts "\n" + ('=' * 80)
    puts "📊 RESUMO DA COLETA COMPLETA DE FILMES"
    puts '=' * 80
    puts "📅 Período: #{MIN_YEAR} - #{MAX_YEAR}"
    puts "🎬 Total de filmes coletados: #{@collected_movies.size}"
    puts ""
    puts "🏆 FILMES DO OSCAR:"
    puts "   • Indicados/Vencedores: #{oscar_count}"
    puts "   • Vencedores: #{winner_count}"
    puts "   • Indicados: #{oscar_count - winner_count}"
    puts ""
    puts "🎥 OUTROS FILMES:"
    puts "   • Filmes populares (>#{MIN_VOTES} votos): #{regular_count}"
    puts ""
    puts "⭐ Nota média IMDb: #{(@collected_movies.sum { |m| m[:nota_imdb].to_f } / @collected_movies.size).round(2)}"
    puts "👥 Média de votos: #{(@collected_movies.sum { |m| m[:votos].to_i } / @collected_movies.size).to_s.reverse.gsub(/(\d{3})(?=\d)/, '\\1.').reverse}"
    puts "❌ Erros encontrados: #{@errors.size}"
    
    if @errors.any?
      puts "\n🔍 PRIMEIROS 10 ERROS:"
      @errors.first(10).each { |error| puts "  - #{error}" }
    end

    puts '=' * 80
  end
end