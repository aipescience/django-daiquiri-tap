Daiquiri Tap
============

Daiquiri Tap is a tiny wrapper for astroquery.utils.tap, adding support for token authorization.

Setup
-----

.. code:: bash

    pip install git+https://github.com/aipescience/django-daiquiri-tap


Usage
-----

It is used like `astroquery.utils.tap`, which is extensively documented in the `astroquery documentation <https://astroquery.readthedocs.io/en/latest/utils/tap.html>`_, but allows to set a token for authorized access to your user account.

The token can be accessed under the url `/accounts/token/` of the particular Daiquiri site, e.g. `gaia.aip.de/accounts/token/ <https://gaia.aip.de/accounts/token/>`_.

.. code:: python

    from daiquiri_tap import DaiquiriTap

    TOKEN = '91123cc8db1bb44326b4d820f88c54bbdec4bea0'

    # connect to the service
    service = DaiquiriTap(url='https://gaia.aip.de/tap', token=TOKEN)

    # launch a syncronous job using adql
    job1 = service.launch_job('select top 10 ra, dec from gdr1.tgas_source')

    # launch an asyncronous job using postgresql and a different queue
    job2 = service.launch_job_async('select ra, dec from gdr1.tgas_source limit 10', lang='postgresql-9.6', queue='5m')

    # clean up the job
    job_id = job2.get_jobid()
    service.archive_async_job(job_id)

    # list all your jobs
    jobs = service.list_async_jobs()

    # retrieve a particular job
    jobs = service.retrieve_async_job()
```
