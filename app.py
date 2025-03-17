import streamlit as st

# Constantes
APP_TITLE = 'Geopapp'
APP_ICON = "imgs/roda.png"
LOGO_PATH = "imgs/roda.png"
SIDEBAR_INIT = "collapsed"    
FILE_XLS = 'historico_oss_corretivas.xls'

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    initial_sidebar_state=SIDEBAR_INIT,
    layout="wide"
)

from utils import header_page, header_side, widget
from datasets.ds_corretivas import load_excel_data, exibir_corretivas, calculo_metricas
from streamlit_extras.metric_cards import style_metric_cards
import matplotlib.pyplot as plt
import numpy as np

def configurar_sidebar():
    """Configura a barra lateral do aplicativo."""
    with st.sidebar:
        st.markdown(header_side, unsafe_allow_html=True)

def exibir_cabecalho():
    """Exibe o cabeçalho da página."""
    st.markdown(header_page, unsafe_allow_html=True)

def exibe_metricas(df):
    """Exibe as métricas calculadas a partir dos dados fornecidos."""
    metricas_df = calculo_metricas(df) 
    
    print(df)
    print(metricas_df)

    referencia_atual = "2025-03"  # Exemplo de referência atual
    ano_atual = int(referencia_atual.split("-")[0])  # Extrai o ano
    mes_atual = int(referencia_atual.split("-")[1])  # Extrai o mês

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
def render_tabs(df):
    """Configura e exibe as abas do aplicativo."""
    abas = st.tabs(['Corretivas', 'Agrupados', 'Resumo Mensal'])
    with abas[0]:
        exibe_metricas(df)
    with abas[1]:

        with st.expander("Filtros"):
                st.write('''
                    The chart above shows some numbers I picked for you.
                    I rolled actual dice for these, so they're *guaranteed* to
                    be random.
                ''')

        exibir_corretivas(df)
    with abas[2]:
        st.write("Conteúdo em desenvolvimento...")

def main():
    """Função principal do aplicativo."""
    configurar_sidebar()
    exibir_cabecalho()
    df = load_excel_data(FILE_XLS)
    render_tabs(df)

if __name__ == "__main__":
    main()
