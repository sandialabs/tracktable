import tracktable.core.geomath as geomath
import datetime
from collections import namedtuple
from tracktable.analysis.symbology_kml import *

lavendar_color = 'FFB57EDC'
red_color = 'FF0000FF'
white_color = 'FFFFFFFF'

def _tab(n):
    return '\t' * n

def write_kml(fn, trajectory, segments=None, with_altitude=True):
    """
    Writes a trajectory to a kml file for viewing by other applications.
    :param fn: name of the kml file to create
    :param trajectory: trajectory to be converted
    :param segments: list of [start, stop] lists indicating subtrajectory
        boundaries
    :param with_altitude: Currently not implemented
    :return: None
    """
    if not segments:
        return

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
            # segments = list_start_stop([[0, len(trajectory)])
            color_string = white_color
        else:
            styles_dict = _create_styles_dict(trajectory, segments)

        # write the styles
        for a_style in styles_dict:
            kml_f.write(styles_dict[a_style].style_xml)

        # write the segments
        for a_segment in segments:
            kml_f.write(get_placemark_string(trajectory, a_segment,
                                             with_altitude,
                                             with_time=False))

        # write the kml footer
        kml_f.write("</Document>\n")
        kml_f.write("</kml>\n")


def _compose_traj_name(traj, suffix_str=''):
    """Gets the name of the trajectory. Appends optional suffix string."""
    return traj[0].object_id + suffix_str



def get_placemark_string(trajectory, a_segment, with_altitude=False,
                         with_time=False):
    """
    Given a trajectory and a single subtrajectory slice, return a kml string
        representing the segment
    :param trajectory: The trajectory being operated on
    :param a_segment: the subtrajectory for this Placemark
    :type a_segment: any type which has: .start, .stop
    :return: the Placemark string
    :rtype: str
    """
    sr = stackWriter()
    returnString = list(sr.push('Placemark'))
    returnString.append(sr.singleLine('name', trajectory[0].object_id))
    try:
        aDesc = a_segment.description
        returnString.append(sr.singleLine('description', aDesc))
    except AttributeError:
        pass

    if with_time:
        returnString.append( sr.push('Timespan'))
        returnString.append(sr.singleLine('begin', trajectory[a_segment.start]
                                     .timestamp.isoformat()))
        returnString.append(sr.singleLine('end', trajectory[a_segment.stop]
                                     .timestamp.isoformat()))
        returnString.append(sr.pop()) # 'Timespan'

    try:
        returnString.append(sr.singleLine('styleUrl', a_segment.styleUrl))
    except AttributeError:
        pass

    returnString.append(sr.push('gx:Track'))
    returnString.append(sr.singleLine('altitudeMode', 'absolute'))

    if with_time:
        for a_point in trajectory[a_segment.start:a_segment.stop]:
            returnString.append(
                sr.singleLine('when', a_point.timestamp.isoformat()))

    # Google Earth eats altitudes as meters, but we have them in feet,
    # so convert.
    convertFeetToMeters = 0.3048
    formatString = '{0},{1},{2}' if with_altitude \
        else '{0},{1},0.0'
    for a_point in trajectory[a_segment.start:a_segment.stop]:
        # try:
        alt = geomath.altitude(a_point) * convertFeetToMeters
        point_str = formatString.format(geomath.longitude(a_point),
                                        geomath.latitude(a_point),
                                            alt)
        # except Exception:
        #     point_str = formatString.format(geomath.longitude(a_point),
        #                        geomath.latitude(a_point))
        returnString.append(
            sr.singleLine('gx:coord', point_str))
    returnString.append(sr.pop()) # 'gx: Track'

    returnString.append(sr.pop()) # 'Placemark'
    
    return ''.join(returnString)


StyleNamedTuple = namedtuple('StyleNamedTuple', "style_id style_xml")

def _create_styles_dict(trajectory, segments):
    """Creates / returns a dictionary where the key is the style
    id, and the value is a named tuple of style_id and style_xml, the kml
    text string for that style."""
    width = 6
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
            style_xml_list.append(sr.singleLine('width', width))
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


