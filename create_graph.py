from wand.image import Image
from wand.color import Color
from wand.drawing import Drawing

WATERMARK_HEIGHT = 30
QUOTE_HEIGHT = 50

WIDTH = 968
HEIGHT = 484


price = '716.03'
change = '1.56'
change_percent = '+0.22'
market_cap = '496.99B'
year_low = '486.23'
year_high = '779.98'
day_low = '703.54'
day_high = '718.85'
volume = '19391100'

# chart (x, y, w, h) = 0, 0, 826, 484


with Color('white') as bg:
    with Image(width=WIDTH, height=HEIGHT, background=bg) as img:
        with Image(filename='goog.png') as chart_img:
            w = chart_img.size[0]
            h = chart_img.size[1]

            new_chart_w = int(float(HEIGHT - WATERMARK_HEIGHT - QUOTE_HEIGHT) / h * w)
            new_chart_h = HEIGHT - WATERMARK_HEIGHT - QUOTE_HEIGHT

            # chart_img.resize(new_chart_w, new_chart_h)

            with Drawing() as draw:

                # Draw the chart
                draw.composite(operator='add', left=0, top=QUOTE_HEIGHT,
                    width=new_chart_w, height=new_chart_h, image=chart_img)

                draw.font = '/Library/Fonts/Arial.ttf'

                # Draw watermark
                draw.font_size = 20
                draw.text(15, QUOTE_HEIGHT + new_chart_h + 10, '@slashStock')

                # Draw current price, change
                draw.font_size = 30
                draw.font_weight = 800
                draw.gravity = 'north_west'
                draw.text(15, 15, '$%s %s (%s%%)' % (price, change, change_percent))

                draw(img)
                img.save(filename='goog-final.png')
