import base64
import hashlib
import io
import logging
import os
import time

from selenium import webdriver

try:  # Python 3
    from urllib.parse import quote
except ImportError:  # Python 2
    from urllib import quote

import jieba

from flask import Flask, request, send_file

import numpy as np
from PIL import Image
from wordcloud import WordCloud, ImageColorGenerator
import matplotlib.pyplot as plt

app = Flask(__name__)


@app.route('/', methods=['POST'])
def hello_world():
    d = app.root_path
    text = request.form.get('content', '')
    gender = request.form.get('gender', 'man')
    is_debug = request.form.get('debug', "0")
    font = os.path.join(d, 'simhei.ttf')

    mask_path = os.path.join(d, "{}_mask.png".format(gender))
    mask_image = np.array(Image.open(mask_path))

    world_list_after_jieba = jieba.cut(text, cut_all=True)
    world_split = ' '.join(world_list_after_jieba)
    cc = "#FDD3D9"
    if gender == 'man':
        cc = "#C1DBFF"
    wc = WordCloud(collocations=False, mask=mask_image, font_path=font, max_words=200, contour_width=0,
                   contour_color=cc, margin=0,
                   mode='RGBA',
                   background_color='rgba(255, 255, 255, 0)',
                   width=252, height=668).generate(world_split)
    img = wc.to_image()
    output_buffer = io.BytesIO()
    img.save(output_buffer, format='png')
    output_buffer.seek(0)

    if is_debug == '1':
        return send_file(output_buffer, mimetype='image/png', attachment_filename='your.png', as_attachment=True)
    binary_data = output_buffer.getvalue()
    base64_data = base64.b64encode(binary_data)
    image_64 = 'data:image/png;base64,' + quote(base64_data)
    return image_64


@app.route('/ss', methods=['GET'])
def screenshot():
    id = request.args.get('i', "0")
    url = request.args.get('u', '')
    if not url.startswith('http'):
        return "url u 参数不是合法的URL地址"
    key = hashlib.md5(url.encode('utf-8')).hexdigest()
    screen_shot_dir = "/data/screen_shot"
    image_name = id + "_" + key + ".png"
    image_path = os.path.join(screen_shot_dir, image_name)
    d = app.root_path
    if not os.path.isfile(image_path):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--window-size=1024,768')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        browser = webdriver.Chrome(chrome_options=chrome_options)
        browser.set_window_size(1024, 768)
        browser.get(url)
        time.sleep(2)
        if not browser.save_screenshot(image_path):
            image_path = os.path.join(d, 'image_error.jpg')
        browser.close()
    return send_file(image_path, mimetype='image/png', attachment_filename=image_name, as_attachment=False)


@app.route('/debug', methods=['POST'])
def debug():
    d = app.root_path
    text = request.form['content']
    gender = request.form['gender']

    font = os.path.join(d, 'PingFangMedium.ttf')

    mask_path = os.path.join(d, "{}.png".format(gender))
    mask_image = np.array(Image.open(mask_path))

    world_list_after_jieba = jieba.cut(text, cut_all=True)
    world_split = ' '.join(world_list_after_jieba)

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
    plt.figure(figsize=(3, 6.68))
    plt.imshow(wc.recolor(color_func=image_colors), interpolation="bilinear")

    # plt.imshow(wc, interpolation='bilinear')
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
    app.debug = True
    handler = logging.FileHandler('/data/log/flask.log')
    app.logger.addHandler(handler)
    app.run()
