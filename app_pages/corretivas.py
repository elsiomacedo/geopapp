import streamlit as st
from components import load_css, header_page

def corretivas(): 
    st.title('Streamlit Page Navigation Tutorial')
    st.write('Teste de navegação')

if __name__ == "__page__":
    corretivas()