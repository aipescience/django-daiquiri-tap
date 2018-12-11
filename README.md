Daiquiri Tap
============

Daiquiri Tap is a tiny wrapper for astroquery.utils.tap, adding support for token authorization.

**Daiquiri Tap is not supported anymore, please use [PyVO](https://pyvo.readthedocs.io/en/latest/) instead.**

You can use TAP token authorization in PyVO by manipulating the `vo.utils.http.session` object, e.g.:

```python
import pyvo as vo

# init tap service
tap_service = vo.dal.TAPService('https://gaia.aip.de/tap')

vo.utils.http.session.headers['Authorization'] = 'Token 23bec8595721dff3fce14265742cd6d0aaef6b95'

tap_service.run_sync('SELECT TOP 5 source_id, ra, dec, parallax FROM gdr2.gaia_source ORDER BY random_index')

tap_service.run_async('SELECT TOP 5 source_id, ra, dec, parallax FROM gdr2.gaia_source ORDER BY random_index')
```
