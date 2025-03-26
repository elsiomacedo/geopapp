import streamlit as st
from components import titulo_page

def dashboard(): 
    st.markdown(titulo_page('Dashboard', 'Análise por AI'), unsafe_allow_html=True)
if __name__ == "__page__":
    dashboard()