from __future__ import print_function
# tested with python2.7 and 3.4
from spyre import server
import pandas as pd

try:
    import urllib2
except ImportError:
    import urllib.request as urllib2

from bokeh.resources import INLINE, CDN
from bokeh.embed import components

from bokeh.models.glyphs import Circle
from bokeh.models import (
    GMapPlot, Range1d, ColumnDataSource,
    PanTool, WheelZoomTool, BoxSelectTool,
    BoxSelectionOverlay, GMapOptions, HoverTool)


def getRain():
    path = 'C:/Users/Michal/Documents/Pydata/rain_tweets.csv'
    rain = pd.read_csv(path, delimiter='\t')
    return rain


class Tweets(server.App):
    title = "Rain Tweets"
    inputs = [{"type": 'dropdown',
               "label": 'Date',
               "options": [
                   {"label": "Choose A Date", "value": "empty"},
                   {"label": "10-27", "value": "10-27", "checked": True},
                   {"label": "10-28", "value": "10-28"},
                   {"label": "10-29", "value": "10-29"},
                   {"label": "10-30", "value": "10-30"},
                   {"label": "10-31", "value": "10-31"},
                   {"label": "11-01", "value": "11-01"},
                   {"label": "11-02", "value": "11-02"}],
               "key": 'date',
               "action_id": "update_data"
               }]

    controls = [{"type": "hidden",
                 "id": "update_data"}]

    outputs = [{"type": "html",
                "id": "html_id",
                "control_id": "update_data",
                "tab": "Bokeh"}]
    tabs = ['Bokeh']

    def getData(self, params):
        self.date = params['date']
        rain = getRain()
        rain['date'] = pd.to_datetime(rain['date'])
        return rain.loc[rain['date'].apply(lambda x: x.strftime('%m-%d')) == self.date]

    def getHTML(self, params):
        df = self.getData(params)
        tweets = df.loc[df['type'] == 'tweet']
        weather = df.loc[df['type'] == 'weather']
        weather = weather.loc[weather['value'] > 0]
        x_range = Range1d()
        y_range = Range1d()
        map_options = GMapOptions(lat=0.0, lng=0.0, map_type="roadmap", zoom=2, styles="""
            [{"featureType":"administrative","elementType":"all","stylers":[{"visibility":"on"},{"lightness":33}]},
            {"featureType":"landscape","elementType":"all","stylers":[{"color":"#f2e5d4"}]},
            {"featureType":"poi.park","elementType":"geometry","stylers":[{"color":"#c5dac6"}]},
            {"featureType":"poi.park","elementType":"labels","stylers":[{"visibility":"on"},{"lightness":20}]},
            {"featureType":"road","elementType":"all","stylers":[{"lightness":20}]},
            {"featureType":"road.highway","elementType":"geometry","stylers":[{"color":"#c5c6c6"}]},
            {"featureType":"road.arterial","elementType":"geometry","stylers":[{"color":"#e4d7c6"}]},
            {"featureType":"road.local","elementType":"geometry","stylers":[{"color":"#fbfaf7"}]},
            {"featureType":"water","elementType":"all","stylers":[{"visibility":"on"},{"color":"#acbcc9"}]}]
            """)

        pallete = ['#c1f1fe', '#85e3fd', '#5fd7f9', '#41b6fb', '#4254ff']

        lats, lons = tweets['latitude_deg'].values, tweets['longitude_deg'].values
        description = tweets['text'].values
        plot = GMapPlot(
            x_range=x_range, y_range=y_range,
            map_options=map_options,
            title="Rain Tweets",
            plot_width=950,
            plot_height=700
        )
        tweet_source = ColumnDataSource(
            data=dict(
                lat=lats,
                lon=lons,
                fill=['blue'] * len(lats),
                desc = description
            )
        )
        tweet_circle = Circle(x="lon", y="lat", size=10, fill_color="fill", line_color="black", fill_alpha=0.8)

        lats, lons = weather['latitude_deg'].values, weather['longitude_deg'].values
        bucket = max(weather['value']) / 5
        color_map = weather['value'].apply(lambda x: min(int(x / bucket), 4)).tolist()
        colors = [pallete[x] for x in color_map]
        description = weather['value'].values
        weather_source = ColumnDataSource(
            data=dict(
                lat=lats,
                lon=lons,
                fill=colors,
                desc=description
            )
        )
        weather_circle = Circle(x="lon", y="lat", size=20, fill_color="fill", line_color=None, fill_alpha=0.2)
        plot.add_glyph(weather_source, weather_circle)
        plot.add_glyph(tweet_source, tweet_circle)
        pan = PanTool()
        wheel_zoom = WheelZoomTool()
        box_select = BoxSelectTool()
        hover = HoverTool(
            tooltips=[
                ("desc", "@desc"),
                ]
        )
        plot.add_tools(pan, wheel_zoom, box_select, hover)

        script, div = components(plot, CDN)
        html = "%s\n%s" % (script, div)
        return html

    def getCustomJS(self):
        return INLINE.js_raw[0]

    def getCustomCSS(self):
        return INLINE.css_raw[0]


if __name__ == '__main__':
    ml = Tweets()
    ml.launch(port=9090)
