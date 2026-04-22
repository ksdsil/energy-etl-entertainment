"""
etl_pipeline.py
Pipeline ETL: Extração → Transformação → Carga
Projeto: Estudo de Eficiência Energética — Parque de Entretenimento Aquático
Protocolo: IPMVP 2012 / ABNT NBR ISO 50001
Autor: Alexsander Silva | github.com/ksdsil
"""

import pandas as pd
import numpy as np
import sqlite3
import os
from datetime import datetime
from scipy import stats

DB_PATH = "data/processed/energia_parque.db"

# ══════════════════════════════════════════
# EXTRACT
# ══════════════════════════════════════════
def extract():
    print("🔵 [EXTRACT] Carregando arquivos CSV...")
    dfs = {
        "temperatura":   pd.read_csv("data/raw/temperaturas_regionais.csv",  parse_dates=["mes"]),
        "visitantes":    pd.read_csv("data/raw/producao_visitantes.csv",      parse_dates=["mes"]),
        "energia":       pd.read_csv("data/raw/consumo_energia.csv",          parse_dates=["mes"]),
        "capacidade":    pd.read_csv("data/raw/capacidade_instalada.csv"),
        "centros_custo": pd.read_csv("data/raw/centros_de_custo.csv"),
        "motores":       pd.read_csv("data/raw/inventario_motores.csv"),
        "reativa":       pd.read_csv("data/raw/energia_reativa.csv",          parse_dates=["mes"]),
    }
    for nome, df in dfs.items():
        print(f"   ✅ {nome}: {len(df)} registros")
    return dfs

# ══════════════════════════════════════════
# TRANSFORM
# ══════════════════════════════════════════
def transform(dfs):
    print("\n🟡 [TRANSFORM] Calculando KPIs e análises estatísticas...")

    # ── Tabela fato principal
    fato = (
        dfs["energia"]
        .merge(dfs["temperatura"], on=["mes","mes_label"])
        .merge(dfs["visitantes"],  on=["mes","mes_label"])
        .merge(dfs["reativa"][["mes","fator_potencia","multa_r$","multa_acumulada_r$"]], on="mes")
    )

    # ── KPIs energéticos
    fato["kwh_por_visitante"]    = round(fato["consumo_kwh"] / fato["total_atendidos"], 4)
    fato["custo_r$_por_visitante"] = round(fato["kwh_por_visitante"] * 0.22, 4)  # tarifa ~R$0,22/kWh
    fato["mwh_mes"]              = round(fato["consumo_kwh"] / 1000, 2)

    # ── ANÁLISE DE REGRESSÃO — 3 relações (protocolo IPMVP)

    # Relação 1: Energia x Visitantes
    x1 = fato["total_atendidos"].values
    y  = fato["consumo_kwh"].values
    slope1, intercept1, r1, p1, _ = stats.linregress(x1, y)
    r2_visitantes = round(r1**2, 4)

    # Relação 2: Energia x Dias acima de 23°C
    x2 = fato["dias_acima_23c"].values
    slope2, intercept2, r2, p2, _ = stats.linregress(x2, y)
    r2_acima23 = round(r2**2, 4)

    # Relação 3: Energia x Dias acima de 20°C ← DETERMINANTE (R²>0.75)
    x3 = fato["dias_acima_20c"].values
    slope3, intercept3, r3, p3, _ = stats.linregress(x3, y)
    r2_acima20 = round(r3**2, 4)

    fato["r2_energia_x_visitantes"] = r2_visitantes
    fato["r2_energia_x_dias23c"]    = r2_acima23
    fato["r2_energia_x_dias20c"]    = r2_acima20
    fato["linha_base_prevista_kwh"] = np.round(intercept3 + slope3 * x3, 0)

    print(f"   📊 R² Energia × Visitantes:      {r2_visitantes} (ref. mín. 0.75) {'✅' if r2_visitantes>=0.75 else '❌'}")
    print(f"   📊 R² Energia × Dias >23°C:      {r2_acima23}  (ref. mín. 0.75) {'✅' if r2_acima23>=0.75 else '❌'}")
    print(f"   📊 R² Energia × Dias >20°C:      {r2_acima20}  (ref. mín. 0.75) {'✅' if r2_acima20>=0.75 else '❌'}")
    print(f"   🎯 DETERMINANTE: Temperatura >20°C (DNA do consumo identificado)")

    # ── Data Quality
    nulos = fato.isnull().sum().sum()
    print(f"   🔍 Data Quality — valores nulos: {nulos}")

    # ── KPIs motores
    motores = dfs["motores"].copy()
    status_resumo = motores["status_operacional"].value_counts().reset_index()
    status_resumo.columns = ["status", "quantidade"]
    status_resumo["percentual"] = round(status_resumo["quantidade"] / len(motores) * 100, 1)

    # ── Resumo financeiro
    total_multas = dfs["reativa"]["multa_r$"].sum()
    kwh_medio    = fato["kwh_por_visitante"].mean()
    custo_medio  = fato["custo_r$_por_visitante"].mean()

    print(f"\n   💰 Total multas energia reativa: R$ {total_multas:,.2f}")
    print(f"   👤 Média energética por visitante: {kwh_medio:.2f} kWh")
    print(f"   💵 Custo médio por visitante: R$ {custo_medio:.2f}")

    return {
        "fato_mensal":   fato,
        "capacidade":    dfs["capacidade"],
        "centros_custo": dfs["centros_custo"],
        "motores":       motores,
        "status_motores":status_resumo,
        "reativa":       dfs["reativa"],
    }

# ══════════════════════════════════════════
# LOAD → SQLite
# ══════════════════════════════════════════
def load(tabelas):
    print(f"\n🟢 [LOAD] Carregando dados em SQLite: {DB_PATH}")
    os.makedirs("data/processed", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    for nome, df in tabelas.items():
        df_save = df.copy()
        for col in df_save.select_dtypes(include=["datetime64[ns]"]).columns:
            df_save[col] = df_save[col].astype(str)
        df_save.to_sql(nome, conn, if_exists="replace", index=False)
        print(f"   ✅ Tabela '{nome}' — {len(df_save)} registros")

    conn.close()
    print(f"\n✅ Pipeline concluído: {DB_PATH}")

# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("  ETL Pipeline — Eficiência Energética Parque Aquático")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    raw   = extract()
    trans = transform(raw)
    load(trans)
