# coding=utf-8
import pandas as pd
import pkuseg
from tqdm import tqdm
from collections import Counter
from string import punctuation as punctuation_en
from zhon.hanzi import punctuation as punctuation_zh


################################## 处理 #####################################

# 标点
punc = set(punctuation_en + punctuation_zh)


def is_punc(word):
    return bool(set(word) & punc)

# 停用词
# TODO
with open('stopwords/中文停用词表.txt', 'r', encoding='utf-8') as f:
    stopwords =[line.strip() for line in f]
    stopwords += [
        '手机', '没',
    ]
    stopwords = set(stopwords)



def is_stopword(word):
    return word in stopwords

# 分词
seg = pkuseg.pkuseg('web')


def seg_text(text):
    words = seg.cut(text)
    return list(filter(lambda x: not is_punc(x) and not is_stopword(x), words))

#############################################################################
# 读取
def read_file(fname):
    return pd.read_csv(fname, '\t')


# 提取
def get_high(datas):
    return datas[datas['评分'] >= 4]


def get_medium(datas):
    return datas[datas['评分'] == 3]


def get_low(datas):
    return datas[datas['评分'] <= 2]


#############################################################################
from PIL import Image
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from wordcloud import WordCloud, ImageColorGenerator

def create_wordcloud(word_freq_dict, mask_img_fname, out_img_fname):
    mask_img = np.array(Image.open(mask_img_fname))

    wc = WordCloud(background_color="white", max_words=2000, mask=mask_img, font_path='STKAITI.TTF')
    # generate word cloud
    wc.generate_from_frequencies(word_freq_dict)

    # 按照图片颜色渲染
    # bimgColors=ImageColorGenerator(mask_img)
    # wc.recolor(color_func=bimgColors)

    wc.to_file(out_img_fname)
    # show
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.show()


#############################################################################

# 用户昵称	几天后追加评论	评论内容	几天后评论	产品颜色	购买时间	内存大小	评分	客户端	用户等级名称	用户省份	点赞数	回复数	手机型号
for dname in ['iqoo']:  # , 'nex', 's1', 'u1', 'x27', 'z5x']:
    for dtype in ['high']:  # , 'medium', 'low']:
        fname = 'comment_jd/{}/data_{}.csv'.format(dname, dtype)
        datas = read_file(fname)
        
        counter_high = Counter()
        
        # data = get_high(datas) #好评
        # data = get_medium(datas) #中评
        # data = get_low(datas) #差评
        data = datas # 所有

        for content in tqdm(data['评论内容']):
            words = seg_text(content)
            counter_high.update(words)
        print(counter_high.most_common(20))

        create_wordcloud(dict(counter_high), 'images/小v_mask2.jpg', 'wc_iqoo.jpg')

        # print(datas['用户昵称'][0])
        # print(datas.keys()[1])
        # print(datas.shape)
        # print(seg_text(datas['评论内容'][5]))
        # print(type(datas['评分'][0]))
        # print(datas[datas['评分']==1]['评论内容'])
