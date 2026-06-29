"""
Dashboard interactivo — Índices de Provisiones por Riesgo de Crédito
Sistema Bancario Chileno | CMF | 2016–2026
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from pathlib import Path

# ── Configuración de la página ──────────────────────────────────────────────
st.set_page_config(
    page_title="Riesgo de Crédito — Banca Chilena",
    page_icon="🏦",
    layout="wide",
)

DATA_DIR = Path(__file__).parent.parent / "data" / "processed"

TIPOS = {
    "Comercial": "indice_comercial",
    "Consumo":   "indice_consumo",
    "Vivienda":  "indice_vivienda",
}

COVID_START = "2020-03-01"
COVID_END   = "2021-06-01"


# ── Carga de datos ───────────────────────────────────────────────────────────
@st.cache_data
def cargar_datos():
    df_prov = pd.read_csv(DATA_DIR / "provisiones_por_tipo.csv", parse_dates=["fecha"])
    df_cart = pd.read_csv(DATA_DIR / "calidad_cartera.csv",      parse_dates=["fecha"])
    return df_prov, df_cart


df_prov, df_cart = cargar_datos()

# Bancos con al menos 60 meses de datos para no mostrar instituciones fugaces
bancos_validos = (
    df_prov.groupby("banco")["fecha"].count()
    [lambda s: s >= 60]
    .index.tolist()
)
bancos_validos.sort()


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("Filtros")

    bancos_sel = st.multiselect(
        "Bancos",
        options=bancos_validos,
        default=["Banco de Chile", "Banco del Estado de Chile",
                 "Banco Santander-Chile", "Banco de Crédito e Inversiones"],
    )

    anio_min, anio_max = st.slider(
        "Rango de años",
        min_value=2016, max_value=2026,
        value=(2016, 2026),
    )

    tipo_sel = st.selectbox("Tipo de crédito", list(TIPOS.keys()), index=1)
    col_sel  = TIPOS[tipo_sel]

    mostrar_covid = st.toggle("Marcar período COVID", value=True)

    st.divider()
    st.caption("Fuente: CMF — Indicadores de Provisiones por Riesgo de Crédito de Bancos")


# ── Filtrado base ─────────────────────────────────────────────────────────────
df_filtrado = df_prov[
    df_prov["banco"].isin(bancos_sel) &
    (df_prov["fecha"].dt.year >= anio_min) &
    (df_prov["fecha"].dt.year <= anio_max)
].copy()


def agregar_covid(fig):
    """Agrega una banda sombreada para el período COVID si el toggle está activo."""
    if mostrar_covid:
        fig.add_vrect(
            x0=COVID_START, x1=COVID_END,
            fillcolor="red", opacity=0.08,
            layer="below", line_width=0,
            annotation_text="COVID", annotation_position="top left",
        )
    return fig


# ── Header ───────────────────────────────────────────────────────────────────
st.title("Riesgo de Crédito — Sistema Bancario Chileno")
st.markdown("Análisis de índices de provisiones por riesgo de crédito · CMF · 2016–2026")
st.divider()


# ── KPIs ─────────────────────────────────────────────────────────────────────
if bancos_sel and not df_filtrado.empty:
    ult_fecha = df_filtrado["fecha"].max()
    df_ult    = df_filtrado[df_filtrado["fecha"] == ult_fecha]

    st.subheader(f"Último dato disponible — {ult_fecha.strftime('%B %Y')}")
    cols = st.columns(len(bancos_sel))

    for col, banco in zip(cols, bancos_sel):
        fila = df_ult[df_ult["banco"] == banco]
        if not fila.empty:
            val = fila[col_sel].values[0]
            col.metric(label=banco, value=f"{val:.2f}%" if pd.notna(val) else "N/D")

    st.divider()


# ── Vista 1: Evolución del sistema ───────────────────────────────────────────
st.subheader("Evolución del sistema bancario")

df_sistema = (
    df_prov[
        (df_prov["fecha"].dt.year >= anio_min) &
        (df_prov["fecha"].dt.year <= anio_max)
    ]
    .groupby("fecha")[list(TIPOS.values())]
    .mean()
    .reset_index()
)

fig_sistema = go.Figure()
colores = ["#1f77b4", "#ff7f0e", "#2ca02c"]
for (nombre, col), color in zip(TIPOS.items(), colores):
    fig_sistema.add_trace(go.Scatter(
        x=df_sistema["fecha"], y=df_sistema[col],
        name=nombre, line=dict(color=color, width=2),
    ))

fig_sistema = agregar_covid(fig_sistema)
fig_sistema.update_layout(
    xaxis_title="Fecha", yaxis_title="Índice de provisiones (%)",
    legend_title="Tipo de crédito", hovermode="x unified",
    height=380,
)
st.plotly_chart(fig_sistema, use_container_width=True)


# ── Vista 2: Comparativa por banco ───────────────────────────────────────────
st.subheader(f"Comparativa por banco — Crédito {tipo_sel}")

if bancos_sel and not df_filtrado.empty:
    df_lineas = df_filtrado[["fecha", "banco", col_sel]].dropna()
    fig_bancos = px.line(
        df_lineas, x="fecha", y=col_sel, color="banco",
        labels={"fecha": "Fecha", col_sel: "Índice (%)", "banco": "Banco"},
        height=400,
    )
    fig_bancos = agregar_covid(fig_bancos)
    fig_bancos.update_layout(hovermode="x unified", legend_title="Banco")
    st.plotly_chart(fig_bancos, use_container_width=True)
else:
    st.info("Selecciona al menos un banco en el panel izquierdo.")


# ── Vista 3: Heatmap ─────────────────────────────────────────────────────────
st.subheader(f"Heatmap — Índice {tipo_sel} promedio anual por banco")

if bancos_sel:
    df_heat = df_prov[
        df_prov["banco"].isin(bancos_sel) &
        (df_prov["fecha"].dt.year >= anio_min) &
        (df_prov["fecha"].dt.year <= anio_max)
    ].copy()
    df_heat["anio"] = df_heat["fecha"].dt.year

    pivot = (
        df_heat.groupby(["banco", "anio"])[col_sel]
        .mean()
        .unstack()
        .round(2)
    )

    fig_heat = px.imshow(
        pivot,
        color_continuous_scale="YlOrRd",
        labels={"x": "Año", "y": "Banco", "color": "Índice (%)"},
        text_auto=".1f",
        aspect="auto",
        height=max(300, len(bancos_sel) * 50),
    )
    fig_heat.update_layout(coloraxis_colorbar_title="Índice (%)")
    st.plotly_chart(fig_heat, use_container_width=True)


# ── Vista 4: Ranking ─────────────────────────────────────────────────────────
st.subheader(f"Ranking de bancos por índice {tipo_sel} promedio")

df_ranking = (
    df_prov[
        df_prov["banco"].isin(bancos_validos) &
        (df_prov["fecha"].dt.year >= anio_min) &
        (df_prov["fecha"].dt.year <= anio_max)
    ]
    .groupby("banco")[col_sel]
    .mean()
    .dropna()
    .sort_values(ascending=False)
    .reset_index()
    .rename(columns={"banco": "Banco", col_sel: f"Índice {tipo_sel} promedio (%)"})
    .round(2)
)
df_ranking.index += 1

fig_ranking = px.bar(
    df_ranking, x=f"Índice {tipo_sel} promedio (%)", y="Banco",
    orientation="h",
    color=f"Índice {tipo_sel} promedio (%)",
    color_continuous_scale="YlOrRd",
    height=max(350, len(df_ranking) * 35),
    labels={"Banco": ""},
)
fig_ranking.update_layout(
    yaxis=dict(autorange="reversed"),
    coloraxis_showscale=False,
)
st.plotly_chart(fig_ranking, use_container_width=True)

st.divider()

# ── Conclusiones ─────────────────────────────────────────────────────────────
st.subheader("Conclusiones del análisis")

col1, col2 = st.columns(2)

with col1:
    st.info(
        "**COVID dejó una huella permanente**  \n"
        "El índice de consumo del sistema saltó de 2.97% (pre-pandemia) a 4.09% durante 2020–2021. "
        "Post-COVID se estabilizó en ~3.13%, sin volver al nivel previo."
    )
    st.info(
        "**Bancos de retail lideran el riesgo**  \n"
        "Banco Ripley (10.4%) y Banco Falabella (4.0%) tienen los índices de consumo más altos del sistema, "
        "reflejo de su foco en crédito masivo de mayor riesgo."
    )
    st.info(
        "**El crédito hipotecario es el más seguro**  \n"
        "El índice de vivienda se mantiene consistentemente por debajo de consumo y comercial "
        "en todos los años analizados."
    )

with col2:
    st.success(
        "**Banco de Chile y BCI son los más estables**  \n"
        "Con variaciones históricas de solo 0.69 y 0.84 puntos respectivamente en consumo, "
        "son los bancos con la cartera más consistente del período."
    )
    st.success(
        "**Tendencia positiva desde 2025**  \n"
        "El índice de consumo del sistema bajó de 3.33% en 2023 a 2.75% en 2025, "
        "la cifra más baja desde 2016, lo que sugiere normalización del riesgo crediticio."
    )
    st.success(
        "**Convergencia post-fusiones**  \n"
        "La salida de bancos pequeños y fusiones (Corpbanca → Itaú, Scotiabank) redujeron "
        "la dispersión de riesgo entre instituciones, concentrando el sistema."
    )

st.divider()
st.caption(
    "Desarrollado por **Marcelo Adolfo Corro Troncoso** · "
    "Datos: CMF Chile · Indicadores de Provisiones por Riesgo de Crédito  \n"
    "*Este análisis es de carácter académico y fue desarrollado con fines de portafolio profesional. "
    "No constituye asesoría financiera ni representa la opinión de ninguna institución. "
    "Los datos utilizados son de acceso público y provienen de la CMF Chile.*"
)
