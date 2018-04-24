__title__ = 'django-daiquiri-tap'
__version__ = '0.1.0'
__author__ = 'Jochen Klar'
__email__ = 'jklar@aip.de'
__license__ = 'Apache-2.0'
__copyright__ = 'Copyright 2018 Leibniz Institute for Astrophysics Potsdam (AIP)'


from astroquery.utils.tap.core import Tap
from astroquery.utils.tap.conn.tapconn import TapConn


class DaiquiriTapConn(TapConn):

    def __init__(self, *args, **kwargs):
        headers = kwargs.pop('headers', {})

        super(DaiquiriTapConn, self).__init__(*args, **kwargs)

        self._TapConn__getHeaders = headers
        self._TapConn__postHeaders = headers


class DaiquiriTap(Tap):

    def __init__(self, url=None, token=None):

        if token is not None:
            headers = {
                'Authorization': 'Token %s' % token
            }

            protocol, host, port, server_context, tap_context = self._Tap__parseUrl(url)

            if protocol == "http":
                connhandler = DaiquiriTapConn(False, host, server_context,
                                              tap_context=tap_context, port=port, headers=headers)
            else:
                connhandler = DaiquiriTapConn(True, host, server_context,
                                              tap_context=tap_context, port=port, sslport=port, headers=headers)

            super(DaiquiriTap, self).__init__(connhandler=connhandler)

        else:
            # just use the regular astroquery Tap
            super(DaiquiriTap, self).__init__(url=url)
