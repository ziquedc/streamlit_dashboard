import pandas as pd
import streamlit as st
import requests
import plotly.express as px

##CONFIGS STREAMLIT
st.set_page_config(layout='wide')


#FUNÇÕES
def formata_num(valor, prefixo = ''):
    for unidade in ['','mil']:
        if valor <1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'


st.title('DASHBOARD DE VENDAS :shopping_trolley:')

#FILTROS E BARRA LATERAL
regioes =['Brasil','Centro-Oeste','Nordeste','Norte','Sudeste','Sul']
st.sidebar.title('Filtros')

regiao = st.sidebar.selectbox('Região', regioes)
if regiao == 'Brasil':
    regiao = ''
todos_anos = st.sidebar.checkbox('Dados de todo o período', value=True)
if todos_anos:
    ano=''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)
    

query_string = {'regiao':regiao.lower(), 'ano':ano}

url = 'https://labdados.com/produtos'
response = requests.get(url, params=query_string)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')

#filtro vendedores
filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

#DADOS
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat' ,'lon']].merge(receita_estados, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum','count']))

#VISUALIZAÇÃO DE DADOS
#GRÁFICOS
fig_mapa_receita = px.scatter_geo(receita_estados,
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope='south america',
                                  size='Preço',
                                  template='seaborn',
                                  hover_name = 'Local da compra',
                                  hover_data = {'lat':False, 'lon':False},
                                  title = 'Receita por estado')

#Gráfico de linhas mensal
fig_receita_mensal = px.line(receita_mensal,
                             x='Mes',
                             y='Preço',
                             markers=True,
                             range_y=(0,receita_mensal.max()),
                             color='Ano',
                             title='Receita mensal')
fig_receita_mensal.update_layout(yaxis_title = 'Receita')

#Gráficos de barras
fig_receita_estados = px.bar(receita_estados.head(),
                             x='Local da compra',
                             y='Preço',
                             text_auto = True,
                             title = 'Top estados (receita)')
fig_receita_estados.update_layout(yaxis_title = 'Receita')

fig_receita_categorias = px.bar(receita_categorias,
                                text_auto = True,
                                title = 'Receita por categoria')
fig_receita_categorias.update_layout(yaxis_title = 'Receita')


#ABAS
aba1, aba2 = st.tabs(['Receita', 'Vendedores'])
with aba1:
    #COLUNAS DO GRID
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Receita',formata_num(dados['Preço'].sum(),'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width=True)
        st.plotly_chart(fig_receita_estados, use_container_width=True)
    with col2:    
        st.metric('Qtd. Vendas',formata_num(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width=True)
        st.plotly_chart(fig_receita_categorias, use_container_width=True)

with aba2:
    qtd_vendedores = st.number_input('Quantidade de vendedores',2,10,5)
    #COLUNAS DO GRID
    col1, col2 = st.columns(2)
    with col1:
        st.metric('Receita',formata_num(dados['Preço'].sum(),'R$'))
        fig_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending= True).head(qtd_vendedores),
                                x='sum',
                                y= vendedores[['sum']].sort_values('sum', ascending= True).head(qtd_vendedores).index,
                                text_auto = True,
                                title = f'Top {qtd_vendedores} vendedores (receita)')
        st.plotly_chart(fig_vendedores, use_container_width=True)
    with col2:   
        st.metric('Qtd. Vendas',formata_num(dados.shape[0]))

