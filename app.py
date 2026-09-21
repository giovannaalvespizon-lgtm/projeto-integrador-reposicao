from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px


st.set_page_config(
    page_title="Dashboard - Sinalização Ferroviária",
    page_icon="🚆",
    layout="wide"
)


st.title("🚆 Dashboard de Análise de Sinalização Ferroviária")
st.markdown("""
Este painel interativo analisa os dados de operação ferroviária comparando sistemas de **Bloco Fixo** e **CBTC (Bloco Móvel)**, 
explorando métricas de *headway*, velocidade permitida e tempo de ocupação dos blocos.
""")



DIRETORIO_APP = Path(__file__).resolve().parent
CAMINHO_CSV = DIRETORIO_APP / "dataset_sinalizacao_ferroviaria.csv"


@st.cache_data
def carregar_dados(caminho_csv: str):
    """Carrega o dataset usando um caminho absoluto baseado na localização do app."""
    caminho = Path(caminho_csv)

    if not caminho.is_file():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    return pd.read_csv(caminho)


try:
    df = carregar_dados(str(CAMINHO_CSV))
except FileNotFoundError as erro:
    st.error(
        "Não foi possível carregar o dataset. "
        "Verifique se 'dataset_sinalizacao_ferroviaria.csv' está na mesma pasta de app.py."
    )
    st.stop()
except Exception as erro:
    st.error(f"Erro ao carregar o dataset: {erro}")
    st.stop()


st.sidebar.header("Filtros de Análise")
tipos_sinal = st.sidebar.multiselect(
    "Selecione o Tipo de Sinalização:",
    options=df["tipo_sinalizacao"].unique(),
    default=df["tipo_sinalizacao"].unique()
)

aspectos = st.sidebar.multiselect(
    "Selecione o Aspecto do Sinal:",
    options=df["aspecto_sinal"].unique(),
    default=df["aspecto_sinal"].unique()
)


df_filtrado = df[
    (df["tipo_sinalizacao"].isin(tipos_sinal)) & 
    (df["aspecto_sinal"].isin(aspectos))
]


st.subheader("Visão Geral dos Dados Filtrados")
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total de Registros", len(df_filtrado))
col2.metric("Velocidade Média", f"{df_filtrado['velocidade_permitida_kmh'].mean():.1f} km/h")
col3.metric("Headway Médio", f"{df_filtrado['headway_seg'].mean():.1f} seg")
col4.metric("Tempo Médio de Ocupação", f"{df_filtrado['tempo_ocupacao_circuito_seg'].mean():.1f} seg")

st.divider()


col_g1, col_g2 = st.columns(2)

with col_g1:
    st.subheader("1. Dispersão: Velocidade vs. Tempo de Ocupação")
    st.markdown("Relação inversa esperada: quanto maior a velocidade permitida, menor o tempo de travessia do bloco.")
    fig_disp = px.scatter(
        df_filtrado,
        x="velocidade_permitida_kmh",
        y="tempo_ocupacao_circuito_seg",
        color="tipo_sinalizacao",
        hover_data=["id_trem", "id_bloco", "aspecto_sinal"],
        labels={
            "velocidade_permitida_kmh": "Velocidade Permitida (km/h)",
            "tempo_ocupacao_circuito_seg": "Tempo de Ocupação (seg)"
        }
    )
    st.plotly_chart(fig_disp, use_container_width=True)

with col_g2:
    st.subheader("2. Boxplot: Headway por Tipo de Sinalização")
    st.markdown("Mostra a distribuição dos intervalos (*headways*), evidenciando que o CBTC opera com intervalos menores.")
    fig_box = px.box(
        df_filtrado,
        x="tipo_sinalizacao",
        y="headway_seg",
        color="tipo_sinalizacao",
        labels={
            "tipo_sinalizacao": "Tipo de Sinalização",
            "headway_seg": "Headway (segundos)"
        }
    )
    st.plotly_chart(fig_box, use_container_width=True)

st.divider()


st.subheader("3. Contagem de Aspecto do Sinal por Tipo de Sinalização")
st.markdown("Proporção de sinais Verdes, Amarelos e Vermelhos em cada tecnologia.")

df_contagem = df_filtrado.groupby(["tipo_sinalizacao", "aspecto_sinal"]).size().reset_index(name="quantidade")

fig_bar = px.bar(
    df_contagem,
    x="tipo_sinalizacao",
    y="quantidade",
    color="aspecto_sinal",
    barmode="stack",
    labels={
        "tipo_sinalizacao": "Tipo de Sinalização",
        "quantidade": "Quantidade de Ocorrências",
        "aspecto_sinal": "Aspecto do Sinal"
    }
)
st.plotly_chart(fig_bar, use_container_width=True)


with st.expander("Visualizar tabela de dados brutos"):
    st.dataframe(df_filtrado)
