import streamlit as st
import pandas as pd
from components import titulo_page
from datetime import datetime


def colorir_status(value):
    """
    Função para aplicar cores na coluna STATUS.
        Args:
        value: Valor da célula. 
    Returns:
        str: String CSS para estilizar a célula.
    """
    CORES_STATUS = {
        "ATENDIDO": "green",
        "ABERTO": "red"
    }       
    if isinstance(value, str) and value in CORES_STATUS:
             return f"color: {CORES_STATUS[value]}; font-weight: bold;"
    return ""

# FUNÇÂO PRINCIPAL DO MÓDULO

def corretivas(): 
    COLUNAS_EXIBICAO = [
        'Nº OS', 'STATUS', 'TIPO DE OS','NATUREZA', 'SOLICITANTE', 'DESCRIÇÃO', 
        'QTD_TECNICOS', 'TECNICO', 'EQUIPE',  'Data/Hora Abertura', 'Data/Hora Início',
       'Data/Hora Término', 'Atendimento', 'Solução', 'Execução'
    ]    
    st.markdown(titulo_page('OS Corretivas', 'Criadas no mês, Abertas e Encerradas no Mês'), unsafe_allow_html=True)
    df = pd.read_csv('dados/DBCorretivas.csv', encoding='utf-8')       
    df = df.reindex(columns=COLUNAS_EXIBICAO)     
    with st.sidebar.expander("Filtros"): 
        filtro_status = st.multiselect('Status:', df['STATUS'].unique(),)
        if filtro_status:
             df = df[df['STATUS'].isin(filtro_status)]              
        filtro_equipe = st.multiselect('Equipe:', df['EQUIPE'].unique(),)
        if filtro_equipe:
             df = df[df['EQUIPE'].isin(filtro_equipe)]     
    df = df.style.map(colorir_status, subset=["STATUS"])                                       
    st.dataframe(df, selection_mode="multi", use_container_width= True, hide_index=True)
    
if __name__ == "__page__":
    corretivas()