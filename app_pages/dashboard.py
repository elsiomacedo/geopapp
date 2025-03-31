import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from components import titulo_page

@st.cache_data

def carregar_dados():
    df = pd.read_csv("dados/DBCorretivas.csv")
    df['min_Atendimento'] = df['Atendimento'].apply(tempo_para_minutos)
    df['min_Solucao'] = df['Solução'].apply(tempo_para_minutos)
    df['min_Execucao'] = df['Execução'].apply(tempo_para_minutos)
    return df

def tempo_para_minutos(valor):
    if pd.isnull(valor):
        return None
    try:
        h, m = map(int, valor.split(":"))
        return h * 60 + m
    except:
        return None


def dashboard(): 
    st.markdown(titulo_page('Dashboard', 'Análise por AI'), unsafe_allow_html=True)

    df = carregar_dados()

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de OS", len(df))
    col2.metric("Atendidas", (df["STATUS"] == "ATENDIDO").sum())
    col3.metric("Pendentes", (df["STATUS"] != "ATENDIDO").sum())
    col4.metric("Taxa de Conclusão", f"{(df['STATUS'] == 'ATENDIDO').mean()*100:.2f}%")

    # Tempos Médios
    st.subheader("⏱️ Tempos Médios (em horas)")
    temp_cols = st.columns(3)
    temp_cols[0].metric("Atendimento", f"{df['min_Atendimento'].mean()/60:.1f} h")
    temp_cols[1].metric("Solução", f"{df['min_Solucao'].mean()/60:.1f} h")
    temp_cols[2].metric("Execução", f"{df['min_Execucao'].mean()/60:.1f} h")

    # Gráficos de Distribuição
    st.subheader("📌 Distribuição de OS")
    graf_cols = st.columns(2)

    with graf_cols[0]:
        status_counts = df['STATUS'].value_counts()
        fig1, ax1 = plt.subplots()
        ax1.pie(status_counts, labels=status_counts.index, autopct="%1.1f%%", startangle=90)
        ax1.axis('equal')
        st.pyplot(fig1)

    with graf_cols[1]:
        tipo_counts = df['TIPO DE OS'].value_counts()
        fig2, ax2 = plt.subplots()
        ax2.bar(tipo_counts.index, tipo_counts.values)
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig2)

    # Técnicos mais atuantes
    st.subheader("🏆 Técnicos com mais OS atendidas")
    df_tecnicos = df[df['STATUS'] == 'ATENDIDO'].copy()
    df_tecnicos['TECNICO'] = df_tecnicos['TECNICO'].fillna("")
    top_tecnicos = df_tecnicos['TECNICO'].str.split(", ").explode().value_counts().head(10)

    st.bar_chart(top_tecnicos)

st.caption("Fonte: dados/DBCorretivas.csv")        
if __name__ == "__page__":
    dashboard()






