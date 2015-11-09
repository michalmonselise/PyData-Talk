from __future__ import print_function
# tested with python2.7 and 3.4
from spyre import server
import pandas as pd

try:
    import urllib2
except ImportError:
    import urllib.request as urllib2

from bokeh.resources import INLINE
from bokeh.resources import CDN
from bokeh.embed import components

from bokeh.models.glyphs import Circle
from bokeh.models import (
    GMapPlot, Range1d, ColumnDataSource,
    PanTool, WheelZoomTool, BoxSelectTool,
    BoxSelectionOverlay, GMapOptions, HoverTool)


def getHist():
    path = 'C:/Users/Michal/Documents/Pydata/oct_hot.csv'
    histr = pd.read_csv(path)
    return histr


class WeatherSd(server.App):
    title = "Historical Weather"
    inputs = [{	"type":'slider',
                "label": 'Number of Days 1 sd Above Mean',
                "key": 'graph_type',
                "action_id": "update_data",
                'value': 1, 'max': 30
            }]

    outputs = [{"type" : "html",
                    "id" : "html_id",
                    "control_id" : "update_data",
                    "tab" : "Bokeh"}]

    controls = [{"type" : "hidden",
                    "id" : "update_data"
                }]

    tabs=['Bokeh']

    def getData(self, params):
        histr = getHist()
        return histr

    def getHTML(self,params):
        df = self.getData(params)
        self.graph_type = params['graph_type']
        df = df.ix[df['hot'] > self.graph_type,:]
        x_range = Range1d()
        y_range = Range1d()
        map_options = GMapOptions(lat=39.0, lng=-98.0, map_type="roadmap", zoom=4, styles="""
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

        lats, lons = df['lat'].values, df['lon'].values
        plot = GMapPlot(
            x_range=x_range, y_range=y_range,
            map_options=map_options,
            title="Historical Weather",
            plot_width=800
            )
        weather_source = ColumnDataSource(
            data=dict(
                lat=lats,
                lon=lons,
                fill=['purple']*len(lats)
                )
            )
        weather_circle = Circle(x="lon", y="lat", size=4, fill_color="fill", line_color=None, fill_alpha=0.1)
        plot.add_glyph(weather_source, weather_circle)
        pan = PanTool()
        wheel_zoom = WheelZoomTool()
        box_select = BoxSelectTool()
        # hover = HoverTool()
        plot.add_tools(pan, wheel_zoom, box_select)

        script, div = components(plot, CDN)
        html = "%s\n%s"%(script, div)
        return html

    def getCustomJS(self):
        return INLINE.js_raw[0]

    def getCustomCSS(self):
        return INLINE.css_raw[0]

if __name__ == '__main__':
    ml = WeatherSd()
    ml.launch(port=9088)
