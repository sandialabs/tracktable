from matplotlib import colors as clr
import math

class stackWriter():
    """
    Useful for writing values to an xml file. Tab indentation already provided
    """
    def __init__(self, startTabDepth=0):
        self.stack = list()
        self._tab_level = startTabDepth

    def push(self, a_string: str, var_value: str=None) -> str:
        """Returns a single-word opening line with < and > around a_string.
        Increases the indent level by 1 after returning the string."""
        if '<' in a_string or '>' in a_string:
            raise ValueError("Can't have symbol bracket '<' or '>' in xml "
                "varialble name.")
        self.stack.append(a_string)
        if not var_value:
            ret_string = self.tabs + '<{0}>\n'.format(a_string)
        else:
            ret_string = self.tabs + '<{0}="{1}">\n'.format(a_string, var_value)
        self._tab_level += 1
        return ret_string

    def pop(self, optionalPopString=''):
        """
        Returns a single-word closing line with </ and > around the string
        being popped off the stack. Decrements the indent level by 1 before
        returning the string.
        :param optionalPopString: If provided, verifies that the string your
            thought was to be popped is actually the one being popped.
        :return: The string that was popped off the stack.
        """
        if len(self.stack) == 0:
            return None
        self._tab_level -= 1

        poppedString = self.stack.pop().split(' ')[0]
        if len(optionalPopString) > 0 and \
                poppedString != optionalPopString:
            raise AttributeError('popped string ("{0}")not same as expected '
                'string ("{1}")'.format(poppedString, optionalPopString))

        return_string = self.tabs + '</{0}>\n'.format(poppedString)
        return return_string

    def singleLine(self, varName, varValue):
        """
        Returns a string of pattern:
                <varName>varValue</varName>
                Does not change the indent level
        :param varName: The name of the xml variable to put in the string.
        :param varValue: The value associated with this variable.
        :return: An XML string representation of the variable/value pair.
        """
        return (self.tabs + '<{0}>{1}</{0}>\n' \
                .format(varName, str(varValue))
                )

    @property
    def tabs(self):
        return '\t' * self._tab_level


# This color palette is based on
# http://mkweb.bcgsc.ca/colorblind/
# Conservative Seven Color Palette

black = ('#%02x%02x%02x' % (0, 0, 0)).upper()
orange = ('#%02x%02x%02x' % (230, 159, 0)).upper()
sky_blue = ('#%02x%02x%02x' % (86, 180, 233)).upper()
bluish_green = ('#%02x%02x%02x' % (0, 158, 115)).upper()
yellow = ('#%02x%02x%02x' % (240, 228, 66)).upper()
blue = ('#%02x%02x%02x' % (0, 114, 178)).upper()
vermillion = ('#%02x%02x%02x' % (213, 94, 0)).upper()
reddish_purple = ('#%02x%02x%02x' % (204, 121, 167)).upper()
white = ('#%02x%02x%02x' % (255, 255, 255)).upper()

color_blind_acceptable_dict = \
    {
        black: 'black',
        orange: 'orange',
        sky_blue: 'sky blue',
        bluish_green: 'bluish green',
        yellow: 'yellow',
        blue: 'blue',
        vermillion: 'vermillion',
        reddish_purple: 'reddish purple',
        white: 'white',
        'black': black,
        'orange': orange,
        'sky blue': sky_blue,
        'bluish green': bluish_green,
        'yellow': yellow,
        'blue': blue,
        'vermillion': vermillion,
        'reddish_purple': reddish_purple,
        'white': white
    }


def color_name_to_rgb_string(color_name, alpha=None, swap_red_blue=False,
                             limit_to_color_blind_palette=False):
    if limit_to_color_blind_palette:
        rgb = color_blind_acceptable_dict[color_name]
        if swap_red_blue:
            rgb = rgb[1:]
            r = rgb[:2]
            g = rgb[2:-2]
            b = rgb[-2:]
            rgb = '#' + b + g + r
        return '#FF' + rgb[1:]

    r, g, b, a = clr.ColorConverter().to_rgba(color_name, alpha=alpha)
    if swap_red_blue:
        temp = r
        r = b
        b = temp

    r, g, b = (int(math.floor(r * 255.9)), int(math.floor(g * 255.9)),
               int(math.floor(b * 255.9)))


    if alpha:
        a = int(math.floor(a * 255.9))
        a = ('#%02x' % a).upper()
        rgb_str = a + ('%02x%02x%02x' % (r, g, b)).upper()

    else:
        rgb_str = ('#%02x%02x%02x' % (r, g, b)).upper()

    return rgb_str

if __name__ == '__main__':
    print('Test runs.')
    print('Purple is', color_name_to_rgb_string('purple'))
    print('Transparent Charteuse is', color_name_to_rgb_string('chartreuse',
                                                              0.5))
    print ('Color Blind friendly vermillion is',
           color_name_to_rgb_string('vermillion',
            limit_to_color_blind_palette=True))

class kml_symbology():
    def __init__(self, symbology_name: str,
                 color: str='white', alpha: float=1.0,
                 width: int=3, scale: float=0.0,
                 start_tab_depth: int=0):
        """
        :param symbology_name: Name of this symbology instance. Required.
        :param color: Standard color string understandable by
            matplotlib.colors.ColorConverter or hex string of the color.
        :param alpha: Alpha channel value. May be None or must be 0.0 : 1.0
        :param width: Width of the line to be plotted.
        :param scale: Scale of the line to be plotted.
        :param start_tab_depth: How many tabs should the xml print start with
        """
        if not 0.0 <= alpha <= 1.0:
            raise AttributeError('alpha must be None or between 0.0 and 1.0.')

        self.symbology_name = symbology_name
        try:
            self.color = color_name_to_rgb_string(color, alpha,
                         swap_red_blue=True,
                         limit_to_color_blind_palette=True)
        except:
            self.color = hex(int(color, 16)).upper()[2:]

        self.width = str(width)
        self.scale = str(scale)
        self.start_tab_depth = start_tab_depth

    def to_kml(self) -> str:
        build_list = []
        sr = stackWriter(self.start_tab_depth)
        build_list.append((sr.push('Style id', self.symbology_name)))
        build_list.append(sr.push('LineStyle'))
        build_list.append(sr.singleLine("labelVisibility", 1))
        build_list.append(sr.singleLine('width', self.width))
        build_list.append(sr.singleLine('color', self.color))
        build_list.append(sr.pop('LineStyle'))
        build_list.append(sr.push('LabelStyle'))
        build_list.append(sr.singleLine('scale', self.scale))
        build_list.append(sr.pop('LabelStyle'))
        build_list.append(sr.push("IconStyle"))
        build_list.append(sr.push("Icon"))
        build_list.append(sr.singleLine('href', ''))
        build_list.append(sr.pop('Icon'))
        build_list.append(sr.pop('IconStyle'))
        build_list.append(sr.pop('Style'))
        return ''.join(build_list)


if __name__ == '__main__':
    print()
    print('Testing class kml_symbology.')
    instance = kml_symbology('SomeName', color='brown', alpha=0.8,
                             width=5, scale=1, start_tab_depth=1)
    kml_str = instance.to_kml()
    print()
    print(kml_str)

    instance = kml_symbology('SomeName', color='ACFF4F09', alpha=0.8,
                             width=5, scale=1, start_tab_depth=1)
    kml_str = instance.to_kml()
    print()
    print(kml_str)



