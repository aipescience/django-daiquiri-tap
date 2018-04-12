Daiquiri Tap
============

Daiquiri Tap is a tiny wrapper for astroquery, adding support for token authorization.

It is used like `astroquery.utils.tap`, which is extensively documented in the `astroquery documentation <https://astroquery.readthedocs.io/en/latest/utils/tap.html>`_, but allows to set a token for authorized access to your user account.

The token can be accessed under the url `/accounts/token/` of the particular Daiquiri site, e.g. `gaia.aip.de/accounts/token/ <https://gaia.aip.de/accounts/token/>`_.

.. code:: python

    from daiquiri_tap import DaiquiriTap

    TOKEN = '91123cc8db1bb44326b4d820f88c54bbdec4bea0'

    service = DaiquiriTap(url='https://gaia.aip.de/tap', token=TOKEN)

    job = service.launch_job('select top 10 ra, dec from gdr1.tgas_source')

    print(job)
