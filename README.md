# Data-Engineering-Breweries-Case

# 🍺 Open Brewery Data Pipeline (Airflow + Medallion Architecture)

## Contexto e Objetivo

Este projeto tem como objetivo demonstrar a criação de uma pipeline de dados orquestrada com **Apache Airflow**, utilizando dados da [Open Brewery DB API](https://www.openbrewerydb.org/). O pipeline consome dados de cervejaria e os processa em três camadas distintas conforme a **Arquitetura Medallion**: Bronze (raw), Silver (curado e particionado) e Gold (agregado para análise).

O projeto simula um cenário real de ingestão, tratamento, particionamento e agregação de dados com foco em boas práticas de engenharia de dados.

---

## 🔧 Tecnologias Utilizadas

- **Python**
- **Apache Airflow** (orquestração)
- **Docker** (containerização)
- **Pandas** (ETL e agregação)
- **Parquet** (formato columnar)
- **API REST** (Open Brewery DB)

---

## 🗺️ Arquitetura Medallion

### 🔹 Bronze (Raw Layer)
- Armazena os dados exatamente como retornados da API.
- Formato: `.json`
- Caminho: `data/raw/breweries_raw.json`

### 🔸 Silver (Curated Layer)
- Transforma os dados brutos em um formato estruturado.
- Remove registros incompletos (sem estado ou país).
- Salva os dados em formato `.parquet`, **particionados por país e estado** (`country/state`).
- Caminho: `data/silver/{country}/{state}/breweries.parquet`

### 🟡 Gold (Aggregated Layer)
- Agrega os dados da camada Silver.
- Agrupamento por país, estado e tipo de cervejaria (`brewery_type`).
- Resultado salvo como único arquivo `.parquet`.
- Caminho: `data/gold/breweries_aggregated.parquet`

