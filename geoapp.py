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


def main():

    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        initial_sidebar_state=SIDEBAR_INIT,
        layout="wide"
    )
    st_theme = st_javascript("""window.getComputedStyle(window.parent.document.getElementsByClassName("stApp")[0]).getPropertyValue("color-scheme")""")
    #st.write(st_theme)
    if st_theme =='light':
        st.logo(LOGO_LIGHT, size="large", icon_image=LOGO_ICON)
    else:
        st.logo(LOGO_DARK, size="large", icon_image=LOGO_ICON)

    st.markdown(f'<style>{load_css()}</style>', unsafe_allow_html=True)
    st.markdown(header_page('Gestão de Operações'), unsafe_allow_html=True)
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






