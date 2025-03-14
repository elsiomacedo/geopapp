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

from utils import header_page, header_side
from datasets.ds_corretivas import load_excel_data, exibir_corretivas, calculo_metricas
from streamlit_extras.metric_cards import style_metric_cards


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

    print(metricas_df)

    ano_atual = 2025
    mes_atual = 3

    # Ajusta o mês e ano anterior se o mês atual for janeiro
    if mes_atual == 1:
        mes_anterior = 12
        ano_anterior = ano_atual - 1
    else:
        mes_anterior = mes_atual - 1
        ano_anterior = ano_atual

    ''' Obtém o valor da métrica para o ano e mês específicos'''
    os_abertas_atual = metricas_df[(metricas_df['Ano'] == ano_atual) & (metricas_df['Mês'] == mes_atual)]['OS Abertas'].values[0]
    os_abertas_ant = metricas_df[(metricas_df['Ano'] == ano_anterior) & (metricas_df['Mês'] == mes_anterior)]['OS Abertas'].values[0]

    os_nat_mes_atual = metricas_df[(metricas_df['Ano'] == ano_atual) & (metricas_df['Mês'] == mes_atual)]['OS Não Atendidas'].values[0]
    os_nat_mes_ant = metricas_df[(metricas_df['Ano'] == ano_anterior) & (metricas_df['Mês'] == mes_anterior)]['OS Não Atendidas'].values[0]

    os_at_mes_atual = metricas_df[(metricas_df['Ano'] == ano_atual) & (metricas_df['Mês'] == mes_atual)]['OS Atendidas'].values[0]
    os_at_mes_ant = metricas_df[(metricas_df['Ano'] == ano_anterior) & (metricas_df['Mês'] == mes_anterior)]['OS Atendidas'].values[0]


    # Exibe métricas utilizando colunas
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric(label="OS Abertas no Mês", value=os_abertas_atual, delta=int(os_abertas_atual-os_abertas_ant))
    col2.metric(label="OS Não Atendidas no Mês", value=os_nat_mes_atual, delta=int(os_nat_mes_atual-os_nat_mes_ant))    
    col3.metric(label="OS Atendidas dentro do Mês", value=os_at_mes_atual, delta=int(os_at_mes_atual-os_at_mes_ant))    
    col4.metric(label="OS Atendidas dentro do Mês", value=os_at_mes_atual, delta=int(os_at_mes_atual-os_at_mes_ant))   
    col5.metric(label="OS Atendidas dentro do Mês", value=os_at_mes_atual, delta=int(os_at_mes_atual-os_at_mes_ant))       

    #col2.metric(label="Loss", value=5000, delta=-1000)    
    #col3.metric(label="No Change", value=5000, delta=0)
    style_metric_cards()

def render_tabs(df):
    """Configura e exibe as abas do aplicativo."""
    abas = st.tabs(['Corretivas', 'Agrupados', 'Resumo Mensal'])
    with abas[0]:
        exibir_corretivas(df)
    with abas[1]:
        st.write("Conteúdo em desenvolvimento...")
    with abas[2]:
        st.write("Conteúdo em desenvolvimento...")

def main():
    """Função principal do aplicativo."""
    configurar_sidebar()
    exibir_cabecalho()
    df = load_excel_data(FILE_XLS)
    exibe_metricas(df)
    render_tabs(df)

if __name__ == "__main__":
    main()
