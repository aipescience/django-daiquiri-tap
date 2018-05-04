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

Example job management
-----

.. code:: python

    from daiquiri_tap import DaiquiriTap
    from  datetime import date, datetime
    import re

    def archive_job(service, jobid, dry):
        if(dry): 
            print('archive  %s' % jobid)
        else:
            service.archive_async_job(jobid)
            print('archived  %s' % jobid)
            
    # n_days = number of days from now
    def archive_by_age(service, jobs, n_day, dry):
     tdy = datetime.now()
        n = 0
        for j in jobs:
            xj = service.retrieve_async_job(j.get_jobid())
            try:
                ctx = tdy - datetime.strptime(xj.get_creation_time(),'%Y-%m-%dT%H:%M:%SZ')
            except:
                ctx = tdy - tdy
        
            if (ctx.days > n_day):
                archive_job(service, j.get_jobid(), dry)
        

    def archive_by_status(service, jobs, status, dry):
        for j in jobs:
            if (re.match(status, j.get_phase())):
                archive_job(service, j.get_jobid(), dry)
        else:
            archive_job(service, j.get_jobid(), dry)
            
    # list queries matching status (=ERROR, COMPLETE) or status='' => list all
    # returns a dict
    def list_queries_by_phase(service, jobs, status):
        queries={}
        if(status): 
            for j in jobs:
                if (re.match(status, j.get_phase())):
                    xj = service.retrieve_async_job(j.get_jobid())
                    queries[j.get_jobid()] = (xj.get_query(),xj.get_creation_time())
        else:    
            for j in jobs:
                xj = service.retrieve_async_job(j.get_jobid())
                queries[j.get_jobid()] = (xj.get_query(),xj.get_creation_time())
        return queries
        
    # manage jobs
    TOKEN = ''
    service = DaiquiriTap(url='https://gaia.aip.de/tap', token=TOKEN)
     
    # this yields only part of the available and desired information 
    jobs = service.list_async_jobs()
    for j in jobs:
       print(j)
       break
     
    # this provides a dict with jobid, time, and query
    status='COMPLETED'
    qlist = list_queries_by_phase(service, jobs, status)
    for query in qlist:
       print('ID: %s, date: %s  \n %s' % (x,query[x][1],query[x][0]))
       break   
    
    # archive all jobs older than 250 days 
    dry = 1
    days = 250
    archive_by_age(service, jobs, days, dry)
    
    # archive all failed jobs  
    dry = 1
    status='ERROR'
    archive_by_status(service, jobs, status, dry)
```   
    
