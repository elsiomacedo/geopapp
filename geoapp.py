import streamlit as st
import time
from components import load_css, header_page
from streamlit_javascript import st_javascript

APP_TITLE = 'Geopapp'
APP_ICON = "imgs/roda.png"
SIDEBAR_INIT = 'expanded'

LOGO_DARK = "imgs/casapark-dark.png"
LOGO_LIGHT ="imgs/casapark-light.png"
LOGO_ICON = "imgs/icon-casa.png"


def configurar_pagina():
    """Configura a página do Streamlit com título, ícone e tema."""
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        initial_sidebar_state=SIDEBAR_INIT,
        layout="wide"
    )

    tema= detectar_tema()

    marca = LOGO_LIGHT if tema == 'light' else LOGO_DARK
    #print(marca)
    st.logo(marca, size="large", icon_image=LOGO_ICON)

def detectar_tema():
    # Injeta um div oculto com a cor de fundo do tema atual
    st.markdown("""
        <div id="theme-detector" style="background-color: var(--background-color); display:none;"></div>
    """, unsafe_allow_html=True)

    # JavaScript pega a cor computada do background
    cor_fundo = st_javascript("""
        const elem = window.parent.document.getElementById("theme-detector");
        const color = window.getComputedStyle(elem).backgroundColor;
        color;
    """)
    # Analisa se é tema escuro baseado na cor RGB
    if cor_fundo and isinstance(cor_fundo, str):
        if "rgb(0, 0, 0" in cor_fundo or "rgb(1, 1, 1" in cor_fundo:  # preto ou quase preto
            return "dark"
        else:
            return "light"
    return "light"  # fallback


def aplicar_estilos():
    """Aplica estilos CSS e cabeçalho da página."""
    st.markdown(f'<style>{load_css()}</style>', unsafe_allow_html=True)
    st.markdown(header_page('Gestão de Operações'), unsafe_allow_html=True)

def carregar_paginas():
    """Define a estrutura de navegação entre as páginas da aplicação."""
    paginas = {
        "": [
            st.Page('app_pages/dashboard.py', title='Dashboard Geral', icon=':material/monitoring:'),
        ],
        "Ordens de Serviços": [
            st.Page('app_pages/corretivas.py', title='OS Corretivas', icon=':material/docs:'),
            st.Page('app_pages/tecnicos.py', title='Técnicos', icon=':material/group:'),
        ],
        "Configurações": [
            st.Page('app_pages/atualdata.py', title='Atualiza Dados', icon=':material/database:'),
        ],
    }
    return st.navigation(paginas, position='sidebar')

def main():
    configurar_pagina()
    aplicar_estilos()
    pagina = carregar_paginas()
    pagina.run()

if __name__ == '__main__':
    main()
