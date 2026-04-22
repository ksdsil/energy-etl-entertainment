"""
analysis.py
Análise Exploratória + Visualizações
Projeto: Estudo de Eficiência Energética — Parque de Entretenimento Aquático
Autor: Alexsander Silva | github.com/ksdsil
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import sqlite3
import os
from scipy import stats

DB_PATH  = "data/processed/energia_parque.db"
OUT_PATH = "outputs/"
os.makedirs(OUT_PATH, exist_ok=True)

AZUL    = "#1A3A6B"
VERDE   = "#1E6B3A"
LARANJA = "#C05A00"
CINZA   = "#5A5A5A"
AMARELO = "#C09000"
CIANO   = "#0088AA"

def load_db():
    conn = sqlite3.connect(DB_PATH)
    fato    = pd.read_sql("SELECT * FROM fato_mensal",    conn)
    cap     = pd.read_sql("SELECT * FROM capacidade",     conn)
    cc      = pd.read_sql("SELECT * FROM centros_custo",  conn)
    motores = pd.read_sql("SELECT * FROM motores",        conn)
    st_mot  = pd.read_sql("SELECT * FROM status_motores", conn)
    reativa = pd.read_sql("SELECT * FROM reativa",        conn)
    conn.close()
    return fato, cap, cc, motores, st_mot, reativa

# ──────────────────────────────────────────────
# GRÁFICO 1 — Consumo vs Visitantes vs Temperatura
# ──────────────────────────────────────────────
def plot_consumo_vs_variaveis(fato):
    fig, ax1 = plt.subplots(figsize=(13, 5))
    x = range(len(fato))

    ax1.plot(x, fato["mwh_mes"], color=LARANJA, lw=2.5, marker="o", ms=6, label="Consumo (MWh)")
    ax1.set_ylabel("Consumo (MWh)", color=LARANJA, fontsize=10)
    ax1.tick_params(axis="y", labelcolor=LARANJA)

    ax2 = ax1.twinx()
    ax2.bar(x, fato["total_atendidos"], alpha=0.2, color=AZUL, label="Visitantes + Hóspedes")
    ax2.set_ylabel("Total Atendidos", color=AZUL, fontsize=10)
    ax2.tick_params(axis="y", labelcolor=AZUL)

    ax3 = ax1.twinx()
    ax3.spines["right"].set_position(("outward", 60))
    ax3.plot(x, fato["temp_media_c"], color=VERDE, lw=2, ls="--", marker="s", ms=4, label="Temp. média °C")
    ax3.set_ylabel("Temperatura °C", color=VERDE, fontsize=10)
    ax3.tick_params(axis="y", labelcolor=VERDE)

    ax1.set_xticks(x)
    ax1.set_xticklabels(fato["mes_label"], rotation=45, ha="right", fontsize=8)
    ax1.set_title("Consumo de Energia × Visitantes × Temperatura\nParque Aquático — Ano Base 2019",
                  fontsize=11, fontweight="bold")

    patches = [
        mpatches.Patch(color=LARANJA, label="Consumo (MWh)"),
        mpatches.Patch(color=AZUL,    label="Total atendidos"),
        mpatches.Patch(color=VERDE,   label="Temp. média °C"),
    ]
    ax1.legend(handles=patches, loc="upper left", fontsize=8)
    plt.tight_layout()
    plt.savefig(f"{OUT_PATH}01_consumo_visitantes_temperatura.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("✅ Gráfico 1 salvo")

# ──────────────────────────────────────────────
# GRÁFICO 2 — 3 Regressões IPMVP lado a lado
# ──────────────────────────────────────────────
def plot_regressoes_ipmvp(fato):
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    y = fato["consumo_kwh"].values

    pares = [
        ("total_atendidos",  "Visitantes + Hóspedes",    fato["r2_energia_x_visitantes"].iloc[0], AZUL),
        ("dias_acima_23c",   "Dias com temp. >23°C",     fato["r2_energia_x_dias23c"].iloc[0],    CINZA),
        ("dias_acima_20c",   "Dias com temp. >20°C ✅",   fato["r2_energia_x_dias20c"].iloc[0],    VERDE),
    ]

    for ax, (col, xlabel, r2, cor) in zip(axes, pares):
        x = fato[col].values
        slope, intercept, *_ = stats.linregress(x, y)
        x_line = np.linspace(x.min(), x.max(), 100)
        y_line = intercept + slope * x_line

        ax.scatter(x, y/1000, color=cor, s=60, zorder=5, alpha=0.8)
        ax.plot(x_line, y_line/1000, color=cor, lw=2, ls="--")
        ax.set_xlabel(xlabel, fontsize=9)
        ax.set_ylabel("Consumo (MWh)" if ax == axes[0] else "", fontsize=9)

        cor_r2 = VERDE if r2 >= 0.75 else LARANJA
        ax.annotate(f"R² = {r2}", xy=(0.05, 0.90), xycoords="axes fraction",
                    fontsize=11, fontweight="bold", color=cor_r2,
                    bbox=dict(boxstyle="round", fc="white", alpha=0.8))

        status = "✅ DETERMINANTE" if r2 >= 0.75 else "❌ Descartado"
        ax.set_title(f"{status}", fontsize=9, color=cor_r2, fontweight="bold")
        ax.grid(alpha=0.3)

    fig.suptitle("Análise IPMVP: Busca pelo DNA de Consumo Energético\n"
                 "Mínimo aceitável: R² ≥ 0,75",
                 fontsize=11, fontweight="bold")
    plt.tight_layout()
    plt.savefig(f"{OUT_PATH}02_regressoes_ipmvp.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("✅ Gráfico 2 salvo")

# ──────────────────────────────────────────────
# GRÁFICO 3 — Capacidade instalada por sistema
# ──────────────────────────────────────────────
def plot_capacidade_instalada(cap):
    cap_plot = cap[cap["potencia_kw"] > 0]
    cores = [AZUL, VERDE, LARANJA, CIANO]

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    wedges, texts, autotexts = axes[0].pie(
        cap_plot["percentual_capacidade"],
        labels=cap_plot["sistema"],
        autopct="%1.0f%%",
        colors=cores,
        startangle=140,
        textprops={"fontsize": 9}
    )
    for at in autotexts:
        at.set_fontweight("bold")
        at.set_color("white")
    axes[0].set_title("Capacidade Instalada por Sistema\n(Total: 703,27 kW)", fontweight="bold")

    bars = axes[1].barh(cap_plot["sistema"], cap_plot["potencia_kw"], color=cores)
    for bar, val in zip(bars, cap_plot["potencia_kw"]):
        axes[1].text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2,
                     f"{val:.1f} kW", va="center", fontsize=9)
    axes[1].set_xlabel("Potência (kW)")
    axes[1].set_title("Potência por Sistema (kW)", fontweight="bold")
    axes[1].grid(axis="x", alpha=0.3)

    plt.suptitle("Inventário de Capacidade Instalada — 5 Sistemas", fontsize=11, fontweight="bold")
    plt.tight_layout()
    plt.savefig(f"{OUT_PATH}03_capacidade_instalada.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("✅ Gráfico 3 salvo")

# ──────────────────────────────────────────────
# GRÁFICO 4 — Centros de custo
# ──────────────────────────────────────────────
def plot_centros_custo(cc):
    cc_plot = cc[cc["percentual"] > 0].sort_values("percentual", ascending=True)
    cores = [AZUL, CIANO, VERDE, LARANJA, AMARELO]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(cc_plot["centro_custo"], cc_plot["percentual"], color=cores)
    for bar, val, kw in zip(bars, cc_plot["percentual"], cc_plot["potencia_kw"]):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                f"{val:.0f}% — {kw:.1f} kW", va="center", fontsize=9)

    ax.set_xlabel("% da Capacidade Instalada")
    ax.set_title("Distribuição por Centro de Custo\n"
                 "Parque Aquático responde por 56% da capacidade instalada",
                 fontsize=11, fontweight="bold")
    ax.set_xlim(0, 75)
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUT_PATH}04_centros_de_custo.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("✅ Gráfico 4 salvo")

# ──────────────────────────────────────────────
# GRÁFICO 5 — Status dos motores
# ──────────────────────────────────────────────
def plot_status_motores(motores):
    status_counts = motores["status_operacional"].value_counts()
    cores_status  = {
        "Acima da capacidade nominal":  LARANJA,
        "Abaixo da capacidade nominal": AMARELO,
        "Dentro da capacidade nominal": VERDE,
    }
    cores = [cores_status.get(s, CINZA) for s in status_counts.index]

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    axes[0].pie(status_counts.values, labels=status_counts.index,
                autopct="%1.0f%%", colors=cores, startangle=90,
                textprops={"fontsize": 8})
    axes[0].set_title("Status Operacional dos Motores/Bombas", fontweight="bold")

    # Potência por ambiente
    pot_amb = motores.groupby("ambiente")["potencia_kw"].sum().sort_values()
    axes[1].barh(pot_amb.index, pot_amb.values, color=AZUL, alpha=0.8)
    for i, v in enumerate(pot_amb.values):
        axes[1].text(v + 1, i, f"{v:.1f} kW", va="center", fontsize=8)
    axes[1].set_title("Potência Total por Ambiente", fontweight="bold")
    axes[1].set_xlabel("kW total")
    axes[1].grid(axis="x", alpha=0.3)

    plt.suptitle("Sistema Motriz: 28% acima da capacidade — risco de sobrecarga e desperdício",
                 fontsize=10, fontweight="bold", color=LARANJA)
    plt.tight_layout()
    plt.savefig(f"{OUT_PATH}05_status_motores.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("✅ Gráfico 5 salvo")

# ──────────────────────────────────────────────
# GRÁFICO 6 — Energia reativa e multas
# ──────────────────────────────────────────────
def plot_energia_reativa(reativa):
    fig, ax1 = plt.subplots(figsize=(13, 5))
    x = range(len(reativa))

    ax1.bar(x, reativa["multa_r$"], color=LARANJA, alpha=0.7, label="Multa mensal (R$)")
    ax1.plot(x, reativa["multa_acumulada_r$"], color=AZUL, lw=2.5,
             marker="D", ms=5, label="Multa acumulada (R$)")
    ax1.set_ylabel("R$", fontsize=10)

    ax2 = ax1.twinx()
    ax2.plot(x, reativa["fator_potencia"], color=VERDE, lw=2.5,
             marker="o", ms=5, label="Fator de potência")
    ax2.axhline(y=0.92, color=CINZA, lw=1.5, ls="--", label="Limite sem multa: 0,92")
    ax2.set_ylabel("Fator de Potência", color=VERDE, fontsize=10)
    ax2.set_ylim(0.75, 1.0)
    ax2.tick_params(axis="y", labelcolor=VERDE)

    total = reativa["multa_r$"].sum()
    ax1.annotate(f"Total período:\nR$ {total:,.2f}",
                 xy=(8, reativa["multa_r$"].max() * 0.85),
                 fontsize=9, bbox=dict(boxstyle="round", fc=AMARELO, alpha=0.9))

    ax1.set_xticks(x)
    ax1.set_xticklabels(reativa["mes_label"], rotation=45, ha="right", fontsize=8)
    ax1.set_title("Perdas com Energia Reativa — R$ 58.243,58 no período\n"
                  "Fator de potência médio: 0,83 (limite sem multa: 0,92)",
                  fontsize=11, fontweight="bold")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=8)
    plt.tight_layout()
    plt.savefig(f"{OUT_PATH}06_energia_reativa_multas.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("✅ Gráfico 6 salvo")

# ──────────────────────────────────────────────
# RESUMO EXECUTIVO
# ──────────────────────────────────────────────
def print_kpis(fato, reativa):
    print("\n" + "═"*60)
    print("  RESUMO EXECUTIVO — KPIs DO PROJETO")
    print("═"*60)
    print(f"  Capacidade instalada total:        703,27 kW")
    print(f"  Consumo médio mensal (2019):        {fato['consumo_kwh'].mean()/1000:.1f} MWh")
    print(f"  DNA do consumo identificado:        Temperatura > 20°C")
    print(f"  R² Temperatura >20°C × Consumo:    {fato['r2_energia_x_dias20c'].iloc[0]} ✅")
    print(f"  R² Visitantes × Consumo:            {fato['r2_energia_x_visitantes'].iloc[0]} ❌")
    print(f"  Média kWh por visitante:            {fato['kwh_por_visitante'].mean():.2f} kWh")
    print(f"  Custo médio por visitante:          R$ {fato['custo_r$_por_visitante'].mean():.2f}")
    print(f"  Perdas energia reativa (período):   R$ {reativa['multa_r$'].sum():,.2f}")
    print(f"  Motores acima da capacidade:        28%")
    print(f"  Motores abaixo da capacidade:       25%")
    print("═"*60)

if __name__ == "__main__":
    fato, cap, cc, motores, st_mot, reativa = load_db()
    plot_consumo_vs_variaveis(fato)
    plot_regressoes_ipmvp(fato)
    plot_capacidade_instalada(cap)
    plot_centros_custo(cc)
    plot_status_motores(motores)
    plot_energia_reativa(reativa)
    print_kpis(fato, reativa)
    print(f"\n✅ Todos os gráficos salvos em: {OUT_PATH}")
