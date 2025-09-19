# test all

import ulite
import os

example_png_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../examples/example_min.png')


def printe(e):
    print(e)


def generate_random_html_color():
    """
    随机生成HTML颜色编码（十六进制格式）

    返回:
        str: 格式为 '#RRGGBB' 的HTML颜色编码
    """
    import random
    # 生成三个0-255之间的随机数
    red = random.randint(0, 255)
    green = random.randint(0, 255)
    blue = random.randint(0, 255)

    # 将每个颜色分量转换为两位十六进制字符串
    hex_color = "#{:02X}{:02X}{:02X}".format(red, green, blue)

    return hex_color


def testbtn(event):
    print(event)
    event.target.setStyles(background_color = generate_random_html_color())
    event.target.setAttributes(text='jiaing')


ui = ulite.createUI()

ui.root.addChild(ulite.Label(text='wuwuwuwuw'))

btn = ulite.Button().setStyles(background_color='green')
ui.root.addChild(btn)
btn.subscribeEvent('click', testbtn)

ipt = ulite.Input()
ipt.subscribeEvent('change', printe)
ipt.subscribeEvent('keydown', printe)
ui.root.addChild(ipt)

ckb = ulite.CheckBox()
ui.root.addChild(ckb)

img = ulite.Image()
ui.root.addChild(img)
img.subscribeEvent('click', lambda e: e.target.setImage(example_png_path))
img.subscribeEvent('mousedown', printe)
img.subscribeEvent('keydown', printe)
# print(ui)
ui.show()
