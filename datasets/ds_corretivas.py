import pandas as pd
from datetime import datetime

data_atual = datetime.now()
dados = pd.read_csv('dados/Optimus Dados.csv', sep=';')

# Converter as colunas de data e hora para o formato datetime
dados['DATA DE ABERTURA'] = pd.to_datetime(dados['DATA DE ABERTURA'], format='%d/%m/%Y')
dados['HORA DE ABERTURA'] = pd.to_datetime(dados['HORA DE ABERTURA'], format='%H:%M:%S').dt.time
# Criar uma nova coluna datetime combinando 'DATA DE ABERTURA' e 'HORA DE ABERTURA'
dados['DTH_ABERTURA'] = pd.to_datetime(dados['DATA DE ABERTURA'].astype(str) + ' ' + dados['HORA DE ABERTURA'].astype(str))
dados = dados.drop(columns=['DATA DE ABERTURA', 'HORA DE ABERTURA'])

# Converter as colunas de data e hora para o formato datetime
dados['DATA DE INÍCIO'] = pd.to_datetime(dados['DATA DE INÍCIO'], format='%d/%m/%Y', errors='coerce')
dados['HORA DE INÍCIO'] = pd.to_datetime(dados['HORA DE INÍCIO'], format='%H:%M:%S', errors='coerce').dt.time
# Criar uma nova coluna datetime combinando 'DATA DE INÍCIO' e 'HORA DE INÍCIO'
dados['DTH_INÍCIO'] = pd.to_datetime(dados['DATA DE INÍCIO'].astype(str) + ' ' + dados['HORA DE INÍCIO'].astype(str), errors='coerce')
# Excluir as colunas 'DATA DE INÍCIO' e 'HORA DE INÍCIO'
dados = dados.drop(columns=['DATA DE INÍCIO', 'HORA DE INÍCIO'])


# Converter as colunas de data e hora para o formato datetime
dados['DATA DE TÉRMINO'] = pd.to_datetime(dados['DATA DE TÉRMINO'], format='%d/%m/%Y', errors='coerce')
dados['HORA DE TÉRMINO'] = pd.to_datetime(dados['HORA DE TÉRMINO'], format='%H:%M:%S', errors='coerce').dt.time
# Criar uma nova coluna datetime combinando 'DATA DE INÍCIO' e 'HORA DE INÍCIO'
dados['DTH_TÉRMINO'] = pd.to_datetime(dados['DATA DE TÉRMINO'].astype(str) + ' ' + dados['HORA DE TÉRMINO'].astype(str), errors='coerce')
# Excluir as colunas 'DATA DE INÍCIO' e 'HORA DE INÍCIO'
dados = dados.drop(columns=['DATA DE TÉRMINO', 'HORA DE TÉRMINO'])


#dados_nos = dados.shape[0]
dados_qtde = dados.groupby('STATUS')['Nº OS'].agg('count').sort_values(ascending=False)
dados_nat = dados.groupby('NATUREZA')['Nº OS'].agg('count').sort_values(ascending=False)
dados_tipo = dados.groupby('TIPO DE OS')['Nº OS'].agg('count').sort_values(ascending=False)
dados_tip = dados.groupby('TIPO DE OS')['Nº OS'].agg('count').sort_values(ascending=False)
dados_sol = dados.groupby('SOLICITANTE')['Nº OS'].agg('count').sort_values(ascending=False)
dados_tec = dados.groupby('TÉCNICO')['Nº OS'].agg('count').sort_values(ascending=False)

#Separa BACKLOG
data_limite = data_atual - pd.Timedelta(days=30)
filtro = (dados['STATUS'] != 'ATENDIDO') & (dados['DTH_ABERTURA'] < data_limite)
backlog = dados[filtro]
qtde_backlog = len(backlog)

#Separa ATENDIDAS
filtro = (dados['STATUS'] == 'ATENDIDO')
ds_atendidas = dados[filtro]
qtde_os_atendidas = len(ds_atendidas)

#Separa ABERTAS
filtro = (dados['STATUS'] != 'ATENDIDO')
ds_abertas = dados[filtro]
qtde_os_abertas = len(ds_abertas) - qtde_backlog

dados_nos = qtde_os_atendidas + qtde_os_abertas + qtde_backlog 
qtde_corretivas = qtde_os_atendidas + qtde_os_abertas

# Formatar a coluna 'DTH_ABERTURA' no formato 'dia/mês/ano'
#dados['DTH_ABERTURA'] = dados['DTH_ABERTURA'].dt.strftime('%d/%m/%Y %H:%M:%S')
# Formatar a coluna 'DTH_INÍCIO' no formato 'dia/mês/ano'
#dados['DTH_INÍCIO'] = dados['DTH_INÍCIO'].dt.strftime('%d/%m/%Y %H:%M:%S')
# Formatar a coluna 'DTH_INÍCIO' no formato 'dia/mês/ano'
#dados['DTH_TÉRMINO'] = dados['DTH_TÉRMINO'].dt.strftime('%d/%m/%Y %H:%M:%S')

# Contar o número de registros que atendem às condições


