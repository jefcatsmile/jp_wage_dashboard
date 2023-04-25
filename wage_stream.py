import numpy as np
import pandas as pd
import streamlit as st
import pydeck as pdk
import plotly.express as px

# ダッシュボードのタイトル
st.title('日本の賃金データダッシュボード')

# データの読み込み
df_jp_ind = pd.read_csv('csv_data/雇用_医療福祉_一人当たり賃金_全国_全産業.csv', encoding='shift_jis')
df_jp_category = pd.read_csv('csv_data/雇用_医療福祉_一人当たり賃金_全国_大分類.csv', encoding='shift_jis')
df_pref_ind = pd.read_csv('csv_data/雇用_医療福祉_一人当たり賃金_都道府県_全産業.csv', encoding='shift_jis')


# 2019年の一人当たり平均賃金のヒートマップ
st.header('2019年 : 一人当たり平均賃金のヒートマップ')

# 県庁所在地の緯度経度データを読み込み
jp_lat_lon = pd.read_csv('csv_data/pref_lat_lon.csv')
jp_lat_lon = jp_lat_lon.rename(columns={'pref_name':'都道府県名'})  #　DataFrameをマージするためにカラム名を変更
# 2019年の年齢計のデータを抽出: df_pref_map
df_pref_map = df_pref_ind[(df_pref_ind['年齢']=='年齢計') & (df_pref_ind['集計年']==2019)]
# 緯度経度のデータをマージ
df_pref_map = pd.merge(df_pref_map, jp_lat_lon, on='都道府県名')
# 一人当たり賃金について、min-maxスケーリング
df_pref_map['一人当たり賃金（相対値）'] = (df_pref_map['一人当たり賃金（万円）']-df_pref_map['一人当たり賃金（万円）'].min()) / (df_pref_map['一人当たり賃金（万円）'].max()-df_pref_map['一人当たり賃金（万円）'].min())

# 地図の表示
view = pdk.ViewState(
    longitude = 139.691648,
    latitude = 35.689185,
    zoom = 4,
    pitch = 40.5,
)

# ヒートマップレイヤー
layer = pdk.Layer(
    'HeatmapLayer',
    data = df_pref_map,
    opacity = 0.4,
    get_position = ['lon', 'lat'],
    threshold = 0.3,
    get_weight = '一人当たり賃金（相対値）'
)

# レンダリング
layer_map = pdk.Deck(layers = layer, initial_view_state=view)

# 画面表示
st.pydeck_chart(layer_map)
show_df = st.checkbox('Show DataFrame')
if show_df == True:
    st.write(df_pref_map)


# 集計年別の一人当たり賃金の推移（折れ線グラフ）
st.header('集計年別の一人当たり賃金（万円）の推移')

# 全国平均賃金
df_ts_mean = df_jp_ind[df_jp_ind['年齢']=='年齢計']
df_ts_mean = df_ts_mean.rename(columns={'一人当たり賃金（万円）': '全国一人当たり賃金（万円）'})
# 都道府県別平均賃金
df_pref_mean = df_pref_ind[df_pref_ind['年齢']=='年齢計']
pref_list = df_pref_mean['都道府県名'].unique()  # 都道府県のリストを抽出
# 都道府県のセレクトボックスを設定
option_pref = st.selectbox('都道府県', (pref_list))
df_pref_mean = df_pref_mean[df_pref_mean['都道府県名']==option_pref]
# 表示するDataFrameを結合
df_mean_line = pd.merge(df_ts_mean, df_pref_mean, on='集計年')
df_mean_line = df_mean_line[['集計年', '全国一人当たり賃金（万円）', '一人当たり賃金（万円）']]
df_mean_line = df_mean_line.set_index('集計年')

# 折れ線グラフ描画
st.line_chart(df_mean_line)


# バブルチャート（年齢階層別全国平均賃金）
st.header('▪️年齢階層別の全国一人当たり平均賃金（万円）')

# データの準備
df_mean_bubble = df_jp_ind[df_jp_ind['年齢']!='年齢計']

# plotly.expressのバブルチャートアニメーション設定
fig = px.scatter(df_mean_bubble,
                 x='一人当たり賃金（万円）',
                 y='年間賞与その他特別給与額（万円）',
                 range_x=[150, 700],
                 range_y=[0, 150],
                 size='所定内給与額（万円）',
                 size_max=38,
                 color='年齢',
                 animation_frame='集計年',
                 animation_group='年齢')

# チャートの描画
st.plotly_chart(fig)


# 産業別平均賃金（横棒グラフ）
st.header('▪️産業別の賃金推移')

# 集計年のセレクトボックス
year_list = df_jp_category['集計年'].unique().tolist()
option_year = st.selectbox('集計年',(year_list))
# 賃金種類のセレクトボックス
wage_list = ['一人当たり賃金（万円）', '所定内給与額（万円）', '年間賞与その他特別給与額（万円）']
option_wage = st.selectbox('賃金種別', (wage_list))

# 集計年データの抽出
df_mean_category = df_jp_category[df_jp_category['集計年']==option_year]
# 横軸（各種賃金）の最大値を取得
max_x = df_jp_category[option_wage].max() + 50

# 横棒グラフの設定
fig = px.bar(df_mean_category,
             x=option_wage,
             y='産業大分類名',
             color='産業大分類名',
             animation_frame='年齢',
             range_x=[0, max_x],
             orientation='h',
             width=800,
             height=500)

# 横棒グラフの描画
st.plotly_chart(fig)


# データの出典元
st.text('出典: RESAS(地域経済分析システム)')
st.text('本結果はRESAS(地域経済分析システム)を加工して作成')