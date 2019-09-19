import base64
import io
import os
import urllib

import jieba

from flask import Flask, request, send_file

import numpy as np
from PIL import Image
from wordcloud import WordCloud,ImageColorGenerator
import matplotlib.pyplot as plt

app = Flask(__name__)


@app.route('/', methods=['POST'])
def word_cloud():
    # Flask的工作目录 code
    d = app.root_path
    # Flask form post参数 文本string
    text = request.form['content']
    #Flask form post参数 gender man/woman
    gender = request.form['gender']

    font = os.path.join(d, 'simhei.ttf')

    mask_path = os.path.join(d, "{}.png".format(gender))
    mask_image = np.array(Image.open(mask_path))

    world_list_after_jieba = jieba.cut(text, cut_all=True)
    world_split = ' '.join(world_list_after_jieba)
    # 248  664 女的
    # 210  664 男的
    wc = WordCloud(collocations=False, mask=mask_image, font_path=font, max_words=200, contour_width=2,
                   contour_color='#C1DBFF', margin=2, background_color='white').generate(
        world_split)

    # store to file
    # wc.to_file(os.path.join(d, "alice.png"))

    # show
    # 设置画布 6.68 inch 默认100dpi 所以分表率位668x668 和mask图片尺寸一致
    plt.figure(figsize=(6.68,6.68))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")
    # plt.imshow(mask_image, cmap=plt.cm.gray, interpolation='bilinear')
    # plt.axis("off")
    # plt.show()

    image = io.BytesIO()
    plt.savefig(image, format='png')
    image.seek(0)  # rewind the data
    # 转换成base64
    b64png = base64.b64encode(image.read())
    image_64 = 'data:image/png;base64,' + urllib.parse.quote(b64png)
    # 直接返回 base64 png 字符串
    return image_64

# debug用的
@app.route('/debug', methods=['POST'])
def debug():
    # Flask的工作目录 code
    d = app.root_path
    text = request.form['content']
    gender = request.form['gender']

    font = os.path.join(d, 'simhei.ttf')

    mask_path = os.path.join(d, "{}_new.png".format(gender))
    mask_image = np.array(Image.open(mask_path))

    world_list_after_jieba = jieba.cut(text, cut_all=True)
    world_split = ' '.join(world_list_after_jieba)
    # 248  664 女的 #FDD3D9
    # 210  664 男的 #C1DBFF
    # contour 轮廓的意思

    wc = WordCloud(collocations=False,
                   contour_width=2,
                   mask=mask_image,
                   scale=1,
                   font_path=font, max_words=400,
                   contour_color='#FDD3D9',
                   background_color="white").generate(
        world_split)

    # store to file
    # wc.to_file(os.path.join(d, "alice.png"))
    image_colors = ImageColorGenerator(mask_image)

    # show
    plt.figure(figsize=(6.68,6.68))
    # wc.recolor(color_func=image_colors 重新着色
    plt.imshow(wc.recolor(color_func=image_colors), interpolation="bilinear")

    #plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")
    # plt.figure()
    # plt.imshow(mask_image, cmap=plt.cm.gray, interpolation='bilinear')
    # plt.axis("off")
    # plt.show()

    image = io.BytesIO()
    plt.savefig(image, format='png')
    image.seek(0)  # rewind the data

    return send_file(image, mimetype='image/png', attachment_filename='your.png', as_attachment=True)


if __name__ == '__main__':
    app.run()
