import streamlit as st
import time
from components import load_css, header_page, header_side

APP_TITLE = 'Geopapp'
APP_ICON = "imgs/roda.png"
LOGO_PATH = "imgs/casapark@2x.png"
LOGO_ICON = "imgs/icon-casa.png"
SIDEBAR_INIT = 'expanded'

def main():

    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        initial_sidebar_state=SIDEBAR_INIT,
        layout="wide"
    )
    st.logo(LOGO_PATH, size="large", icon_image=LOGO_ICON)

    st.markdown(f'<style>{load_css()}</style>', unsafe_allow_html=True)
    st.markdown(header_page(), unsafe_allow_html=True)
    #st.sidebar.markdown(header_side(), unsafe_allow_html=True)  

    pages = {
        "":[
            st.Page('app_pages/dashboard.py', title = 'Dashboard Geral', icon= ':material/monitoring:'),
        ],
        "Ordens de Serviços": [
            st.Page('app_pages/corretivas.py', title = 'OS Corretivas', icon= ':material/docs:'),
        ],
        "Configurações": [
            st.Page('app_pages/atualdata.py', title = 'Atualiza Dados', icon= ':material/database:'),       
            ] ,
        }

    pg=st.navigation(pages, position='sidebar')

    pg.run()

if __name__ == '__main__':
    main()






