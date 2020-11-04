from underground import metadata, SubwayFeed
from PIL import Image, ImageFont, ImageDraw
from inky import InkyPHAT
from functools import reduce
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

inky_display = InkyPHAT("yellow")
inky_display.set_border(inky_display.WHITE)
font = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
small_font = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 8)

API_KEY = os.getenv('MTA_API_KEY')

Q_ROUTE = 'Q'
B_ROUTE = 'B'
STATIONS = [
    {"route": Q_ROUTE, "station": 'D24N', "direction": 'North'},
    {"route": B_ROUTE, "station": 'D24N', "direction": 'North'}
]


def get_station_times(station_data):
    route = station_data.get('route')
    station = station_data.get('station')
    feed = SubwayFeed.get(route, api_key=API_KEY)
    stops = feed.extract_stop_dict().get(route, dict()).get(station, [])
    labeled_stops = [{"route": route, "time": t} for t in stops]
    return labeled_stops


def draw_route(draw, route, y):
    bg_color = inky_display.YELLOW if route == Q_ROUTE else inky_display.WHITE
    fg_color = inky_display.WHITE if route == Q_ROUTE else inky_display.BLACK
    outline = inky_display.YELLOW if route == Q_ROUTE else inky_display.BLACK
    x_pos = 18 if route == Q_ROUTE else 20
    draw.ellipse([(12, y), (42, y+30)], bg_color, outline)
    draw.text((x_pos, y + 1), route, fg_color, font)


def draw_time(draw, time, y):
    draw.text((48, y), time.strftime('%-I:%M %p'), inky_display.BLACK, font)


def draw_row(draw, arrival, y):
    draw_route(draw, arrival.get('route', ''), y)
    draw_time(draw, arrival.get('time', ''), y)


def draw_updated(draw):
    message = 'Updated: {}'.format(datetime.now().strftime('%-I:%M:%S %p'))
    w, h = small_font.getsize(message)

    x = (inky_display.WIDTH - w)
    y = (inky_display.HEIGHT - h)
    draw.text((x, y,), message, inky_display.BLACK, small_font)


def print_to_inky(train_one, train_two):
    img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
    draw = ImageDraw.Draw(img)
    draw.line([(0, inky_display.HEIGHT / 2), (inky_display.WIDTH,
                                              inky_display.HEIGHT / 2)], inky_display.BLACK, 1)
    draw_row(draw, train_one, 14)
    draw_row(draw, train_two, inky_display.HEIGHT - 42)
    draw_updated(draw)
    inky_display.set_image(img)
    inky_display.show()


def main():
    times = reduce(lambda x, y: x+y,
                   [get_station_times(station) for station in STATIONS])
    sorted_times = sorted(times, key=lambda k: k['time'])
    first, second, *_ = sorted_times
    print_to_inky(first, second)


main()
