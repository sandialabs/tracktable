import tracktable.core.geomath as geomath
import datetime
from collections import namedtuple
from tracktable.analysis.symbology_kml import *
import networkx as nx
from tracktable.analysis.nx_graph import depth_level_x_gen
import statistics

lavendar_color = 'FFB57EDC'
red_color = 'FF0000FF'
white_color = 'FFFFFFFF'

def _tab(n):
    return '\t' * n

def write_kml_graph(fn, trajectory, g: nx.DiGraph, with_altitude=True):
    """
    Writes a trajectory to a kml file for viewing by other applications.
    :param fn: name of the kml file to create
    :param trajectory: trajectory to be converted
    :param g: NetworkX DiGraph (tree) containing the nodes to be written
    :param with_altitude: Currently not implemented
    :return: None
    """
    if not g:
        return

    with open(fn, "w") as kml_f:

        #write the kml header
        kml_f.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
        kml_f.write("<kml xmlns=\"http://www.opengis.net/kml/2.2\" ")
        kml_f.write("xmlns:gx=\"http://www.google.com/kml/ext/2.2\" ")
        kml_f.write("xmlns:kml=\"http://www.opengis.net/kml/2.2\"\n>")
        kml_f.write("<Document>\n")

        level_2_list = sorted(depth_level_x_gen(g, 2),
                              key=lambda n: n.start)
        styles_dict = _create_styles_dict(trajectory, level_2_list)

        # write the styles
        for a_style in styles_dict:
            kml_f.write(styles_dict[a_style])

        # write the segments
        for a_segment in level_2_list:
            write_str = get_placemark_string(trajectory, a_segment,
                                             with_altitude,
                                             with_time=False)
            if write_str:
                kml_f.write(write_str)

        # write the kml footer
        kml_f.write("</Document>\n")
        kml_f.write("</kml>\n")

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

def _interpolate_points(point1: tuple, point2: tuple) -> tuple:
    long = statistics.mean([point1[0], point2[0]])
    lat = statistics.mean([point1[1], point2[1]])
    alt1 = geomath.altitude(point1)
    alt2 = geomath.altitude(point2)
    alt = statistics.mean([alt1, alt2])
    return long, lat, alt


def get_placemark_string(trajectory, a_segment,
                         with_altitude=False,
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
    if not a_segment:
        return

    altitude_mode = 'absolute'
    altitude_list = []
    for a_pt in trajectory:
        try:
            alt = geomath.altitude(a_pt)
        except AttributeError:
            alt = 0
        altitude_list.append(alt)
    if statistics.median(altitude_list) < 100.0:
        altitude_mode = 'relative'

    sr = stackWriter()
    returnString = list(sr.push('Placemark'))
    returnString.append(sr.singleLine('name', trajectory[0].object_id))

    try:
        a_desc = a_segment.description
        if '<' in a_desc:
            a_desc = "Description not available."
        returnString.append(sr.singleLine('description', a_desc))
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
        # returnString.append(sr.singleLine('styleUrl', a_segment.styleUrl))
        returnString.append(sr.singleLine('styleUrl', a_segment.category.name))
    except AttributeError:
        pass

    returnString.append(sr.push('gx:Track'))

    if with_time:
        for a_point in trajectory[a_segment.start:a_segment.stop]:
            returnString.append(
                sr.singleLine('when', a_point.timestamp.isoformat()))

    # Google Earth eats altitudes as meters, but we have them in feet,
    # so convert.
    convertFeetToMeters = 0.3048
    formatString = '{0},{1},{2}' if with_altitude \
        else '{0},{1},0.0'

    #Also, if the altitudes are all 0, we msut set altitudeMode to realative.
    altitude_list = []

    if a_segment.start != 0:
        prev_pt = trajectory[a_segment.start-1]
        start_pt = trajectory[a_segment.start]
        halfway_pt = _interpolate_points(prev_pt, start_pt)
        try:
            alt = halfway_pt[2] * convertFeetToMeters
        except AttributeError:
            alt = 0
        altitude_list.append(alt)
        point_str = formatString.format(geomath.longitude(halfway_pt),
                                        geomath.latitude(halfway_pt),
                                            alt)
        returnString.append(
            sr.singleLine('gx:coord', point_str))

    for a_point in trajectory[a_segment.start:a_segment.stop]:
        # try:
        alt = geomath.altitude(a_point) * convertFeetToMeters
        altitude_list.append(alt)
        point_str = formatString.format(geomath.longitude(a_point),
                                        geomath.latitude(a_point),
                                            alt)
        returnString.append(
            sr.singleLine('gx:coord', point_str))

    try:
        lastplotted = trajectory[a_segment.stop-1]
        next_seg_first_pt = trajectory[a_segment.stop]
        halfway_pt = _interpolate_points(lastplotted, next_seg_first_pt)
        try:
            alt = halfway_pt[2] * convertFeetToMeters
        except AttributeError:
            alt = 0
        altitude_list.append(alt)
        point_str = formatString.format(geomath.longitude(halfway_pt),
                                        geomath.latitude(halfway_pt),
                                            alt)
        returnString.append(
            sr.singleLine('gx:coord', point_str))
    except IndexError:
        pass

    returnString.append(sr.singleLine('altitudeMode', altitude_mode))
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
        style_name = a_segment.category.name
        if style_name not in styles_dict:
            styles_dict[style_name] = a_segment.category.symbology.to_kml()

        # style_count += 1
        # style_color = a_segment.color
        # style_id = style_color
        # a_segment.styleUrl = style_id
        # if style_color not in styles_dict:
        #     a_style = kml_symbology(style_id, color=style_color, alpha=1.0,
        #                             width=3, scale=1, start_tab_depth=0)
        #     style_xml = a_style.to_kml()
        #     styles_dict[style_color] = \
        #         StyleNamedTuple(style_id=style_id,
        #                         style_xml=style_xml)

    return styles_dict


