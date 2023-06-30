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

st.set_page_config( page_title='Cities', page_icon='🍽️', layout = 'wide' )

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

df1 = df.copy()
df2 = df.copy()
#========================================
# Barra lateral
#=========================================
st.sidebar.markdown('## Filtros')

countries_options = st.sidebar.multiselect(
    'Escolha os países que deseja visualizar as informações',
    ["India", "Australia", "Brazil", "Canada", "Indonesia", "New Zeland", "Philippines", "Qatar", "Singapure", "South Africa",
     "Sri Lanka", "Turkey", "United Arab Emirates", "England", "United States of America"],
    default = ['Brazil', 'England', 'Qatar', 'South Africa', 'Canada', 'Australia'] )

# Filtro de países
linhas_selecionadas = df['country_code'].isin( countries_options )
df = df.loc[ linhas_selecionadas, :]


restaurant_numbers = st.sidebar.slider('Selecione a quantidade de Restaurantes que deseja visualizar', 1, 20)


cuisines_options = st.sidebar.multiselect(
       'Escolha os tipos de culinária',
       ['Italian', 'European', 'Filipino', 'American', 'Korean', 'Pizza',
       'Taiwanese', 'Japanese', 'Coffee', 'Chinese', 'Seafood',
       'Singaporean', 'Vietnamese', 'Latin American', 'Healthy Food',
       'Cafe', 'Fast Food', 'Brazilian', 'Argentine', 'Arabian', 'Bakery',
       'Tex-Mex', 'Bar Food', 'International', 'French', 'Steak',
       'German', 'Sushi', 'Grill', 'Peruvian', 'North Eastern',
       'Ice Cream', 'Burger', 'Mexican', 'Vegetarian', 'Contemporary',
       'Desserts', 'Juices', 'Beverages', 'Spanish', 'Thai', 'Indian',
       'BBQ', 'Mongolian', 'Portuguese', 'Greek', 'Asian', 'Author',
       'Gourmet Fast Food', 'Lebanese', 'Modern Australian', 'African',
       'Coffee and Tea', 'Australian', 'Middle Eastern', 'Malaysian',
       'Tapas', 'New American', 'Pub Food', 'Southern', 'Diner', 'Donuts',
       'Southwestern', 'Sandwich', 'Irish', 'Mediterranean', 'Cafe Food',
       'Korean BBQ', 'Fusion', 'Canadian', 'Breakfast', 'Cajun',
       'New Mexican', 'Belgian', 'Cuban', 'Taco', 'Caribbean', 'Polish',
       'Deli', 'British', 'California', 'Others', 'Eastern European',
       'Creole', 'Ramen', 'Ukrainian', 'Hawaiian', 'Patisserie',
       'Yum Cha', 'Pacific Northwest', 'Tea', 'Moroccan', 'Burmese',
       'Dim Sum', 'Crepes', 'Fish and Chips', 'Russian', 'Continental',
       'South Indian', 'North Indian', 'Salad', 'Finger Food', 'Mandi',
       'Turkish', 'Kerala', 'Pakistani', 'Biryani', 'Street Food',
       'Nepalese', 'Goan', 'Iranian', 'Mughlai', 'Rajasthani', 'Mithai',
       'Maharashtrian', 'Gujarati', 'Rolls', 'Momos', 'Parsi',
       'Modern Indian', 'Andhra', 'Tibetan', 'Kebab', 'Chettinad',
       'Bengali', 'Assamese', 'Naga', 'Hyderabadi', 'Awadhi', 'Afghan',
       'Lucknowi', 'Charcoal Chicken', 'Mangalorean', 'Egyptian',
       'Malwani', 'Armenian', 'Roast Chicken', 'Indonesian', 'Western',
       'Dimsum', 'Sunda', 'Kiwi', 'Asian Fusion', 'Pan Asian', 'Balti',
       'Scottish', 'Cantonese', 'Sri Lankan', 'Khaleeji', 'South African',
       'Durban', 'World Cuisine', 'Izgara', 'Home-made', 'Giblets',
       'Fresh Fish', 'Restaurant Cafe', 'Kumpir', 'Döner',
       'Turkish Pizza', 'Ottoman', 'Old Turkish Bars', 'Kokoreç'],
        default = ['Home-made', 'BBQ', 'Japanese', 'Brazilian', 'Arabian', 'American', 'Italian'])

# Filtro de cuisines
linhas_filtradas = df['cuisines'].isin( cuisines_options )
df = df.loc[ linhas_filtradas, :]    


st.sidebar.markdown(""" ---""")
st.sidebar.markdown('### Powered by Matheus Serafim')

#========================================
# Layout no Streamlit
#========================================
st.markdown('# 🍽️ Visão Tipos de Cozinhas')

st.markdown('## Melhores Restaurantes dos Principais tipos Culinários')

with st.container():

    col1, col2, col3, col4, col5 = st.columns( 5 )
    with col1:
        df_aux = (df1.loc[(df1.loc[: , 'cuisines'] == 'Italian') , ['restaurant_name' , 'aggregate_rating', 'restaurant_id']]
                            .groupby(['restaurant_name', 'restaurant_id'])
                            .mean()
                            .sort_values(['aggregate_rating'] , ascending = False)
                            .reset_index())
        
        df_aux = (df_aux.loc[df_aux['aggregate_rating'] == df_aux['aggregate_rating']
                        .max(),['restaurant_name','restaurant_id']]
                        .groupby('restaurant_name')
                        .min()
                        .sort_values(by='restaurant_id',ascending=True)
                        .reset_index())

        df_aux = df1.loc[df1['restaurant_id'] == df_aux.iloc[0,1],['restaurant_name','country_code','city','average_cost_for_two','currency','cuisines','aggregate_rating']]
        
        
        col1.metric(f'{df_aux.iloc[0,5]} : {df_aux.iloc[0,0]}' , f'{df_aux.iloc[0,6]}/5.0')

    with col2:
        df_aux = (df1.loc[(df1.loc[: , 'cuisines'] == 'American') , ['restaurant_name' , 'aggregate_rating', 'restaurant_id']]
                            .groupby(['restaurant_name', 'restaurant_id'])
                            .mean()
                            .sort_values(['aggregate_rating'] , ascending = False)
                            .reset_index())
        
        df_aux = (df_aux.loc[df_aux['aggregate_rating'] == df_aux['aggregate_rating']
                        .max(),['restaurant_name','restaurant_id']]
                        .groupby('restaurant_name')
                        .min()
                        .sort_values(by='restaurant_id',ascending=True)
                        .reset_index())

        df_aux = df1.loc[df1['restaurant_id'] == df_aux.iloc[0,1],['restaurant_name','country_code','city','average_cost_for_two','currency','cuisines','aggregate_rating']]
        
        
        col2.metric(f'{df_aux.iloc[0,5]} : {df_aux.iloc[0,0]}' , f'{df_aux.iloc[0,6]}/5.0')

    with col3:
        df_aux = (df1.loc[(df1.loc[: , 'cuisines'] == 'Arabian') , ['restaurant_name' , 'aggregate_rating', 'restaurant_id']]
                            .groupby(['restaurant_name', 'restaurant_id'])
                            .mean()
                            .sort_values(['aggregate_rating'] , ascending = False)
                            .reset_index())
        
        df_aux = (df_aux.loc[df_aux['aggregate_rating'] == df_aux['aggregate_rating']
                        .max(),['restaurant_name','restaurant_id']]
                        .groupby('restaurant_name')
                        .min()
                        .sort_values(by='restaurant_id',ascending=True)
                        .reset_index())

        df_aux = df1.loc[df1['restaurant_id'] == df_aux.iloc[0,1],['restaurant_name','country_code','city','average_cost_for_two','currency','cuisines','aggregate_rating']]
        
        
        col3.metric(f'{df_aux.iloc[0,5]} : {df_aux.iloc[0,0]}' , f'{df_aux.iloc[0,6]}/5.0')

    with col4:
        df_aux = (df1.loc[(df1.loc[: , 'cuisines'] == 'Japanese') , ['restaurant_name' , 'aggregate_rating', 'restaurant_id']]
                            .groupby(['restaurant_name', 'restaurant_id'])
                            .mean()
                            .sort_values(['aggregate_rating'] , ascending = False)
                            .reset_index())
        
        df_aux = (df_aux.loc[df_aux['aggregate_rating'] == df_aux['aggregate_rating']
                        .max(),['restaurant_name','restaurant_id']]
                        .groupby('restaurant_name')
                        .min()
                        .sort_values(by='restaurant_id',ascending=True)
                        .reset_index())

        df_aux = df1.loc[df1['restaurant_id'] == df_aux.iloc[0,1],['restaurant_name','country_code','city','average_cost_for_two','currency','cuisines','aggregate_rating']]
        
        
        col4.metric(f'{df_aux.iloc[0,5]} : {df_aux.iloc[0,0]}' , f'{df_aux.iloc[0,6]}/5.0')

    with col5:
        df_aux = (df1.loc[(df1.loc[: , 'cuisines'] == 'Brazilian') , ['restaurant_name' , 'aggregate_rating', 'restaurant_id']]
                            .groupby(['restaurant_name', 'restaurant_id'])
                            .mean()
                            .sort_values(['aggregate_rating'] , ascending = False)
                            .reset_index())
        
        df_aux = (df_aux.loc[df_aux['aggregate_rating'] == df_aux['aggregate_rating']
                        .max(),['restaurant_name','restaurant_id']]
                        .groupby('restaurant_name')
                        .min()
                        .sort_values(by='restaurant_id',ascending=True)
                        .reset_index())

        df_aux = df1.loc[df1['restaurant_id'] == df_aux.iloc[0,1],['restaurant_name','country_code','city','average_cost_for_two','currency','cuisines','aggregate_rating']]
        
        
        col5.metric(f'{df_aux.iloc[0,5]} : {df_aux.iloc[0,0]}' , f'{df_aux.iloc[0,6]}/5.0')
        
        
with st.container():
    st.markdown(f'## Top {restaurant_numbers} Restaurantes')
    df_aux = (df.loc[: , ['restaurant_id' , 'restaurant_name' , 'country_code' , 'city' ,
                          'cuisines' , 'average_cost_for_two' , 'aggregate_rating' ,   'votes']]
                .sort_values(['aggregate_rating' , 'restaurant_id'] , ascending = [False, True]))
    df_aux['restaurant_id'] = df1.loc[:, 'restaurant_id'].apply(lambda x: "{0:>20}".format(x))
    df_aux['votes'] = df1.loc[:, 'votes'].apply(lambda x: "{0:>20}".format(x))
    st.dataframe( df_aux.head(restaurant_numbers) )

with st.container():

    col1, col2 = st.columns(2)
    with col1:
        df_aux = round(df2.loc[: , ['cuisines' , 'aggregate_rating']].groupby(['cuisines']).mean().sort_values('aggregate_rating' , ascending = False).reset_index(), 2)

        fig = (px.bar(df_aux.head(restaurant_numbers), x = 'cuisines' , y = 'aggregate_rating', 
                      text_auto = True, 
                      labels = {'cuisines' : 'Tipo de Culinária' , 'aggregate_rating' : 'Média da Avaliação Média'}, 
                      title = f'Top {restaurant_numbers} Melhores tipos de Culinárias'))
        
        st.plotly_chart(fig, use_container_width = True)

    with col2:
        df_aux = (round(df2.loc[: , ['cuisines' , 'aggregate_rating']]
                          .groupby(['cuisines'])
                          .mean()
                          .sort_values('aggregate_rating' , ascending = True)
                          .reset_index(), 2))

        fig = (px.bar(df_aux.head(restaurant_numbers), x = 'cuisines' , y = 'aggregate_rating', 
                      text_auto = True, labels = {'cuisines' : 'Tipo de Culinária' , 'aggregate_rating' : 'Média da Avaliação Média'}, 
                      title = f'Top {restaurant_numbers} Piores Tipos de Culinárias'))

        st.plotly_chart(fig, use_container_width = True)
        

        
        