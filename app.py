import streamlit as st
from utils import header_page, header_side, widget, card
from pages.pg_corretivas import exibir_corretivas

# Constantes
APP_TITLE = 'Geopapp'
APP_ICON = "imgs/roda.png"
LOGO_PATH = "imgs/roda.png"
SIDEBAR_INIT = "collapsed"

def configurar_pagina():
    """Configura a página do Streamlit."""
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        initial_sidebar_state=SIDEBAR_INIT ,
        layout="wide"
    )
    st.logo(LOGO_PATH)

def configurar_sidebar():
    """Configura a barra lateral do aplicativo."""
    with st.sidebar:
        st.markdown(header_side, unsafe_allow_html=True)
        #st.image(LOGO_PATH, use_container_width=True)
        #st.title(APP_TITLE)
        #st.markdown("---")
        #st.write("Selecione as opções abaixo:")
        # Adicione mais widgets ou elementos da barra lateral conforme necessário

def exibir_cabecalho():
    """Exibe o cabeçalho da página."""
    st.markdown(header_page, unsafe_allow_html=True)

def main():
    """Função principal do aplicativo."""

    # Configurar a página
    configurar_pagina()
    # Configurar a barra lateral
    configurar_sidebar()
        # Exibir cabeçalho
    exibir_cabecalho()

    st.markdown("""
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
    """ , unsafe_allow_html=True)
  
    st.markdown(card('ELSIO'), unsafe_allow_html=True)

    # Criar abas
    aba1, aba2, aba3 = st.tabs(['Corretivas', 'Agrupados', 'Resumo Mensal'])
    
    # Conteúdo da aba Corretivas
    with aba1:
        #Exibe Tabela de COrretivas
     
        exibir_corretivas()
    
    # Conteúdo da aba Agrupados
    with aba2:
        pass
    with aba3:
        pass        


if __name__ == "__main__":
    main()
