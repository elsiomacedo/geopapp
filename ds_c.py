import streamlit as st
import os
import time

def save_uploaded_file(uploaded_file, folder="dados", fonte="corretivas"):

    # Caminho completo para salvar o arquivo
    fonte = fonte + ".xls"
    file_path = os.path.join(folder, fonte)

    # Salva o arquivo na subpasta
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Mostra a mensagem de sucesso   
    message_placeholder = st.empty()        
    message_placeholder.success("Arquivo salvo com sucesso!")  # Exibe a mensagem
    time.sleep(2)  # Aguarda 2 segundos
    message_placeholder.empty()  # Limpa a mensagem

with st.expander("Filtros"):
        # Widget de upload
        uploaded_file = st.file_uploader("Escolha um arquivo para enviar", type=["xls"])

        # Salva o arquivo se o upload for feito
        if uploaded_file is not None:
            save_uploaded_file(uploaded_file)  
          