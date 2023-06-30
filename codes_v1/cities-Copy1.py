# Libraries
import pandas as pd
import plotly.express as px
import re
import folium
from haversine import haversine
import plotly.graph_objects as go
import jupyterlab_dash
import streamlit as st
import datetime as dt
from PIL import Image
from streamlit_folium import folium_static
from folium.plugins import FastMarkerCluster
import inflection
import numpy as np

st.set_page_config( page_title='Cities', page_icon='🏙️', layout = 'wide' )

# ======================================
# Funções
# ======================================
# Renomear as colunas do DataFrame
def rename_columns(dataframe):
    df = dataframe.copy()
    title = lambda x: inflection.titleize(x)
    snakecase = lambda x: inflection.underscore(x)
    spaces = lambda x: x.replace(" ", "")
    cols_old = list(df.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old))
    cols_new = list(map(snakecase, cols_old))
    df.columns = cols_new
    return df

# Preenchimento do nome dos países
COUNTRIES = {
    1: "India",
    14: "Australia",
    30: "Brazil",
    37: "Canada",
    94: "Indonesia",
    148: "New Zeland",
    162: "Philippines",
    166: "Qatar",
    184: "Singapure",
    189: "South Africa",
    191: "Sri Lanka",
    208: "Turkey",
    214: "United Arab Emirates",
    215: "England",
    216: "United States of America",
}
def country_name(country_id):
    return COUNTRIES[country_id]

# Criação do Tipo de Categoria de Comida
def create_price_tye(price_range):
    if price_range == 1:
        return "cheap"
    elif price_range == 2:
        return "normal"
    elif price_range == 3:
        return "expensive"
    else:
        return "gourmet"

# Criação do nome das Cores
COLORS = {
    "3F7E00": "darkgreen",
    "5BA829": "green",
    "9ACD32": "lightgreen",
    "CDD614": "orange",
    "FFBA00": "red",
    "CBCBC8": "darkred",
    "FF7800": "darkred",
}
def color_name(color_code):
    return COLORS[color_code]


# ============================ Inicio da estrutura lógica do codigo =======================
# ==========================    
# Import Dataset
# ==========================  
df_raw = pd.read_csv( 'zomato.csv')
df_raw.head()
df = df_raw.copy()

# ==========================    
# Limpando os dados
# ========================== 
# Renomeando as colunas do dataframe
df = rename_columns(df)

# Removendo as linhas duplicadas do Dataframe
df = df.drop_duplicates().reset_index(drop = True )

# Excluindo todas a linhas sem dados do dataframe
df = df.dropna()

# Alterando os tipos das colunas
df['restaurant_name'] = df['restaurant_name'].astype(object)

df['cuisines'] = df['cuisines'].astype(str)

# Categrorizando a coluna Cuisine somente por um tipo de culinária
df["cuisines"] = df.loc[:, "cuisines"].apply(lambda x: x.split(",")[0])

# Limpando as linhas vazias
df = df.loc[(df['cuisines'] != 'nan'), :]
df = df.loc[(df['cuisines'] != 'Drinks Only'), :]
df = df.loc[(df['cuisines'] != 'Mineira'), :]

# Removendo coluna Switch to order menu do df
df = df.drop('switch_to_order_menu', axis = 1 )

# Renomeando as linhas da coluna county_code
df['country_code'] = df.loc[:, 'country_code'].apply(lambda x: country_name(x))

# Criação do Tipo de Categoria de Comida
df['price_range'] = df.loc[:, 'price_range'].apply(lambda x: create_price_tye(x))

# Criação do nome das Cores
df['rating_color'] = df.loc[:, 'rating_color'].apply(lambda x: color_name(x))


#========================================
# Barra lateral
#=========================================
st.header('🏙️ Visão Cidades')

st.sidebar.markdown('## Filtros')

countries_options = st.sidebar.multiselect(
    'Escolha os países que deseja visualizar as informações',
    ["India", "Australia", "Brazil", "Canada", "Indonesia", "New Zeland", "Philippines", "Qatar", "Singapure", "South Africa",
     "Sri Lanka", "Turkey", "United Arab Emirates", "England", "United States of America"],
    default = ['Brazil', 'England', 'Qatar', 'South Africa', 'Canada', 'Australia'] )

# Filtro de países
linhas_selecionadas = df['country_code'].isin( countries_options )
df = df.loc[ linhas_selecionadas, :]


st.sidebar.markdown(""" ---""")
st.sidebar.markdown('### Powered by Matheus Serafim')

#========================================
# Layout no Streamlit
#========================================
with st.container():
    df_aux = (df.loc[:, ['restaurant_id', 'city', 'country_code']]
                .groupby(['city', 'country_code'])
                .count()
                .sort_values(['restaurant_id','city'],ascending=[False,True])
                .reset_index())

    fig = (px.bar(df_aux.head(10), x = 'city' , y = 'restaurant_id', 
                  text_auto = True, 
                  labels = {'city' : 'Cidade' , 'restaurant_id' : 'Quantidade de restaurantes', 'country_code': 'País'}, 
                  color = 'country_code', 
                  title = 'Top 10 Cidades com mais restaurantes na Base de Dados'))

    st.plotly_chart(fig, use_container_width = True)

with st.container():

    col1, col2 = st.columns( 2 )
    with col1:
        df_aux = (df.loc[: , ['city' , 'restaurant_id' , 'aggregate_rating' , 'country_code']]
                    .groupby(['country_code' , 'city' , 'restaurant_id'])
                    .mean()
                    .sort_values('aggregate_rating' , ascending = False)
                    .reset_index())
        
        df_aux2 = (df_aux.loc[df_aux['aggregate_rating'] >= 4 , ['city', 'restaurant_id', 'country_code']]
                         .groupby(['country_code', 'city'])
                         .count()
                         .sort_values('restaurant_id' , ascending = False)
                         .reset_index())

        fig = (px.bar(df_aux2.head(7), x = 'city' , y = 'restaurant_id', 
                      text_auto = True, 
                      labels = {'city' : 'Cidade' , 'restaurant_id' : 'Quantidade de restaurantes', 'country_code': 'País'}, 
                      color = 'country_code', 
                      title = 'Top 7 Cidades com restaurantes com média de avaliação acima de 4'))

        st.plotly_chart(fig, use_container_width = True)

    with col2:
        df_aux = (df.loc[: , ['city' , 'restaurant_id' , 'aggregate_rating' , 'country_code']]
                  .groupby(['country_code' , 'city' , 'restaurant_id'])
                  .mean()
                  .sort_values('aggregate_rating' , ascending = True)
                  .reset_index())
        
        df_aux2 = (df_aux.loc[df_aux['aggregate_rating'] <= 2.5 , ['city', 'restaurant_id', 'country_code']]
                         .groupby(['country_code', 'city'])
                         .count()
                         .sort_values('restaurant_id' , ascending = False)
                         .reset_index())

        fig = (px.bar(df_aux2.head(7), x = 'city' , y = 'restaurant_id', 
                      text_auto = True, 
                      labels = {'city' : 'Cidade' , 'restaurant_id' : 'Quantidade de restaurantes', 'country_code': 'País'}, 
                      color = 'country_code', 
                      title = 'Top 7 Cidades com restaurantes com média de avaliação abaixo de 2.5'))
        
        st.plotly_chart(fig, use_container_width = True)

with st.container():
    df_aux = df.loc[: , ['city' , 'cuisines', 'country_code']].groupby(['city', 'country_code']).nunique().sort_values('cuisines', ascending = False ).reset_index()

    fig = (px.bar(df_aux.head(10), x = 'city' , y = 'cuisines', 
                  text_auto = True, 
                  labels = {'city' : 'Cidade' , 'cuisines' : 'Quantidade de tipos culinários únicos', 'country_code': 'País'}, 
                  color = 'country_code', 
                  title = 'Top 10 Cidades com mais restaurantes com tipos culinários distintos'))

    st.plotly_chart(fig, use_container_width = True)
        


    