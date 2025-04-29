import requests
import json
import os
import pandas as pd  # Adicionando a importação do pandas
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

# Definir o caminho para salvar os dados
RAW_DATA_PATH = '/opt/airflow/data/raw/breweries_raw.json'
SILVER_DATA_PATH = '/opt/airflow/data/silver'
GOLD_DATA_PATH = '/opt/airflow/data/gold'

# URL da API
API_URL = "https://api.openbrewerydb.org/v1/breweries"

# Função para fazer a requisição à API e salvar os dados
def fetch_brewery_data():
    response = requests.get(API_URL)
    if response.status_code == 200:
        breweries_data = response.json()

        # Cria a pasta se não existir
        os.makedirs(os.path.dirname(RAW_DATA_PATH), exist_ok=True)

        # Salvando os dados no formato JSON
        with open(RAW_DATA_PATH, 'w') as f:
            json.dump(breweries_data, f, indent=4)
        print(f"Dados salvos em {RAW_DATA_PATH}")
    else:
        print(f"Erro ao buscar dados: {response.status_code}")


# Função SILVER: Transformar dados
def transform_brewery_data():
    if not os.path.exists(RAW_DATA_PATH):
        raise FileNotFoundError(f"Arquivo não encontrado: {RAW_DATA_PATH}")

    # Lê o JSON bruto
    try:
        df = pd.read_json(RAW_DATA_PATH)
    except Exception as e:
        print(f"Erro ao ler o arquivo JSON: {e}")
        raise

    # Seleciona apenas colunas de interesse
    df = df[['id', 'name', 'brewery_type', 'city', 'state', 'country', 'longitude', 'latitude']]

    # Remove linhas com state ou country nulos
    df = df.dropna(subset=['state', 'country'])

    # Cria o diretório silver se não existir
    os.makedirs(SILVER_DATA_PATH, exist_ok=True)

    # Salva particionado por country/state
    for (country, state), group in df.groupby(['country', 'state']):
        state_folder = os.path.join(SILVER_DATA_PATH, country, state)
        os.makedirs(state_folder, exist_ok=True)
        group.to_parquet(os.path.join(state_folder, 'breweries.parquet'), index=False)

    print(f"Dados transformados e salvos em {SILVER_DATA_PATH}")

# Função GOLD: Agregar dados usando pandas
def aggregate_brewery_data():
    if not os.path.exists(SILVER_DATA_PATH):
        raise FileNotFoundError(f"Diretório não encontrado: {SILVER_DATA_PATH}")
    
    os.makedirs(GOLD_DATA_PATH, exist_ok=True)
    output_file = os.path.join(GOLD_DATA_PATH, 'breweries_aggregated.parquet')

    # Carregar todos os arquivos Parquet da camada Silver com pandas
    all_files = []
    for root, dirs, files in os.walk(SILVER_DATA_PATH):
        for file in files:
            if file.endswith('.parquet'):
                all_files.append(os.path.join(root, file))

    # Concatenar todos os arquivos Parquet em um único DataFrame
    df_list = [pd.read_parquet(file) for file in all_files]
    df = pd.concat(df_list, ignore_index=True)

    # Agregar os dados
    aggregated_df = df.groupby(['country', 'state', 'brewery_type']).agg(
        brewery_count=('id', 'count')
    ).reset_index()

    # Salvar os dados agregados em formato Parquet
    aggregated_df.to_parquet(output_file, index=False)

    print(f"Dados agregados e salvos em {output_file}")

# Definir a DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 4, 28),  # Ajuste conforme necessário
}

dag = DAG(
    'brewery_pipeline',  # Nome da DAG
    default_args=default_args,
    description='Uma DAG para adquirir dados de uma API',
    schedule_interval='@daily',  # Defina a frequência (ex: @daily, @hourly, ou crie uma cron expression personalizada)
    catchup=False,  # Para não rodar para datas passadas
)

# Usando PythonOperator para rodar a função de aquisição de dados
fetch_data_task = PythonOperator(
    task_id='fetch_brewery_data_task',
    python_callable=fetch_brewery_data,
    dag=dag,
)

# Tarefa de Transformação (Silver)
transform_data = PythonOperator(
    task_id='transform_data',
    python_callable=transform_brewery_data,
    dag=dag,  # Certifique-se de adicionar a DAG aqui
)

# Tarefa de Agregação (Gold) usando pandas
aggregate_data = PythonOperator(
    task_id='aggregate_data',
    python_callable=aggregate_brewery_data,
    dag=dag,  # Certifique-se de adicionar a DAG aqui
)

# Definindo a sequência de execução
fetch_data_task >> transform_data >> aggregate_data