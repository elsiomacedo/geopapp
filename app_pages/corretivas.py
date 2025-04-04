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

    # Adicionar coluna de referência no formato yyyy/mm
    df['Referência'] = pd.to_datetime(df['Data/Hora Abertura'], errors='coerce').dt.strftime('%Y/%m')
    
    referencia_atual = st.sidebar.selectbox('Referência', sorted(df['Referência'].unique(), reverse=True), label_visibility='visible')
    
    if referencia_atual:
        df['Data/Hora Abertura'] = pd.to_datetime(df['Data/Hora Abertura'], errors='coerce')
        df['Data/Hora Término'] = pd.to_datetime(df['Data/Hora Término'], errors='coerce')

        # Criar as colunas de referência para Abertura e Término
        df['Ref_Abertura'] = df['Data/Hora Abertura'].dt.strftime('%Y/%m')
        df['Ref_Termino'] = df['Data/Hora Término'].dt.strftime('%Y/%m')

        # Filtrar onde qualquer uma das referências seja igual à referência selecionada
        df = df[(df['Ref_Abertura'] == referencia_atual) | (df['Ref_Termino'] == referencia_atual)]
        df = df[COLUNAS_EXIBICAO]

    with st.sidebar.expander("Filtros"): 
        

        filtro_status = st.multiselect('Status:', ['Todos', 'Atendido', 'Não Atendido'],)
        if 'Atendido' in filtro_status and 'Não Atendido' not in filtro_status:
            df = df[df['STATUS'] == 'ATENDIDO']
        elif 'Não Atendido' in filtro_status and 'Atendido' not in filtro_status:
            df = df[df['STATUS'] != 'ATENDIDO']
        # If 'Todos' is selected or no specific filter is applied, do not filter the dataframe
        filtro_equipe = st.multiselect('Equipe:', [equipe for equipe in df['EQUIPE'].unique() if pd.notnull(equipe)],)
        if filtro_equipe:
             df = df[df['EQUIPE'].isin(filtro_equipe)]     
    df = df.style.map(colorir_status, subset=["STATUS"])                                       
    st.dataframe(df, selection_mode="multi", use_container_width= True, hide_index=True)
    
if __name__ == "__page__":
    corretivas()