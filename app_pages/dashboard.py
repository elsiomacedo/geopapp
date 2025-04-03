import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards 
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from components import titulo_page
from metricas import metricascorretivas

@st.cache_data
def carrega():
    # Definir o caminho do arquivo CSV
    csv_path = "dados/DBCorretivas.csv"
    return pd.read_csv(csv_path)    

def dashboard(df):
    st.markdown(titulo_page('Dashborad', 'Acompanhamento de Indicadores'), unsafe_allow_html=True)
 

    metricas_df = metricascorretivas(df)

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
      
    #st.write("### Evolução Mensal")

    col1, col2 = st.columns(2)
    with col1:    
        #st.write("### OS Abertas vs OS Atendidas")
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Define a largura das barras
        bar_width = 0.2
        
        # Define as posições das barras no eixo X
        r1 = np.arange(len(metricas_df['Referência']))  # Posições para as barras de OS Abertas
        r2 = [x + bar_width for x in r1]  # Posições para as barras de OS Atendidas (deslocadas)
        r3 = [x + bar_width for x in r2]  # Posições para as barras de OS Atendidas (deslocadas)        
        r4 = [x + bar_width for x in r3]  # Posições para as barras de OS Atendidas (deslocadas)           

        # Cria as barras para OS Abertas e OS Atendidas
        bars1 = ax.bar(r1, metricas_df['OS Abertas'], width=bar_width, label='Abertas', color='blue', alpha=0.7)
        bars2 = ax.bar(r2, metricas_df['OS Atendidas'], width=bar_width, label='Atendidas', color='green', alpha=0.7)
        bars3 = ax.bar(r3, metricas_df['OS Não Atendidas'], width=bar_width, label='Não Atendidas', color='orange', alpha=0.7)
        bars4 = ax.bar(r4, metricas_df['Backlogs'], width=bar_width, label='Backlogs', color='red', alpha=0.7)
        
        # Função para adicionar os rótulos
        def adicionar_rotulos(barras):
            for bar in barras:
                altura = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, altura + 0.5, f'{int(altura)}', 
                        ha='center', va='bottom', fontsize=8)

        adicionar_rotulos(bars1)
        adicionar_rotulos(bars2)
        adicionar_rotulos(bars3)
        adicionar_rotulos(bars4)


        # Configurações do gráfico
        ax.set_xlabel('Referência (Ano-Mês)')
        ax.set_ylabel('Quantidade')
        ax.set_title('Evolução de Atendimento')
        ax.set_xticks([r + bar_width  for r in range(len(metricas_df['Referência']))])  # Centraliza os rótulos no eixo X
        ax.set_xticklabels(metricas_df['Referência'])
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Exibe o gráfico no Streamlit
        st.pyplot(fig)
    with col2:    
        #st.write("### OS Abertas vs OS Atendidas")
        fig, ax = plt.subplots(figsize=(10, 6))

        # Define as posições no eixo X
        x = np.arange(len(metricas_df['Referência']))

        # Cria as linhas para cada métrica
        ax.plot(x, metricas_df['OS Abertas'], marker='o', label='Abertas', color='blue')
        ax.plot(x, metricas_df['OS Atendidas'], marker='o', label='Atendidas', color='green')
        ax.plot(x, metricas_df['OS Não Atendidas'], marker='o', label='Não Atendidas', color='orange')
        ax.plot(x, metricas_df['Backlogs'], marker='o', label='Backlogs', color='red')

        # Adiciona rótulos de dados nos pontos
        def adicionar_rotulos_linha(x_vals, y_vals):
            for i, y in enumerate(y_vals):
                ax.text(x_vals[i], y + 0.5, f'{int(y)}', ha='center', va='bottom', fontsize=8)

        adicionar_rotulos_linha(x, metricas_df['OS Abertas'])
        adicionar_rotulos_linha(x, metricas_df['OS Atendidas'])
        adicionar_rotulos_linha(x, metricas_df['OS Não Atendidas'])
        adicionar_rotulos_linha(x, metricas_df['Backlogs'])

        # Configurações do gráfico
        ax.set_xlabel('Referência (Ano-Mês)')
        ax.set_ylabel('Quantidade')
        ax.set_title('OS Abertas vs OS Atendidas (Gráfico de Linha)')
        ax.set_xticks(x)
        ax.set_xticklabels(metricas_df['Referência'], rotation=45)
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        # Exibe o gráfico no Streamlit
        st.pyplot(fig)

if __name__ == "__page__":
    df = carrega()
    dashboard(df)






