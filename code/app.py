try:  # Python 3
    from urllib.parse import quote
except ImportError:  # Python 2
    from urllib import quote
import base64
import io
import os
import jieba
from flask import Flask, request, send_file
import numpy as np
from PIL import Image
from wordcloud import WordCloud

app = Flask(__name__)


@app.route('/api/word-cloud', methods=['POST'])
def word_cloud():
    d = app.root_path
    text = request.form['content']
    gender = request.form['gender']
    is_debug = request.form['debug']
    font = os.path.join(d, 'simhei.ttf')

    mask_path = os.path.join(d, "{}_mask.png".format(gender))
    mask_image = np.array(Image.open(mask_path))

    world_list_after_jieba = jieba.cut(text, cut_all=True)
    world_split = ' '.join(world_list_after_jieba)
    # contour color
    cc = "#FDD3D9"
    if gender == 'man':
        cc = "#C1DBFF"

    # 设置png 透明背景 background_color="rgba(255, 255, 255, 0)", mode="RGBA"
    # https://github.com/amueller/word_cloud/issues/186
    wc = WordCloud(collocations=False, mask=mask_image, font_path=font, max_words=200, contour_width=1,
                   contour_color=cc, margin=0, background_color='white', width=252, height=668).generate(
        world_split)

    img = wc.to_image()
    output_buffer = io.BytesIO()
    img.save(output_buffer, format='png')

    if is_debug == '1':
        # image file response
        output_buffer.seek(0)
        return send_file(output_buffer, mimetype='image/png', attachment_filename='your.png', as_attachment=True)
    # base64 image string response
    binary_data = output_buffer.getvalue()
    base64_data = base64.b64encode(binary_data)
    image_64 = 'data:image/png;base64,' + quote(base64_data)
    return image_64


if __name__ == '__main__':
    app.run()
