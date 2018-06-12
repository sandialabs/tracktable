import tracktable.core.geomath as geomath
import datetime
from collections import namedtuple

lavendar_color = 'FFB57EDC'
red_color = 'FF0000FF'
white_color = 'FFFFFFFF'

def _tab(n):
    return '\t' * n

def write_kml(fn, trajectory, segments=None, color_func=None, with_altitude=False):

    with open(fn, "w") as kml_f:

        #write the kml header
        kml_f.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
        kml_f.write("<kml xmlns=\"http://www.opengis.net/kml/2.2\" ")
        kml_f.write("xmlns:gx=\"http://www.google.com/kml/ext/2.2\" ")
        kml_f.write("xmlns:kml=\"http://www.opengis.net/kml/2.2\"\n>")
        kml_f.write("<Document>\n")

        styles_dict = {}
        width = 3.0
        if not segments:
            segments = [0, len(trajectory)]
            color_string = white_color
        elif not color_func:
            color_string = white_color
        else:
            styles_dict = _create_styles_dict(trajectory, segments, color_func)

        # write the styles
        for a_style in styles_dict:
            kml_f.write(styles_dict[a_style].style_xml)

        # write the segments
        for a_segment in segments:
            kml_f.write(get_placemark_string(trajectory, a_segment))

        # write the kml footer
        kml_f.write("</Document>\n")
        kml_f.write("</kml>\n")


def _compose_traj_name(traj, suffix_str=''):
    """Gets the name of the trajectory. Appends optional suffix string."""
    return traj[0].object_id + suffix_str

class stackWriter():
    def __init__(self, startTabDepth=0):
        self.stack = list()
        self._tab_level = startTabDepth

    def push(self, a_string):
        if '<' in a_string or '>' in a_string:
            raise ValueError("Can't have symbol bracker '<' or '>' in xml "
                "varialble name.")
        self.stack.append(a_string)
        ret_string = self.tabs + '<{0}>\n'.format(a_string)
        self._tab_level += 1
        return ret_string

    def pop(self, optionalPopString=''):
        if len(self.stack) == 0:
            return None
        self._tab_level -= 1

        poppedString = self.stack.pop()
        if len(optionalPopString) > 0 and \
                poppedString != optionalPopString:
            raise AttributeError('popped string ("{0}")not same as expected '
                'string ("{1}")'.format(poppedString, optionalPopString))

        return_string = self.tabs + '</{0}>\n'.format(poppedString)
        return return_string

    def singleLine(self, varName, varValue):
        return (self.tabs + '<{0}>{1}</{0}>\n' \
                .format(varName, str(varValue))
                )

    @property
    def tabs(self):
        return '\t' * self._tab_level


def get_placemark_string(trajectory, a_segment):

    sr = stackWriter()
    returnString = list(sr.push('Placemark'))
    returnString.append(sr.singleLine('name', trajectory[0].object_id))
    returnString.append(sr.singleLine('description', 'temp description'))

    # returnString.append( sr.push('Timespan'))
    # returnString.append(sr.singleLine('begin', trajectory[a_segment[0]]
    #                              .timestamp.isoformat()))
    # returnString.append(sr.singleLine('end', trajectory[a_segment[1]]
    #                              .timestamp.isoformat()))
    # returnString.append(sr.pop()) # 'Timespan'

    returnString.append(sr.singleLine('styleUrl', a_segment.styleUrl))

    returnString.append(sr.push('gx:Track'))
    returnString.append(sr.singleLine('altitudeMode', 'absolute'))
    # for a_point in trajectory[a_segment[0]:a_segment[1]]:
    #     returnString.append(
    #         sr.singleLine('when', a_point.timestamp.isoformat()))
    for a_point in trajectory[a_segment[0]:a_segment[1]]:
        point_str = '{},{},0.0'.format(geomath.longitude(a_point), geomath.latitude(a_point))
        returnString.append(
            sr.singleLine('gx:coord', point_str))
    returnString.append(sr.pop()) # 'gx: Track'

    returnString.append(sr.pop()) # 'Placemark'
    
    return ''.join(returnString)




StyleNamedTuple = namedtuple('StyleNamedTuple', "style_id style_xml")

def _create_styles_dict(trajectory, segments, color_func):
    width = 3
    styles_dict = {}
    style_count = 0
    for a_segment in segments:
        style_count += 1
        style_color = a_segment.color
        style_id = style_color
        a_segment.styleUrl = style_id
        if style_color not in styles_dict:
            style_xml_list = []
            style_xml_list.append("<Style id=\"{0}\">\n".format(style_id))
            sr = stackWriter(1)
            style_xml_list.append(sr.push('LineStyle'))
            style_xml_list.append(sr.singleLine("labelVisibility", 1))
            style_xml_list.append(sr.singleLine('width', 3))
            style_xml_list.append(sr.singleLine('color',style_color))
            style_xml_list.append(sr.pop('LineStyle'))
            style_xml_list.append(sr.push('LabelStyle'))
            style_xml_list.append(sr.singleLine('scale',0))
            style_xml_list.append(sr.pop('LabelStyle'))
            style_xml_list.append(sr.push("IconStyle"))
            style_xml_list.append(sr.push("Icon"))
            style_xml_list.append(sr.singleLine('href', ''))
            style_xml_list.append(sr.pop('Icon'))
            style_xml_list.append(sr.pop('IconStyle'))
            style_xml_list.append("</Style>\n")
            style_xml = ''.join(style_xml_list)
            styles_dict[style_color] = \
                StyleNamedTuple(style_id=style_id,style_xml=style_xml)
    return styles_dict


