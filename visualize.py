import pyecharts
from pyecharts.charts import Timeline, Bar, Pie, Grid, Scatter3D
from pyecharts import options as opts
from pyecharts.globals import ThemeType

import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from random import randint
import re

df = pd.read_csv('Colors of Van Gogh\df.csv', dtype={'Style': str, 'Genre': str})
df_reduced = pd.read_csv('Colors of Van Gogh\df_reduced.csv')

# 1.每个年份的作品数量（简单）
# 2.每个风格的作品数量
# 3.每个种类的不同作品数量且有不同年份参照finance indices
# 4.色彩选用散点图 并拼接成一个rgb色谱


# 1.每个年份的作品数量
year = df["Year"].value_counts().rename_axis('year').reset_index(name='counts')
year = year.sort_values(by='year')

a = Bar(init_opts=opts.InitOpts(theme=ThemeType.VINTAGE))
a.add_xaxis(year.year.tolist())
a.add_yaxis("作品数量", year.counts.tolist())
a.set_global_opts(title_opts=opts.TitleOpts(title="梵高每个年份画作数量", subtitle="19120269金熙闻"),
                  toolbox_opts=opts.ToolboxOpts(),
                  xaxis_opts=opts.AxisOpts(name_location="start", axislabel_opts=opts.LabelOpts(font_size=9)),
                  datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],
                  legend_opts=opts.LegendOpts(is_show=False))
a.render("每个年份数量.html")

# print(year.year.tolist())
# print(year.counts.tolist())

# 2.每个风格的作品数量
style = df["Style"].value_counts().rename_axis('style').reset_index(name='counts')
style_name = style['style'].tolist()

b = Bar(init_opts=opts.InitOpts(theme=ThemeType.VINTAGE))
b.add_xaxis(style_name)
b.add_yaxis("作品数量", style.counts.tolist())
b.set_global_opts(title_opts=opts.TitleOpts(title="梵高每个类型画作数量", subtitle="金熙闻19120269"),
                  toolbox_opts=opts.ToolboxOpts(),
                  legend_opts=opts.LegendOpts(is_show=False),
                  xaxis_opts=opts.AxisOpts(name_location="start", axislabel_opts=opts.LabelOpts(font_size=9)),
                  datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")],

                  )
b.render("每个风格数量.html")
# print(style_name)
# print(style.counts.tolist())

#3.每个种类的不同作品数量且有不同年份参照finance indices
style = df["Style"].value_counts().rename_axis('style').reset_index(name='counts')
style_name=style['style'].tolist()

def get_year_overlap_chart(year:int)->Bar:
    processed_style = df[df['Year'] == year]
    processed_style = processed_style['Style'].value_counts()
    processed_style = processed_style.to_frame()
    processed_style = pd.DataFrame(processed_style.values.T, columns=processed_style.index)
    standarddf = pd.DataFrame(
        columns=['Post-Impressionism', 'Realism', 'Neo-Impressionism', 'Japonism', 'Cloisonnism', 'Impressionism'],
        data=[])
    processed_style = processed_style.append(standarddf, sort=True)
    processed_style.fillna(0, inplace=True)
    order = ['Post-Impressionism', 'Realism', 'Neo-Impressionism', 'Japonism', 'Cloisonnism', 'Impressionism']
    processed_style = processed_style[order]
    res = processed_style.values.tolist()[0]

    bar=(
        Bar(init_opts=opts.InitOpts(theme=ThemeType.VINTAGE))
        .add_xaxis(xaxis_data=style_name)
        .add_yaxis(
            series_name = "作品数量",
            y_axis=res,
            label_opts=opts.LabelOpts(is_show=False)
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="{}梵高作品类型".format(year), subtitle="金熙闻19120269"
            ),
            tooltip_opts=opts.TooltipOpts(
                is_show=True, trigger="axis", axis_pointer_type="shadow"
            ),
        )
    )
    pie=(
        Pie(init_opts=opts.InitOpts(theme=ThemeType.VINTAGE))
        .add(
            series_name="作品风格占比",
            data_pair=[list(z) for z in zip(style_name,res)],
            center=["75%", "35%"],
            radius="28%"
        )
        .set_series_opts(tooltip_opts=opts.TooltipOpts(is_show=True, trigger="item"))
    )
    return bar.overlap(pie)
timeline = Timeline(init_opts=opts.InitOpts(width="1600px", height="800px",theme=ThemeType.VINTAGE))

for y in year.year.tolist():
    timeline.add(get_year_overlap_chart(year=y), time_point=str(y))

timeline.add_schema(is_auto_play=True, play_interval=1000)
timeline.render("3.html")

# # 4.词云
# word=''
# for name in df['Name']:
#     word=word+' '+name
# print(word)
# def random_color_func(word=None, font_size=None, position=None,
#                       orientation=None, font_path=None, random_state=None):
#     h = randint(120,250)
#     s = int(100.0 * 255.0 / 255.0)
#     l = int(100.0 * float(random_state.randint(70, 120)) / 255.0)
#     return "hsl({}, {}%, {}%)".format(h, s, l)
# my_wordcloud=WordCloud(width=6000, height=2400, background_color='white',
#                       color_func=random_color_func,
#                       normalize_plurals=False).generate(word)
# plt.imshow(my_wordcloud)
# plt.axis("off")
# plt.show()

# 5.色谱图
def color(value):
  digit = list(map(str, range(10))) + list("ABCDEF")
  if isinstance(value, tuple):
    string = '#'
    for i in value:
      a1 = i // 16
      a2 = i % 16
      string += digit[a1] + digit[a2]
    return string
  elif isinstance(value, str):
    a1 = digit.index(value[1]) * 16 + digit.index(value[2])
    a2 = digit.index(value[3]) * 16 + digit.index(value[4])
    a3 = digit.index(value[5]) * 16 + digit.index(value[6])
    return (a1, a2, a3)

def cut_text(text,lenth):
    textArr = re.findall('.{'+str(lenth)+'}', text)
    textArr.append(text[(len(textArr)*lenth):])
    textArr.pop()
    return textArr

color_list=[]
rgb_list=[]
for i in range(0,1931):
    temp_color=df['Colors'][i].replace('(','').replace(')','').replace("'",'').replace(',','').replace(' ','').strip()
    for colors in cut_text(temp_color,7):
        rgb_list.append(colors)
        color_list.append(color(colors))

scatter = (
    Scatter3D(init_opts=opts.InitOpts(width="1440px", height="720px"))  # 初始化
        .add("", color_list,
             grid3d_opts=opts.Grid3DOpts(width=100, height=100, depth=100),
             xaxis3d_opts=opts.Axis3DOpts(
                 name='R',
                 type_="value",
                 color=rgb_list,
                 # textstyle_opts=opts.TextStyleOpts(color="#fff"),
             ),
             yaxis3d_opts=opts.Axis3DOpts(
                 name='G',
                 type_="value",
                 # textstyle_opts=opts.TextStyleOpts(color="#fff"),
             ),
             zaxis3d_opts=opts.Axis3DOpts(
                 name='B',
                 type_="value",
                 # textstyle_opts=opts.TextStyleOpts(color="#fff"),
             )
             )

        # 设置全局配置项
        .set_global_opts(
        title_opts=opts.TitleOpts(title="色谱图", subtitle="19120269金熙闻"),
        visualmap_opts=opts.VisualMapOpts(
            max_=256,
            min_=0,
            pos_top=50,
            range_color=rgb_list
        )
    )
        .render("色谱图.html")
)



# processed_style=df[df['Year'] == 1882]
# processed_style=processed_style['Style'].value_counts()
# processed_style=processed_style.to_frame()
# processed_style=pd.DataFrame(processed_style.values.T,columns=processed_style.index)
# standarddf = pd.DataFrame(
#     columns=['Post-Impressionism', 'Realism', 'Neo-Impressionism', 'Japonism', 'Cloisonnism', 'Impressionism'],
#     data=[])
# result=processed_style.append(standarddf,sort=True)
# result.fillna(0,inplace=True)
# order=['Post-Impressionism', 'Realism', 'Neo-Impressionism', 'Japonism', 'Cloisonnism', 'Impressionism']
# result=result[order]
# res=result.values.tolist()[0]
# print(res)


# list_sort_year = df[df['Year'] == 1876]['Year'].groupby(df['Style']).count()
# list_sort_year["Post-Impressionism"]
# print(df[df['Year'] == 1876]['Year'].groupby(df['Style']).count()["Post-Impressionism"])
#
