import streamlit as st
import pandas as pd
from components import titulo_page

def tecnicos(): 
    st.markdown(titulo_page('Equipe Técnica', 'Produtividade Mês Atual'), unsafe_allow_html=True)
    df = pd.read_csv('dados/DBTecno.csv', encoding='utf-8')      
    st.dataframe(df)  
if __name__ == "__page__":
    tecnicos()