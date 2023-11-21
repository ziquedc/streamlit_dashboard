import pandas as pd
import streamlit as st
import requests
import time

##CONFIGS STREAMLIT
st.set_page_config(layout='wide')


#FUNCOES
@st.cache_data
def convert_csv(df):
    return df.to_csv(index= False).encode('utf-8')

def mensagem_sucesso():
     sucesso = st.success('Arquivo baixado com sucesso!')
     time.sleep(6)
     sucesso.empty()


st.title('DADOS BRUTOS')

url = 'https://labdados.com/produtos'
response = requests.get(url)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')

with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as colunas', list(dados.columns), list(dados.columns))



#BARRA LATERAL
st.sidebar.title('Filtros')
with st.sidebar.expander('Nome do produto'):
    produtos = st.multiselect('Selecione os produtos', dados['Produto'].unique(), dados['Produto'].unique())
with st.sidebar.expander('PreÃ§o do produto'):
    preco = st.slider('Selecione o preÃ§o do produto',0, 5000, (0,5000))
with st.sidebar.expander('Data da compra'):
    data_compra = st.date_input('Selecione a data',(dados['Data da Compra'].min(), dados['Data da Compra'].max()) )

query = '''
Produto in @produtos and \
@preco[0] <= PreÃ§o <= @preco[1] and \
@data_compra[0] <= `Data da Compra` <= @data_compra[1]
'''
dados_filtrados = dados.query(query)
dados_filtrados = dados_filtrados[colunas]

st.dataframe(dados_filtrados)

st.markdown(f'A tabela possui :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}] colunas')


#botao de download
st.markdown('Escreva um nome para o arquivo')
coluna1, coluna2 = st.columns(2)
with coluna1:
    nome_arquivo = st.text_input('', label_visibility='collapsed', value='dados')
    nome_arquivo += '.csv'
with coluna2:
    st.download_button('Baixar dados em CSV', data=convert_csv(dados_filtrados), file_name=nome_arquivo, mime='text/csv', on_click=mensagem_sucesso)
