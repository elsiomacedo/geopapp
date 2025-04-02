import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# DataFrame exemplo
df = pd.DataFrame({
    'ID': [1, 2, 3],
    'Nome': ['Ana', 'Bruno', 'Carlos'],
    'Email': ['ana@email.com', 'bruno@email.com', 'carlos@email.com'],
    'Idade': [25, 30, 35],
    'Cidade': ['SP', 'RJ', 'MG']
})

st.write("### Clique em uma linha da tabela para ver os detalhes")

# Configurações do AgGrid
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_selection('single', use_checkbox=False)  # Seleção por clique
grid_options = gb.build()

# Renderiza a tabela com seleção ativada
grid_response = AgGrid(
    df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    height=250,
    theme='blue'
)

# Captura a seleção (sempre uma lista de dicts ou vazia)
selected = grid_response.get('selected_rows', [])

# Se vier como DataFrame, converte
if isinstance(selected, pd.DataFrame):
    selected = selected.to_dict(orient='records')

# Verifica se há seleção
if isinstance(selected, list) and len(selected) > 0:
    st.write("### Detalhes da linha selecionada:")
    for chave, valor in selected[0].items():
        st.text_input(chave, value=str(valor), disabled=True)
else:
    st.info("Nenhuma linha selecionada.")