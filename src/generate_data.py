"""
generate_data.py
Geração de dados sintéticos — Estudo de Eficiência Energética
Setor: Parque de Entretenimento Aquático (dados anonimizados)
Protocolo: IPMVP 2012 / ABNT NBR ISO 50001
Autor: Alexsander Silva | github.com/ksdsil
"""

import pandas as pd
import numpy as np
import os

np.random.seed(42)
os.makedirs("data/raw", exist_ok=True)

meses = pd.date_range(start="2019-01-01", periods=12, freq="MS")
nomes_meses = ["Jan","Fev","Mar","Abr","Mai","Jun",
               "Jul","Ago","Set","Out","Nov","Dez"]

# ─────────────────────────────────────────────
# 1. TEMPERATURAS REGIONAIS (INMET – Suzano SP)
# ─────────────────────────────────────────────
# Suzano SP: verão quente (~28°C), inverno ameno (~16°C)
temp_media = [27.5, 27.8, 26.4, 23.1, 19.8, 17.2,
              16.4, 17.9, 20.3, 23.6, 25.4, 27.1]

# Dias com temperatura acima de 20°C (determinante do consumo — R²=0.89)
dias_acima_20 = [28, 26, 25, 18, 10, 4,
                 2,  5,  12, 20, 24, 27]

# Dias com temperatura acima de 23°C (acionamento climatização)
dias_acima_23 = [25, 24, 20, 10, 3,  0,
                 0,  1,  5,  12, 18, 22]

df_temp = pd.DataFrame({
    "mes": meses,
    "mes_label": nomes_meses,
    "temp_media_c": temp_media,
    "dias_acima_20c": dias_acima_20,
    "dias_acima_23c": dias_acima_23
})
df_temp.to_csv("data/raw/temperaturas_regionais.csv", index=False)
print("✅ temperaturas_regionais.csv gerado")

# ─────────────────────────────────────────────
# 2. VISITANTES E HÓSPEDES (produção do parque)
# ─────────────────────────────────────────────
# Sazonalidade típica de parque aquático SP:
# pico no verão (jan/fev/dez), baixo no inverno
visitantes = [18500, 17200, 14800, 8200, 4100, 1800,
              1200,  2400,  5600,  9800, 13200, 16900]

hospedes = [2800, 2600, 2100, 980, 420, 180,
            120,  240,  580,  1100, 1800, 2500]

df_prod = pd.DataFrame({
    "mes": meses,
    "mes_label": nomes_meses,
    "visitantes": visitantes,
    "hospedes": hospedes,
    "total_atendidos": [v+h for v,h in zip(visitantes, hospedes)]
})
df_prod.to_csv("data/raw/producao_visitantes.csv", index=False)
print("✅ producao_visitantes.csv gerado")

# ─────────────────────────────────────────────
# 3. CONSUMO DE ENERGIA (kWh/mês) — ano base 2019
# ─────────────────────────────────────────────
# DNA do parque: consumo guiado por temperatura >20°C, não por visitantes
# Consumo base fixo (refrigeração contínua) + componente climático
consumo_base = 35000   # kWh/mês fixo (refrigeração)
consumo_kwh = []
for i in range(12):
    componente_climatico = dias_acima_20[i] * 1850  # kWh por dia quente
    componente_visitantes = visitantes[i] * 0.8     # pequena influência
    total = consumo_base + componente_climatico + componente_visitantes
    total = round(total * np.random.uniform(0.97, 1.03))
    consumo_kwh.append(total)

df_energia = pd.DataFrame({
    "mes": meses,
    "mes_label": nomes_meses,
    "consumo_kwh": consumo_kwh
})
df_energia.to_csv("data/raw/consumo_energia.csv", index=False)
print("✅ consumo_energia.csv gerado")

# ─────────────────────────────────────────────
# 4. CAPACIDADE INSTALADA POR SISTEMA (703.27 kW total)
# ─────────────────────────────────────────────
# Distribuição real do relatório:
# Motriz 55%, Climatização 30%, Refrigeração 10%,
# Eletroeletrônicos 5%, Iluminação 0% (LED moderno)
sistemas_cap = {
    "Motriz":           {"pct": 0.55, "kw": 386.80},
    "Climatização":     {"pct": 0.30, "kw": 210.98},
    "Refrigeração":     {"pct": 0.10, "kw":  70.33},
    "Eletroeletrônicos":{"pct": 0.05, "kw":  35.16},
    "Iluminação":       {"pct": 0.00, "kw":   0.00},
}

rows_cap = []
for sistema, dados in sistemas_cap.items():
    rows_cap.append({
        "sistema": sistema,
        "percentual_capacidade": dados["pct"] * 100,
        "potencia_kw": dados["kw"]
    })

df_cap = pd.DataFrame(rows_cap)
df_cap.to_csv("data/raw/capacidade_instalada.csv", index=False)
print("✅ capacidade_instalada.csv gerado")

# ─────────────────────────────────────────────
# 5. DISTRIBUIÇÃO POR CENTRO DE CUSTO
# ─────────────────────────────────────────────
# Baseado na figura 8 do relatório
centros = {
    "Parque Aquático":        0.56,
    "Diretoria Comercial":    0.12,
    "Diretoria ADM/FIN":      0.11,
    "Pousadas":               0.11,
    "Diretoria Operacional":  0.10,
    "Eventos Individuais":    0.00,
}

rows_cc = []
for centro, pct in centros.items():
    kw = round(703.27 * pct, 2)
    rows_cc.append({
        "centro_custo": centro,
        "percentual": pct * 100,
        "potencia_kw": kw
    })

df_cc = pd.DataFrame(rows_cc)
df_cc.to_csv("data/raw/centros_de_custo.csv", index=False)
print("✅ centros_de_custo.csv gerado")

# ─────────────────────────────────────────────
# 6. SISTEMA MOTRIZ — INVENTÁRIO DE BOMBAS/MOTORES
# ─────────────────────────────────────────────
# 28% acima da capacidade, 25% abaixo, 47% adequados
n_motores = 40
n_acima  = int(0.28 * n_motores)
n_abaixo = int(0.25 * n_motores)
n_dentro = n_motores - n_acima - n_abaixo
status_dist = (
    ["Acima da capacidade nominal"] * n_acima +
    ["Abaixo da capacidade nominal"] * n_abaixo +
    ["Dentro da capacidade nominal"] * n_dentro
)
np.random.shuffle(status_dist)

motor_rows = []
for i in range(n_motores):
    pot = round(np.random.choice([0.75, 1.5, 3.0, 5.5, 7.5, 11.0, 15.0,
                                   22.0, 30.0], p=[0.1,0.15,0.2,0.2,0.15,
                                                    0.1,0.05,0.03,0.02]), 2)
    motor_rows.append({
        "motor_id": f"MTR-{i+1:03d}",
        "aplicacao": np.random.choice([
            "Bomba filtragem piscina", "Bomba recirculação",
            "Bomba toboágua", "Bomba câmara fria", "Motor ventilador"
        ]),
        "potencia_kw": pot,
        "status_operacional": status_dist[i],
        "ambiente": np.random.choice([
            "Casa de máquinas", "Área externa", "Câmara fria",
            "Área coberta", "Área úmida/cloro"
        ])
    })

df_motores = pd.DataFrame(motor_rows)
df_motores.to_csv("data/raw/inventario_motores.csv", index=False)
print(f"✅ inventario_motores.csv gerado — {n_motores} motores")

# ─────────────────────────────────────────────
# 7. ENERGIA REATIVA E MULTAS
# ─────────────────────────────────────────────
# Total real: R$ 58.243,58 no período
multa_media_mensal = 58243.58 / 12
fp_mensal = [0.80, 0.81, 0.82, 0.83, 0.84, 0.85,
             0.86, 0.85, 0.83, 0.82, 0.81, 0.80]

multas = [round(multa_media_mensal * np.random.uniform(0.85, 1.15), 2)
          if fp < 0.92 else 0.0 for fp in fp_mensal]

df_reativa = pd.DataFrame({
    "mes": meses,
    "mes_label": nomes_meses,
    "fator_potencia": fp_mensal,
    "multa_r$": multas,
    "multa_acumulada_r$": pd.Series(multas).cumsum().round(2).values
})
df_reativa.to_csv("data/raw/energia_reativa.csv", index=False)
print("✅ energia_reativa.csv gerado")

print(f"\n✅ Todos os datasets gerados em data/raw/")
print(f"   Total capacidade instalada: 703.27 kW")
print(f"   Consumo médio anual: {sum(consumo_kwh)/12:,.0f} kWh/mês")
print(f"   Total multas energia reativa: R$ {sum(multas):,.2f}")
