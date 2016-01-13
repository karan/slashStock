import locale
import math

from wand.image import Image
from wand.color import Color
from wand.drawing import Drawing


WIDTH = 968
HEIGHT = 484

ZOOM_MULTIPLE = 1.7

GREEN = '#093'
RED = '#d14836'
GREY = '#666666'
BLACK = '#000000'
WHITE = '#ffffff'
BG_GREEN = '#4A913C'

WATERMARK_HEIGHT = 50


def comma(n):
    locale.setlocale(locale.LC_ALL, 'en_US')
    n = float(n)
    return locale.format("%.02f", n, grouping=True)


def millify(n):
    n = float(n)
    if n < 10 ** 6:
        return comma(n)[:-3]

    millnames = ['', '', 'M', 'B', 'T']
    millidx = max(0, min(len(millnames) - 1,
                         int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))))

    return '{:.01f}{}'.format(n / 10 ** (3 * millidx), millnames[millidx])


def create_image(share, chart_file, out_file):
    # Unpack the quote
    price = share['price']
    change = share['change']
    change_percent = share['change_percent']
    open_price = share['open_price']
    market_cap = share['market_cap']
    year_low = share['year_low']
    year_high = share['year_high']
    day_low = share['day_low']
    day_high = share['day_high']
    volume = share['volume']
    pe_ratio = share['pe_ratio']


    with Color('white') as bg:
        with Image(width=WIDTH, height=HEIGHT, background=bg) as img:
            with Image(filename=chart_file) as chart_img:
                w = int(chart_img.size[0] * ZOOM_MULTIPLE)
                h = int(chart_img.size[1] * ZOOM_MULTIPLE)

                with Drawing() as draw:

                    draw.font = 'fonts/arial.ttf'

                    # Draw watermark
                    draw.fill_color = Color(BG_GREEN)
                    draw.rectangle(left=0, top=HEIGHT-WATERMARK_HEIGHT, right=WIDTH, bottom=HEIGHT)
                    draw(img)
                    draw.font_size = 20
                    draw.fill_color = Color(WHITE)
                    draw.text(WIDTH-150, HEIGHT-WATERMARK_HEIGHT+50, '@slashStock')

                    # Draw the chart
                    draw.composite(operator='add', left=0, top=0,
                        width=w, height=h, image=chart_img)

                    # Draw current price
                    draw.font_size = 40
                    draw.fill_color = Color(BLACK)
                    draw.text(w + 20, 60, '%s' % price)
                    price_w = int(draw.get_font_metrics(img, price).text_width)

                    # Draw change
                    draw.font_size = 25
                    draw.fill_color = Color(GREEN) if '+' in change else Color(RED)
                    draw.text(w + price_w + 35, 60, '%s (%s%%)' % (change, change_percent))

                    # Draw market cap
                    draw.font_size = 20
                    draw.fill_color = Color(GREY)
                    draw.text(w + 50, 110, 'Mkt cap')
                    draw.fill_color = Color(BLACK)
                    draw.text(w + 150, 110, '%s' % market_cap)

                    # Draw range
                    draw.font_size = 20
                    draw.fill_color = Color(GREY)
                    draw.text(w + 50, 140, 'Range')
                    draw.fill_color = Color(BLACK)
                    draw.text(w + 150, 140, '%s - %s' % (day_low, day_high))

                    # 52-week range
                    draw.font_size = 20
                    draw.fill_color = Color(GREY)
                    draw.text(w + 50, 170, '52 week')
                    draw.fill_color = Color(BLACK)
                    draw.text(w + 150, 170, '%s - %s' % (year_low, year_high))

                    # Open price
                    draw.font_size = 20
                    draw.fill_color = Color(GREY)
                    draw.text(w + 50, 200, 'Open')
                    draw.fill_color = Color(BLACK)
                    draw.text(w + 150, 200, '%s' % open_price)

                    # Volume
                    draw.font_size = 20
                    draw.fill_color = Color(GREY)
                    draw.text(w + 50, 230, 'Volume')
                    draw.fill_color = Color(BLACK)
                    draw.text(w + 150, 230, '%s' % millify(volume))

                    # P/E ratio
                    draw.font_size = 20
                    draw.fill_color = Color(GREY)
                    draw.text(w + 50, 260, 'P/E')
                    draw.fill_color = Color(BLACK)
                    draw.text(w + 150, 260, '%s' % (comma(pe_ratio) if pe_ratio != '-' else pe_ratio))

                    draw(img)
                    img.save(filename=out_file)
