import jieba
import streamlit_echarts
import streamlit as st
import requests
import re
from collections import Counter
from bs4 import BeautifulSoup
from pyecharts.globals import SymbolType
from pyecharts import options as opts
from pyecharts.charts import Line, Bar, WordCloud, Pie, Funnel

#获取文本
def get_text(url):
    response = requests.get(url)
    encoding = response.encoding if 'charset' in response.headers.get('content-type', '').lower() else None
    # 使用BeautifulSoup解析响应文本，去除其中的 HTML 标签
    soup = BeautifulSoup(response.content, 'html.parser', from_encoding=encoding)
    text = soup.get_text()
    text = re.sub(pattern='[,， \n \t \r # \-<>＇《》・｜～（）＞&\*－+＂%{}=-、。.—!！?？":：；;\/\.【】()\']', repl='',
                  string=text)  # 去除符号
    words = jieba.cut(text)  # 实现分词
    ## 去除停用词
    stop_words = set()
    with open('hit_stopwords.txt', 'r', encoding='utf-8') as f: # 哈工大停用词列表
        for line in f:
            stop_words.add(line.strip())
    filtered_words = [word for word in words if word not in stop_words] # 去除停用词
    ls = filter(lambda word: len(word) > 1, filtered_words)  # 留下字长大于1的词
    word_counts = Counter(ls) # 计算词频
    threshold = 10 # 设置词频阈值
    filtered_word_freq = {word: freq for word, freq in word_counts.items() if freq >= threshold} # 过滤低频词
    top_dict = dict(sorted(filtered_word_freq.items(), key=lambda item: item[1], reverse=True)[:20])# 获取词频排名前20的词汇
    return top_dict

#展示不同类型的图像
def show_selected_chart(selected_chart,top_dict):
    x_data = list(top_dict.keys())
    y_data = list(top_dict.values())
    if selected_chart == '词云图':
        words_list = [(element, count) for element, count in top_dict.items()]
        c = (
            WordCloud()
            .add("", words_list, shape=SymbolType.DIAMOND)
            .set_global_opts(title_opts=opts.TitleOpts(title="词云图") )
        )
        streamlit_echarts.st_pyecharts(c)

    elif selected_chart == '折线图':
        c = (
            Line()
            .set_global_opts(
                title_opts=opts.TitleOpts(title="折线图"),
                tooltip_opts=opts.TooltipOpts(is_show=False),
                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)),
                yaxis_opts=opts.AxisOpts(
                    axistick_opts=opts.AxisTickOpts(is_show=True),
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
            )
            .add_xaxis(xaxis_data=x_data)
            .add_yaxis(
                series_name="词频",
                y_axis=y_data,
                symbol="emptyCircle",
                is_symbol_show=True,
                label_opts=opts.LabelOpts(is_show=False),
            )
        )
        streamlit_echarts.st_pyecharts(c)

    elif selected_chart == '饼图':
        words_list = [(element, count) for element, count in top_dict.items()]
        c = (
            Pie()
            .add("",words_list)
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        )
        streamlit_echarts.st_pyecharts(c)

    elif selected_chart == '漏斗图':
        words_list = [(element, count) for element, count in top_dict.items()]
        c = (
            Funnel()
            .add(
                series_name="",
                data_pair=words_list,
                gap=2,
                tooltip_opts=opts.TooltipOpts(trigger="item", formatter="{a} <br/>{b} : {c}%"),
                label_opts=opts.LabelOpts(is_show=True, position="inside"),
            )
        )
        streamlit_echarts.st_pyecharts(c)

    elif selected_chart == '柱状图':
        c = (
            Bar()
            .add_xaxis(xaxis_data=x_data)
            .add_yaxis("词频", y_axis=y_data)
            .set_global_opts(
                title_opts=opts.TitleOpts(title="柱状图"),
                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)),
                datazoom_opts=[opts.DataZoomOpts()],
            )
        )
        streamlit_echarts.st_pyecharts(c)

    elif selected_chart == '玫瑰图':
        c = (
            Pie()
            .add(
                "",
                [list(z) for z in zip(x_data, y_data)],
                radius=["30%", "75%"],
                center=["25%", "50%"],
                rosetype="radius",
                label_opts=opts.LabelOpts(is_show=False),
            )
            .add(
                "",
                [list(z) for z in zip(x_data, y_data)],
                radius=["30%", "75%"],
                center=["75%", "50%"],
                rosetype="area",
            )
        )
        streamlit_echarts.st_pyecharts(c)
    elif selected_chart == '面积图':
        c=(
            Line()
            .add_xaxis(x_data)
            .add_yaxis(
                series_name="词频",
                y_axis=y_data,
                areastyle_opts=opts.AreaStyleOpts(opacity=0.5),  # 设置面积图的透明度
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="面积图"),
                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)),
            )
        )
        streamlit_echarts.st_pyecharts(c)

# Streamlit 应用程序的主体部分
def main():
    st.title("交互式文本分析",)
    # 文本输入框, 用户输入文章URL
    url = st.text_input("请输入一个URL")
    if url:
        # 请求URL抓取文本内容并对文本分词,统计词频
        top_dict = get_text(url)
        # 创建一个下拉菜单，用于选择不同的图形
        selected_chart = st.sidebar.selectbox('选择图形类型', ['词云图', '折线图', '柱状图', '饼图', '玫瑰图', '漏斗图', '面积图'])
        # 根据用户的选择，展示相应的图形
        show_selected_chart(selected_chart, top_dict)
        
# 运行 Streamlit 应用程序
if __name__ == '__main__':
    main()
