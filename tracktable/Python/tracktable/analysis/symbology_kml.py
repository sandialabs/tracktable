from matplotlib import colors as clr
import math

class stackWriter():
    """
    Useful for writing values to an xml file. Tab indentation already provided
    """
    def __init__(self, startTabDepth=0):
        self.stack = list()
        self._tab_level = startTabDepth

    def push(self, a_string):
        """Returns a single-word opening line with < and > around a_string.
        Increases the indent level by 1 after returning the string."""
        if '<' in a_string or '>' in a_string:
            raise ValueError("Can't have symbol bracker '<' or '>' in xml "
                "varialble name.")
        self.stack.append(a_string)
        ret_string = self.tabs + '<{0}>\n'.format(a_string)
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

        poppedString = self.stack.pop()
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


def color_name_to_rgb_string(color_name, alpha=None):
    r, g, b = clr.ColorConverter().to_rgb(color_name)

    r, g, b = (int(math.floor(r * 255.9)), int(math.floor(g * 255.9)),
               int(math.floor(b * 255.9)))


    if alpha:
        a = int(math.floor(alpha * 255.9))
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

class kml_symbology():
    def __init__(self, color: str='white', alpha: float=1.0, width: int=3):
        """
        :param color: Standard color string understandable by
            matplotlib.colors.ColorConverter
        :param alpha: Alpha channel value. May be None. Must be 0.0 : 1.0
        :param width: Width of the line to be plotted.
        """
        if not 0.0 <= alpha <= 1.0:
            raise AttributeError('alpha must be None or between 0.0 and 1.0.')
        self.color = color_name_to_rgb_string(color, alpha)
        self.width = str(width)

    # def __str__(self):



