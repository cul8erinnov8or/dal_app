import streamlit as st
import pandas as pd
import numpy as np
import random
# from google.oauth2.service_account import Credentials
# import gspread
# from gspread_dataframe import get_as_dataframe, set_with_dataframe
import folium
from streamlit_folium import folium_static
from PIL import Image
from datetime import datetime
import time
from geopy.distance import geodesic

# scopes = [
#     'https://www.googleapis.com/auth/spreadsheets',
#     'https://www.googleapis.com/auth/drive'
# ]

# credentials = Credentials.from_service_account_file(
#     'C:/Users/eplci/Downloads/pivotal-sprite-406613-761b24952379.json',
#     scopes=scopes
# )

# gc = gspread.authorize(credentials)
# spreadsheet_url = '(https://docs.google.com/spreadsheets/d/1sUX1ad891fYIIGrQzPTmXBgEfsaI-8T5zVv8bp5AbIc/edit#gid=0)'
# spreadsheet = gc.open_by_url(spreadsheet_url)
# worksheet = spreadsheet.sheet1


st.title('昼飯どうする？')
st.header('そんなあなたに、昼飯決める君！！！！')
st.text('質問に答えてね')

q1 = st.selectbox(label = '一人で行く？複数人？', options = ['一人', '複数人'])
q2 = st.selectbox(label = '何系食べたい？', options = ['こだわらない（ランダムに出力します）', '定食', '中華', '多国籍', '洋食', '焼肉屋', 'うどん', 'カレー', 'カツ', '寿司', 'ラーメン', '牛丼'])
q3 = st.selectbox(label = '重視するのは？', options = ['ガッツリ', 'おしゃれ', 'コスパ'])
button = st.button('送信')

# df_read = get_as_dataframe(worksheet)
df_read = pd.read_csv('dal.csv', dtype = str)
df_read = df_read.dropna(subset = 'id').copy()

dal_loc = [35.65918493355944, 139.75321656558702]
df_read['distance'] = ''
for i, row in df_read.iterrows():
    df_read.at[i, 'distance'] = geodesic(dal_loc, (row['lat'], row['lon'])).m

if q2 == 'こだわらない（ランダムに出力します）':
    if button:
        iteration = st.empty()
        bar = st.progress(0)
        for i in range(100):
            iteration.text(f'おすすめのレストランを探しています... {i+1} / 100')
            bar.progress(i+1)
            time.sleep(0.01)
        
        random_number = int(random.uniform(1, len(df_read)))
        the_lat = df_read.loc[df_read['id'] == random_number, 'lat'].values[0]
        the_lon = df_read.loc[df_read['id'] == random_number, 'lon'].values[0]
        the_restaurant = df_read.loc[df_read['id'] == random_number, 'name'].values[0]
        the_genre = df_read.loc[df_read['id'] == random_number, 'genre'].values[0]
        the_remarks = df_read.loc[df_read['id'] == random_number, 'remarks'].values[0]
        the_distance = int(df_read.loc[df_read['id'] == random_number, 'distance'].values[0])
        
        f"""
            選ばれたレストランは
            
            ### {the_restaurant}
            
            です。
            
            - ジャンル：{the_genre}
            - ひとこと：{the_remarks}
            - DALからの距離：{the_distance}メートル
            """
        
        restaurant_pic = Image.open(f'dal_pic/{the_restaurant}.jpg')
        st.image(restaurant_pic)
        st.caption(the_restaurant)
        
        map_centre = [the_lat, the_lon]
        map = folium.Map(location = map_centre, tiles = 'openstreetmap', zoom_start = 18)
        for i, dt in df_read.iterrows():
            folium.Marker(location = [dt['lat'], dt['lon']], popup = '{}'.format(dt['name'])).add_to(map)
        folium.Marker(location = map_centre, popup = '{}'.format(df_read['name']), icon = folium.Icon(color = 'red')).add_to(map)
        folium_static(map)

        st.write('以下はあなたが気に入りそうなレストランの候補です。')
        df = df_read[['name', 'address', 'remarks']].head()
        st.dataframe(df)
    
else:
    if button:
        iteration = st.empty()
        bar = st.progress(0)
        for i in range(100):
            iteration.text(f'おすすめのレストランを探しています... {i+1} / 100')
            bar.progress(i+1)
            time.sleep(0.01)
        
        col = list(df_read.columns)
        del col[:3]
        del col[-5:]

        df_q = pd.DataFrame(columns = col)
        df_q.loc['q'] = 0
        df_q.loc['q', q1] = 1
        df_q.loc['q', q2] = 1
        df_q.loc['q', q3] = 1
        df = pd.concat([df_read, df_q])
        
        df_vec = df[col]
        item_vectors = np.array(df_vec)
        norm = np.matrix(np.linalg.norm(item_vectors, axis=1))
        sim_mat = np.array(np.dot(item_vectors, item_vectors.T)/np.dot(norm.T, norm))

        the_restaurant = np.argsort(sim_mat[-1])[::-1][1:2]
        df_top = df[df['id'].isin(the_restaurant)]
        the_restaurant = df_top['name'].values[0]
        the_lat = df_top['lat'].values[0]
        the_lon = df_top['lon'].values[0]
        the_genre = df_top['genre'].values[0]
        the_remarks = df_top['remarks'].values[0]
        the_distance = int(df_top['distance'].values[0])
        
        
        f"""
        選ばれたレストランは
        
        ### {the_restaurant}
        
        です。
        
        - ジャンル：{the_genre}
        - ひとこと：{the_remarks}
        - DALからの距離：{the_distance}メートル
        """
        
        restaurant_pic = Image.open(f'dal_pic/{the_restaurant}.jpg')
        st.image(restaurant_pic)
        st.caption(the_restaurant)

        map_centre = [the_lat, the_lon]
        map = folium.Map(location = map_centre, tiles = 'openstreetmap', zoom_start = 18)
        for i, dt in df_read.iterrows():
            folium.Marker(location = [dt['lat'], dt['lon']], popup = '{}'.format(dt['name'])).add_to(map)
        folium.Marker(location = map_centre, popup = '{}'.format(df['name']), icon = folium.Icon(color = 'red')).add_to(map)
        folium_static(map)
        

        top5 = np.argsort(sim_mat[-1])[::-1][2:6]
        st.write('以下はあなたが気に入りそうなレストランの候補です。')
        df = df[df['id'].isin(top5)][['name', 'address', 'remarks']]
        st.dataframe(df)

    