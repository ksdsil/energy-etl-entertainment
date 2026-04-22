# 🎢 Energy Efficiency ETL — Aquatic Entertainment Park
### Estudo de Eficiência Energética — Parque de Entretenimento Aquático

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Pandas](https://img.shields.io/badge/Pandas-ETL-green?logo=pandas)
![SciPy](https://img.shields.io/badge/SciPy-Regression-orange)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey?logo=sqlite)
![Status](https://img.shields.io/badge/Status-Concluído-brightgreen)

---

## 📌 Sobre o Projeto

Este projeto digitaliza um **estudo de eficiência energética** conduzido em um parque aquático de grande porte — originalmente executado com coleta manual de dados em campo — transformando-o em um **pipeline de dados completo** com análise estatística, banco relacional e visualizações profissionais.

O estudo seguiu rigorosamente o protocolo **IPMVP 2012** *(International Performance Measurement and Verification Protocol)* e a norma **ABNT NBR ISO 50001**, cobrindo 12 meses de linha de base.

> **Descoberta principal:** O consumo de energia do parque **não é determinado pelo número de visitantes**, mas sim pela **temperatura regional acima de 20°C** — identificado com R²=0,89, acima do mínimo aceitável de 0,75 pelo protocolo IPMVP.

---

## 🎯 Objetivos Técnicos

- Identificar o **DNA de consumo energético** via análise de regressão (protocolo IPMVP)
- Testar 3 variáveis independentes: visitantes, temperatura >23°C e temperatura >20°C
- Mapear capacidade instalada em 5 sistemas e 6 centros de custo
- Quantificar perdas por energia reativa
- Diagnosticar condições operacionais do sistema motriz (40 motores/bombas)

---

## 🗂️ Estrutura do Repositório

```
energy-etl-entertainment/
│
├── data/
│   ├── raw/                              # Datasets sintéticos (baseados em dados reais anonimizados)
│   │   ├── temperaturas_regionais.csv
│   │   ├── producao_visitantes.csv
│   │   ├── consumo_energia.csv
│   │   ├── capacidade_instalada.csv
│   │   ├── centros_de_custo.csv
│   │   ├── inventario_motores.csv
│   │   └── energia_reativa.csv
│   └── processed/
│       └── energia_parque.db             # SQLite com 6 tabelas
│
├── src/
│   ├── generate_data.py                  # Geração dos datasets sintéticos
│   ├── etl_pipeline.py                   # Pipeline ETL + análise de regressão IPMVP
│   └── analysis.py                       # 6 visualizações profissionais
│
├── outputs/                              # Gráficos gerados automaticamente
│   ├── 01_consumo_visitantes_temperatura.png
│   ├── 02_regressoes_ipmvp.png
│   ├── 03_capacidade_instalada.png
│   ├── 04_centros_de_custo.png
│   ├── 05_status_motores.png
│   └── 06_energia_reativa_multas.png
│
├── requirements.txt
└── README.md
```

---

## 🛠️ Stack Tecnológica

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.10+ |
| Manipulação de dados | Pandas, NumPy |
| Análise estatística | SciPy (regressão linear, R²) |
| Banco de dados | SQLite |
| Visualização | Matplotlib |
| Protocolo de referência | IPMVP 2012 / ISO 50001 |

---

## 📊 KPIs do Projeto

| Indicador | Valor |
|---|---|
| Capacidade instalada total mapeada | **703,27 kW** |
| Consumo médio mensal (ano base) | ~73,8 MWh/mês |
| **DNA identificado** | **Temperatura > 20°C** |
| R² Temperatura >20°C × Consumo | **0,89** ✅ |
| R² Visitantes × Consumo | 0,67 ❌ (descartado) |
| Média energética por visitante | 11,10 kWh |
| Custo médio por visitante | R$ 2,44 |
| Perdas energia reativa (período) | **R$ 58.243,58** |
| Motores operando acima da capacidade | **28%** |
| Motores operando abaixo da capacidade | **25%** |

---

## 📈 Visualizações Geradas

### 1. Consumo × Visitantes × Temperatura
Evidencia visualmente que o consumo segue o padrão térmico, não o fluxo de visitantes.

### 2. Análise de Regressão IPMVP — 3 Variáveis
Gráfico de dispersão com linha de tendência para cada relação testada, com R² destacado. Demonstra o processo metodológico completo de identificação do determinante.

### 3. Capacidade Instalada por Sistema
Pizza + barras horizontais: Motriz (55%), Climatização (30%), Refrigeração (10%).

### 4. Distribuição por Centro de Custo
Parque aquático concentra 56% da capacidade instalada — referencial para rateio de custos gerenciais.

### 5. Status Operacional dos Motores
28% acima da capacidade (risco de falha e desperdício), 25% subdimensionados.

### 6. Energia Reativa e Multas
Fator de potência médio 0,83 vs limite 0,92 — R$ 58.243,58 em penalidades evitáveis.

---

## 🚀 Como Executar

```bash
git clone https://github.com/ksdsil/energy-etl-entertainment.git
cd energy-etl-entertainment
pip install -r requirements.txt
python src/generate_data.py
python src/etl_pipeline.py
python src/analysis.py
```

---

## 💡 Diferenciais Técnicos

- **Análise de regressão com SciPy**: implementação do protocolo IPMVP com teste de 3 hipóteses estatísticas
- **Descoberta contra-intuitiva**: consumo climático > consumo por visitantes em empresa de entretenimento
- **Distribuição por centro de custo**: modelagem gerencial que vai além da análise técnica
- **Setor diferenciado**: entretenimento/turismo com sazonalidade climática marcante

---

## 🔍 Contexto do Projeto Original

Estudo conduzido em parque aquático de grande porte (dados anonimizados), com coleta presencial de campo durante 4 semanas, envolvendo:
- Levantamento de 40+ motores e bombas industriais
- Análise de 12 meses de faturas de energia (ano base pré-pandemia: 2019)
- Dados climáticos oficiais do INMET
- Dados de frequência de visitantes e hóspedes
- Distribuição de custos por 6 centros de custo gerenciais

> ⚠️ *Dados sintéticos baseados na estrutura e proporções reais do estudo. Nome do parque e valores exatos foram anonimizados por confidencialidade.*

---

## 🔗 Projetos Relacionados

- [energy-etl-pipeline](https://github.com/ksdsil/energy-etl-pipeline) — Estudo similar em indústria de laticínios (setor alimentício)

---

## 👤 Autor

**Alexsander Silva**
Analista de Dados | ETL | Python | SQL | Power BI | Eficiência Energética Industrial

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Alexsander_Silva-blue?logo=linkedin)](https://linkedin.com/in/alexsandersilva)
[![GitHub](https://img.shields.io/badge/GitHub-ksdsil-black?logo=github)](https://github.com/ksdsil)

---

*Key skills: Data Analysis | ETL Pipeline | Statistical Regression | IPMVP Protocol | ISO 50001 | Energy Efficiency | Python | Pandas | SciPy | SQLite | Industrial IoT*
