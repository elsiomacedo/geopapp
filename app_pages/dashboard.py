import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards 
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
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


def dashboard_old(): 
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

def dashboard():
    csv_metricas = 'dados/DBMetricasCorretivas.csv'    
    metricas_df = pd.read_csv(csv_metricas, encoding='utf-8')


    referencia_atual = "2025-04"  # Exemplo de referência atual
    ano_atual = int(referencia_atual.split("-")[0])  # Extrai o ano
    mes_atual = int(referencia_atual.split("-")[1])  # Extrai o mês

    # Filtra o DataFrame para exibir apenas a referência atual
    referencia_atual_df = metricas_df[metricas_df['Referência'] == referencia_atual]
    #st.dataframe(referencia_atual_df, use_container_width=True, hide_index=True)

    # Ajusta o mês e ano anterior se o mês atual for janeiro
    if mes_atual == 1:
        mes_anterior = 12
        ano_anterior = ano_atual - 1
    else:
        mes_anterior = mes_atual - 1
        ano_anterior = ano_atual

 # Cria a referência anterior no formato "YYYY-MM"
    referencia_anterior = f"{ano_anterior}-{mes_anterior:02d}"
    print(referencia_anterior)

    # Obtém o valor da métrica para o ano e mês específicos
    os_abertas_atual = metricas_df[metricas_df['Referência'] == referencia_atual]['OS Abertas'].values[0]
    os_abertas_ant = metricas_df[metricas_df['Referência'] == referencia_anterior]['OS Abertas'].values[0]

    os_nat_mes_atual = metricas_df[metricas_df['Referência'] == referencia_atual]['OS Não Atendidas'].values[0]
    os_nat_mes_ant = metricas_df[metricas_df['Referência'] == referencia_anterior]['OS Não Atendidas'].values[0]

    os_at_mes_atual = metricas_df[metricas_df['Referência'] == referencia_atual]['OS Atendidas'].values[0]
    os_at_mes_ant = metricas_df[metricas_df['Referência'] == referencia_anterior]['OS Atendidas'].values[0]

    os_at_backlog_atual = metricas_df[metricas_df['Referência'] == referencia_atual]['Backlogs Atendidos'].values[0]
    os_at_backlog_ant = metricas_df[metricas_df['Referência'] == referencia_anterior]['Backlogs Atendidos'].values[0]

    backlog_atual = metricas_df[metricas_df['Referência'] == referencia_atual]['Backlogs'].values[0]
    backlog_ant = metricas_df[metricas_df['Referência'] == referencia_anterior]['Backlogs'].values[0]

    # Exibe métricas utilizando colunas
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(label="Backlogs", value=backlog_atual, delta=int(backlog_atual - backlog_ant))    
    col2.metric(label="OS Abertas no Mês", value=os_abertas_atual, delta=int(os_abertas_atual - os_abertas_ant))
    col3.metric(label="OS Não Atendidas no Mês", value=os_nat_mes_atual, delta=int(os_nat_mes_atual - os_nat_mes_ant))    
    col4.metric(label="OS Atendidas do Mês", value=os_at_mes_atual, delta=int(os_at_mes_atual - os_at_mes_ant))    
    col5.metric(label="Backlogs Atendidos", value=os_at_backlog_atual, delta=int(os_at_backlog_atual - os_at_backlog_ant))   

    style_metric_cards()
      
    st.write("### Dados Mensais")

    col1, col2 = st.columns(2)
    with col1:    
        # Criar o gráfico de barras
        st.write("### Gráfico de OS Abertas vs OS Atendidas")
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(metricas_df['Referência'], metricas_df['OS Abertas'], label='OS Abertas', color='blue', alpha=0.7)
        ax.bar(metricas_df['Referência'], metricas_df['OS Atendidas'], label='OS Atendidas', color='green', alpha=0.7)
        ax.set_xlabel('Referência (Ano-Mês)')
        ax.set_ylabel('Quantidade')
        ax.set_title('OS Abertas vs OS Atendidas')
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        # Exibir o gráfico no Streamlit
        st.pyplot(fig)
    with col2:    
        st.write("### OS Abertas vs OS Atendidas")
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Define a largura das barras
        bar_width = 0.35
        
        # Define as posições das barras no eixo X
        r1 = np.arange(len(metricas_df['Referência']))  # Posições para as barras de OS Abertas
        r2 = [x + bar_width for x in r1]  # Posições para as barras de OS Atendidas (deslocadas)
        
        # Cria as barras para OS Abertas e OS Atendidas
        ax.bar(r1, metricas_df['OS Abertas'], width=bar_width, label='OS Abertas', color='blue', alpha=0.7)
        ax.bar(r2, metricas_df['OS Atendidas'], width=bar_width, label='OS Atendidas', color='green', alpha=0.7)
        
        # Configurações do gráfico
        ax.set_xlabel('Referência (Ano-Mês)')
        ax.set_ylabel('Quantidade')
        ax.set_title('OS Abertas vs OS Atendidas')
        ax.set_xticks([r + bar_width / 2 for r in range(len(metricas_df['Referência']))])  # Centraliza os rótulos no eixo X
        ax.set_xticklabels(metricas_df['Referência'])
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Exibe o gráfico no Streamlit
        st.pyplot(fig)

if __name__ == "__page__":
    dashboard()






