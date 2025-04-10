
import streamlit as st
from streamlit_tags import st_tags
import pandas as pd
from components import titulo_page
from datetime import datetime
import unicodedata

# ========== Funções Utilitárias ==========

def remover_acentos(texto):
    if isinstance(texto, str):
        return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    return texto

def colorir_status(value):
    cores = {"ATENDIDO": "green", "ABERTO": "red"}
    if isinstance(value, str) and value in cores:
        return f"color: {cores[value]}; font-weight: bold;"
    return ""

def carregar_dados(path_csv='dados/DBCorretivas.csv'):
    df = pd.read_csv(path_csv, encoding='utf-8')
    df['Data/Hora Abertura'] = pd.to_datetime(df['Data/Hora Abertura'], errors='coerce')
    df['Data/Hora Término'] = pd.to_datetime(df['Data/Hora Término'], errors='coerce')
    df['Referência'] = df['Data/Hora Abertura'].dt.strftime('%Y/%m')
    df['Ref_Abertura'] = df['Data/Hora Abertura'].dt.strftime('%Y/%m')
    df['Ref_Termino'] = df['Data/Hora Término'].dt.strftime('%Y/%m')
    return df

def filtrar_por_referencia(df, referencia):
    return df[(df['Ref_Abertura'] == referencia) | (df['Ref_Termino'] == referencia)]

def aplicar_filtros_textuais(df, palavras):
    palavras_sem_acento = [remover_acentos(p).lower().strip() for p in palavras]
    aplicar_filtro_status = "nao atendida" in palavras_sem_acento
    palavras_sem_acento = [p for p in palavras_sem_acento if p != "nao atendida"]

    df_sem_acento = df.astype(str).map(remover_acentos)
    mascara = pd.Series(True, index=df.index)

    if palavras_sem_acento:
        mascara_texto = df_sem_acento.apply(
            lambda row: all(p in ' '.join(row).lower() for p in palavras_sem_acento), axis=1)
        mascara &= mascara_texto

    if aplicar_filtro_status and "STATUS" in df.columns:
        mascara &= df["STATUS"].astype(str).str.upper() != "ATENDIDO"

    return df[mascara]

# ========== Interface Streamlit ==========

def corretivas():
    st.markdown(titulo_page('OS Corretivas', 'Criadas no mês, Abertas e Encerradas no Mês'), unsafe_allow_html=True)

    df = carregar_dados()
    referencia_atual = st.sidebar.selectbox('Referência', sorted(df['Referência'].unique(), reverse=True))

    if referencia_atual:
        df = filtrar_por_referencia(df, referencia_atual)

        colunas_default = [
            'TIPO DE OS', 'NATUREZA', 'SOLICITANTE', 'DESCRIÇÃO',
            'QTD_TECNICOS', 'TECNICO', 'EQUIPE', 'Data/Hora Abertura',
            'Data/Hora Início', 'Data/Hora Término', 'Atendimento',
            'Solução', 'Execução'
        ]
        # Só inicializa se ainda não existir
        if 'filtro_status' not in st.session_state:
            st.session_state.filtro_status = []

        if st.session_state.get('filtro_status')==[]:
            titulo_expander = "Filtros e Visibilidade dos Campos ╰┈➤"
        else:
            titulo_expander = "Filtros (**Aplicados**) e Visibilidade dos Campos ╰┈➤"
        
        with st.expander(titulo_expander):
            # Filtros de status

            palavras = st_tags(label='Digite Palavras para aplicar Filtros', 
                               text='Enter para adicionar', value=[], 
                               maxtags=10, key="filtro_status")
            
           # filtro_statu = st.session_state.filtro_status = palavras
           
            if palavras:
                df = aplicar_filtros_textuais(df, palavras)
            # Selecionar COlunas Visiveis
            colunas_selecionadas = st.multiselect(
            'Selecione as colunas para exibição:',
            options=colunas_default,
            default=['TIPO DE OS', 'NATUREZA', 'DESCRIÇÃO'],
            key='colunas_exibicao'
            )
            colunas_exibir = ['Nº OS', 'STATUS'] + colunas_selecionadas
            df = df[colunas_exibir]

            if st.session_state.get('filtro_status'):
                st.write(f"Filtros aplicados: {st.session_state.filtro_status}")
            else:
                st.write("Nenhum filtro aplicado.")
                
        df_styled = df.style.map(colorir_status, subset=["STATUS"])
        st.dataframe(df_styled, selection_mode="multi", use_container_width=True, hide_index=True)

if __name__ == "__page__":
    corretivas()
