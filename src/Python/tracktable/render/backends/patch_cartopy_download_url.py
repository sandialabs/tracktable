# We do not claim copyright on this module.  It is borrowed from Cartopy
# (https://github.com/SciTools/cartopy) as a workaround for a missing 
# server until their changes make it into wider release.

import os
import io

from cartopy.io import Downloader
from cartopy import config

from cartopy.io.shapereader import Reader

# This class is from cartopy/io/shapereader.py.


class NEShpDownloader_PatchedURL(Downloader):
    """
    This is exactly like cartopy.io.shapereader.NEShpDownloader
    except that its URL has been patched to include the new location
    of the Natural Earth data files after naciscdn.org went offline in
    September 2021.

    Specialise :class:`cartopy.io.Downloader` to download the zipped
    Natural Earth shapefiles and extract them to the defined location
    (typically user configurable).

    The keys which should be passed through when using the ``format_dict``
    are typically ``category``, ``resolution`` and ``name``.

    """
    FORMAT_KEYS = ('config', 'resolution', 'category', 'name')

    # NaturalEarth files have migrated to S3 buckets.
    _NE_URL_TEMPLATE = ('https://naturalearth.s3.amazonaws.com'
                        '/{resolution}_{category}'
                        '/ne_{resolution}_{name}.zip')

    def __init__(self,
                 url_template=_NE_URL_TEMPLATE,
                 target_path_template=None,
                 pre_downloaded_path_template='',
                 ):
        # adds some NE defaults to the __init__ of a Downloader
        Downloader.__init__(self, url_template,
                            target_path_template,
                            pre_downloaded_path_template)

    def zip_file_contents(self, format_dict):
        """
        Return a generator of the filenames to be found in the downloaded
        natural earth zip file.

        """
        for ext in ['.shp', '.dbf', '.shx', '.prj', '.cpg']:
            yield ('ne_{resolution}_{name}'
                   '{extension}'.format(extension=ext, **format_dict))

    def acquire_resource(self, target_path, format_dict):
        """
        Download the zip file and extracts the files listed in
        :meth:`zip_file_contents` to the target path.
        """
        from zipfile import ZipFile

        target_dir = os.path.dirname(target_path)
        if not os.path.isdir(target_dir):
            os.makedirs(target_dir)

        url = self.url(format_dict)

        shapefile_online = self._urlopen(url)

        zfh = ZipFile(io.BytesIO(shapefile_online.read()), 'r')

        for member_path in self.zip_file_contents(format_dict):
            ext = os.path.splitext(member_path)[1]
            target = os.path.splitext(target_path)[0] + ext
            member = zfh.getinfo(member_path.replace(os.sep, '/'))
            with open(target, 'wb') as fh:
                fh.write(zfh.open(member).read())

        shapefile_online.close()
        zfh.close()

        return target_path

    @staticmethod
    def default_downloader():
        """
        Return a generic, standard, NEShpDownloader instance.
        Typically, a user will not need to call this staticmethod.
        To find the path template of the NEShpDownloader:
            >>> ne_dnldr = NEShpDownloader.default_downloader()
            >>> print(ne_dnldr.target_path_template)
            {config[data_dir]}/shapefiles/natural_earth/{category}/\
ne_{resolution}_{name}.shp
        """
        default_spec = ('shapefiles', 'natural_earth', '{category}',
                        'ne_{resolution}_{name}.shp')
        ne_path_template = os.path.join('{config[data_dir]}', *default_spec)
        pre_path_template = os.path.join('{config[pre_existing_data_dir]}',
                                         *default_spec)
        return NEShpDownloader_PatchedURL(
            target_path_template=ne_path_template,
            pre_downloaded_path_template=pre_path_template)


def patch_cartopy_backend():
    # add a generic Natural Earth shapefile downloader to the config dictionary's
    # 'downloaders' section.
    _ne_key = ('shapefiles', 'natural_earth')
    config['downloaders'][_ne_key] = NEShpDownloader_PatchedURL.default_downloader()

    # config['downloaders'].setdefault(_ne_key,
    #                                  NEShpDownloader_PatchedURL.default_downloader())

