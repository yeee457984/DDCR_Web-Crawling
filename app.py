import os
import pandas as pd
import jieba
from wordcloud import WordCloud
from io import BytesIO
import base64
from crawl import fetch
import matplotlib.pyplot as plt
import dash
from dash import dcc, html, Output, Input

# Dash用
import plotly.io as pio
pio.orjson = None

# 解決 matplotlib 中文字型
plt.rcParams['font.family'] = ['Heiti TC']

# 偵測中文字型路徑
possible_fonts = [
    '/System/Library/Fonts/STHeiti Medium.ttc',
    '/System/Library/Fonts/PingFang.ttc',
    '/Library/Fonts/Microsoft JhengHei.ttf',
    'C:/Windows/Fonts/msjh.ttc',
    './msjh.ttc'
]

font_path = None
for font in possible_fonts:
    if os.path.exists(font):
        font_path = font
        break

if font_path is None:
    raise ValueError("⚠️ 沒找到中文字型，請確認系統或專案資料夾內有中文字型檔。")

# 讀取停用詞表
def get_stopwords(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        stopwords = set([line.strip() for line in f])
    return stopwords

stopwords = get_stopwords('stopword.txt')

# 爬文章資料
article = []
for i in range(10):
    article += fetch(i)
arti_data = pd.DataFrame(article)

# 整理資料
grouped_text = arti_data.groupby('forum')['title'].apply(lambda x: ' '.join(x)).reset_index()

# Dash App
app = dash.Dash(__name__)
server = app.server  # <-- 重點！給 gunicorn 用

app.layout = html.Div([
    html.H1('論壇文章文字雲分析'),

    dcc.Dropdown(
        id='forum-dropdown',
        options=[{'label': f, 'value': f} for f in grouped_text['forum']],
        value=grouped_text['forum'].iloc[0],
        clearable=False
    ),

    html.Img(id='wordcloud-img', style={'width': '60%', 'marginTop': '20px'})
])

# Callback 生成文字雲
@app.callback(
    Output('wordcloud-img', 'src'),
    Input('forum-dropdown', 'value')
)
def update_wordcloud(selected_forum):
    text = grouped_text[grouped_text['forum'] == selected_forum]['title'].values[0]
    words = jieba.lcut(text)
    filtered_words = [w for w in words if w not in stopwords and len(w.strip()) > 1]
    word_freq = pd.Series(filtered_words).value_counts().to_dict()

    wc = WordCloud(
        font_path=font_path,
        background_color='white',
        width=800, height=400
    ).generate_from_frequencies(word_freq)

    img = BytesIO()
    wc.to_image().save(img, format='PNG')
    img.seek(0)
    encoded = base64.b64encode(img.read()).decode()

    return f'data:image/png;base64,{encoded}'

if __name__ == '__main__':
    app.run(debug=True)
