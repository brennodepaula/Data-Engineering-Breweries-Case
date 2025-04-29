# Data-Engineering-Breweries-Case

# Open Brewery Data Pipeline (Airflow + Medallion Architecture)

## Contexto e Objetivo

Este projeto tem como objetivo demonstrar a criação de uma pipeline de dados orquestrada com **Apache Airflow**, utilizando dados da [Open Brewery DB API](https://www.openbrewerydb.org/). O pipeline consome dados de cervejaria e os processa em três camadas distintas conforme a **Arquitetura Medallion**: Bronze (raw), Silver (curado e particionado, retirando aquelas cervejarias onde a informação de país e/ou estado não existia) e Gold (agregado para análise).

O projeto simula um cenário real de ingestão, tratamento, particionamento e agregação de dados com foco em boas práticas de engenharia de dados.

---

## Tecnologias Utilizadas

- **Python**
- **Apache Airflow** (orquestração)
- **Docker** (containerização)
- **Pandas** (ETL e agregação)
- **Parquet** (formato columnar)
- **API REST** (Open Brewery DB)

---

## Arquitetura Medallion

### Bronze (Raw Layer)
- Armazena os dados exatamente como retornados da API.
- Formato: `.json`
- Caminho: `data/raw/breweries_raw.json`

### Silver (Curated Layer)
- Transforma os dados brutos em um formato estruturado.
- Remove registros incompletos (sem estado ou país).
- Salva os dados em formato `.parquet`, **particionados por país e estado** (`country/state`).
- Caminho: `data/silver/{country}/{state}/breweries.parquet`

### Gold (Aggregated Layer)
- Agrega os dados da camada Silver.
- Agrupamento por país, estado e tipo de cervejaria (`brewery_type`).
- Resultado salvo como único arquivo `.parquet`.
- Caminho: `data/gold/breweries_aggregated.parquet`

---

## Estrutura do Projeto

<pre>
open-brewery-pipeline/
│
├── dags/
│   └── brewery_pipeline.py             # DAG principal com as tarefas: fetch, transform e aggregate
│
├── data/
│   ├── raw/                            # Bronze - dados brutos da API em formato JSON
│   ├── silver/                         # Silver - dados tratados em Parquet, particionados por país/estado
│   └── gold/                           # Gold - dados agregados para análise
│
├── docker-compose.yml                  # Configuração da infraestrutura do Airflow via Docker
├── requirements.txt                    # Lista de dependências Python
└── README.md                           # Documentação do projeto
 </pre>

---

## Execução

### Pré-requisitos

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

### Passos

```bash
# Clone o repositório
git clone https://github.com/brennodepaula/Data-Engineering-Breweries-Case.git

# Suba a infraestrutura
docker-compose up --build

# Acesse o Airflow no navegador
http://localhost:8080

# Login padrão:
Usuário: airflow
Senha: airflow
```
---
## Propostas
### Monitoramento e alertas
- Uso de alertas via Slack, Microsoft Teams ou email via Airflow (on_failure_callback)
- Uso de bibliotecas como a great_expectations para validações

### Utilização em Cloud
- As arquiterua das pastas poderia facilmente ser replicada em qualquer serviço de armazenamento de arquivos, como Google Cloud Storage ou Amazon S3
- Os arquivos das camadas Silver e Gold poderiam ser disponibilizados para consultas SQL no AWS Athena ou Google Big Query
- O Airflow poderia ser gerenciado dentro de uma máquina virutal ou mesmo com o uso de ferramentas específicas como o Cloud Composer do Google
