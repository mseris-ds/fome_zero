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

st.set_page_config( page_title='Main Page', page_icon='📊', layout = 'wide' )

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

def clean_code( df ):
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

    return df    

def country_maps( df ):
        re6 = df.loc[:,['restaurant_name','average_cost_for_two','currency','aggregate_rating','country_code','city','cuisines','latitude','longitude']]
        map1 = folium.Map(location=[0, 0],zoom_start=2)
        marker_cluster = folium.plugins.MarkerCluster().add_to(map1)
        for index,location in re6.iterrows():
            folium.Marker([location['latitude'],location['longitude']],
            popup=folium.Popup(f'''<h6><b>{location['restaurant_name']}</b></h6>
            <h6>Preço: {location['average_cost_for_two']} ({location['currency']}) para dois <br>
            Culinária: {location['cuisines']} <br>
            Avaliação: {location['aggregate_rating']}/5.0</h6>''',
            max_width=300,min_width=150),
            tooltip=location["restaurant_name"],
            icon=folium.Icon(color='green', icon='home', prefix='fa')).add_to(marker_cluster)
        
        folium_static(map1,width=1024,height=600)
        return df      
    


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
df = clean_code( df )


df1 = df.copy()
#========================================
# Barra lateral
#=========================================
#image_path = 'logo.png'
image = Image.open( 'logo.png' )
st.sidebar.image( image, width = 40 )

st.sidebar.markdown('# Fome zero')

st.sidebar.markdown('## Filtros')

countries_options = st.sidebar.multiselect(
    'Escolha os países que deseja visualizar as informações',
    ["India", "Australia", "Brazil", "Canada", "Indonesia", "New Zeland", "Philippines", "Qatar", "Singapure", "South Africa",
     "Sri Lanka", "Turkey", "United Arab Emirates", "England", "United States of America"],
    default = ['Brazil', 'England', 'Qatar', 'South Africa', 'Canada', 'Australia'] )

# Filtro de países
linhas_selecionadas = df['country_code'].isin( countries_options )
df = df.loc[ linhas_selecionadas, :]


st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Matheus Serafim')


#========================================
# Layout no Streamlit
#========================================

st.markdown( '# Fome Zero!')

st.markdown('## O Melhor lugar para encontrar seu mais novo restaurante favorito!')

st.markdown('### Temos as seguintes marcas dentro da nossa plataforma:')

with st.container():

    col1, col2, col3, col4, col5 = st.columns( 5 )
    with col1:
        number_of_restaurants = len(df1.loc[:, 'restaurant_id'].unique())
        col1.metric(' Restaurantes Cadastrados ' , number_of_restaurants)

    with col2:
        number_of_countries = len(df1.loc[:, 'country_code'].unique())
        col2.metric(' Países Cadastrados ' , number_of_countries)

    with col3:
        number_of_cities = len(df1.loc[:, 'city'].unique())
        col3.metric(' Cidades Cadastradas ' , number_of_cities)

    with col4:
        total_ratings = df1.loc[:, 'votes'].sum()
        total = f'{total_ratings:,.0f}'
        total = total.replace(',','.')
        col4.metric(' Avaliações Feitas na Plataforma ' , total)

    with col5:
        total_cuisines = len(df1.loc[:, 'cuisines'].unique())
        col5.metric(' Tipos de Culinárias Oferecidas ' , total_cuisines)

with st.container():
    country_maps( df )
      

        








    
    
        