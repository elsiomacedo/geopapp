import streamlit as st
from streamlit_tags import st_tags
import pandas as pd
from components import titulo_page
from datetime import datetime
import unicodedata


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

        palavras = st_tags(
            label='',
            text=' 🔍 Enter para adicionar',
            value=[],
            maxtags=10,
            key='palavras_badges'
        )
        # Função para remover acentos
        def remover_acentos(texto):
            if isinstance(texto, str):
                return ''.join(
                    c for c in unicodedata.normalize('NFD', texto)
                    if unicodedata.category(c) != 'Mn'
                )
            return texto        
        if palavras:
                # Normaliza as palavras digitadas
                palavras_sem_acento = [remover_acentos(p).lower().strip() for p in palavras]

                # Verifica se o termo especial "nao atendida" está presente
                aplicar_filtro_status = "nao atendida" in palavras_sem_acento

                # Remove "nao atendida" da lista de palavras
                palavras_sem_acento = [p for p in palavras_sem_acento if p != "nao atendida"]

                # Remove acentos do DataFrame (convertendo para string antes)
                df_sem_acento = df.astype(str).map(remover_acentos)

                # Começa com uma máscara booleana verdadeira
                mascara = pd.Series(True, index=df.index)

                # Aplica filtro textual normal (com as palavras restantes)
                if palavras_sem_acento:
                    mascara_texto = df_sem_acento.apply(
                        lambda row: all(p in ' '.join(row).lower() for p in palavras_sem_acento),
                        axis=1
                    )
                    mascara &= mascara_texto

                # Aplica filtro STATUS != ATENDIDO, se necessário
                if aplicar_filtro_status and "STATUS" in df.columns:
                    mascara &= df["STATUS"].astype(str).str.upper() != "ATENDIDO"

                # Aplica os filtros ao DataFrame original
                df = df[mascara]
    #df = df.astype(str).applymap(remover_acentos)            
    #df = df.style.applymap(colorir_status, subset=["STATUS"])
    df = df.style.map(colorir_status, subset=["STATUS"])    
    st.dataframe(df, selection_mode="multi", use_container_width= True, hide_index=True)


    #df = df.style.map(colorir_status, subset=["STATUS"])                                       
    #st.dataframe(df, selection_mode="multi", use_container_width= True, hide_index=True)
    
if __name__ == "__page__":
    corretivas()