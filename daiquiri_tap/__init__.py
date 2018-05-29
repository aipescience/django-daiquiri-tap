__title__ = 'django-daiquiri-tap'
__version__ = '0.1.0'
__author__ = 'Jochen Klar'
__email__ = 'jklar@aip.de'
__license__ = 'Apache-2.0'
__copyright__ = 'Copyright 2018 Leibniz Institute for Astrophysics Potsdam (AIP)'


import requests

from astroquery.utils.tap.core import Tap, TAP_CLIENT_ID
from astroquery.utils.tap.conn.tapconn import TapConn
from astroquery.utils.tap.model.job import Job
from astroquery.utils.tap.xmlparser import utils
from astroquery.utils.tap.xmlparser.jobSaxParser import JobSaxParser


class DaiquiriTapConn(TapConn):

    def __init__(self, *args, **kwargs):
        headers = kwargs.pop('headers', {})

        super(DaiquiriTapConn, self).__init__(*args, **kwargs)

        self._TapConn__getHeaders = headers
        self._TapConn__postHeaders = headers
        self.__deleteHeaders = headers

    def execute_delete(self, subcontext, verbose=False):
        conn = self._TapConn__get_connection(verbose)
        context = self._TapConn__get_tap_context(subcontext)
        conn.request("DELETE", context, None, self.__deleteHeaders)
        response = conn.getresponse()
        self.__currentReason = response.reason
        self.__currentStatus = response.status
        return response


class DaiquiriTap(Tap):

    def __init__(self, url=None, token=None, verbose=False):

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

            super(DaiquiriTap, self).__init__(connhandler=connhandler, verbose=verbose)

        else:
            # just use the regular astroquery Tap
            super(DaiquiriTap, self).__init__(url=url, verbose=verbose)


    def launch_job(self, query, name=None, output_file=None,
                   output_format="votable", verbose=False,
                   dump_to_file=False, upload_resource=None,
                   upload_table_name=None, lang=None, queue=None):

        if verbose:
            print("Launched query: '"+str(query)+"'")

        if upload_resource is not None:
            if upload_table_name is None:
                raise ValueError("Table name is required when a resource is uploaded")
            response = self._Tap__launchJobMultipart(query,
                                                 upload_resource,
                                                 upload_table_name,
                                                 output_format,
                                                 "sync",
                                                 verbose,
                                                 name,
                                                 lang,
                                                 queue)
        else:
            response = self.__launchJob(query,
                                        output_format,
                                        "sync",
                                        verbose,
                                        name,
                                        lang,
                                        queue)

        # handle redirection
        if response.status == 303:
            # redirection
            if verbose:
                print("Redirection found")
            location = self._Tap__connHandler.find_header(
                response.getheaders(),
                "location")
            if location is None:
                raise requests.exceptions.HTTPError("No location found after redirection was received (303)")
            if verbose:
                print("Redirect to %s", location)
            subcontext = self._Tap__extract_sync_subcontext(location)
            response = self._Tap__connHandler.execute_get(subcontext)
        job = Job(async_job=False, query=query, connhandler=self._Tap__connHandler)
        isError = self._Tap__connHandler.check_launch_response_status(response,
                                                                  verbose,
                                                                  200)
        suitableOutputFile = self._Tap__getSuitableOutputFile(False,
                                                          output_file,
                                                          response.getheaders(),
                                                          isError,
                                                          output_format)
        job.set_output_file(suitableOutputFile)
        job.set_output_format(output_format)
        job.set_response_status(response.status, response.reason)
        if isError:
            job.set_failed(True)
            if dump_to_file:
                self._Tap__connHandler.dump_to_file(suitableOutputFile, response)
            raise requests.exceptions.HTTPError(response.reason)
        else:
            if verbose:
                print("Retrieving sync. results...")
            if dump_to_file:
                self._Tap__connHandler.dump_to_file(suitableOutputFile, response)
            else:
                results = utils.read_http_response(response, output_format)
                job.set_results(results)
            if verbose:
                print("Query finished.")
            job.set_phase('COMPLETED')
        return job


    def launch_job_async(self, query, name=None, output_file=None,
                         output_format="votable", verbose=False,
                         dump_to_file=False, background=False,
                         upload_resource=None, upload_table_name=None,
                         lang=None, queue=None):

        if verbose:
            print("Launched query: '"+str(query)+"'")
        if upload_resource is not None:
            if upload_table_name is None:
                raise ValueError(
                    "Table name is required when a resource is uploaded")
            response = self.__launchJobMultipart(query,
                                                 upload_resource,
                                                 upload_table_name,
                                                 output_format,
                                                 "async",
                                                 verbose,
                                                 name,
                                                 lang,
                                                 queue)
        else:
            response = self.__launchJob(query,
                                        output_format,
                                        "async",
                                        verbose,
                                        name,
                                        lang,
                                        queue)

        isError = self._Tap__connHandler.check_launch_response_status(response,
                                                                  verbose,
                                                                  303)
        job = Job(async_job=True, query=query, connhandler=self._Tap__connHandler)
        suitableOutputFile = self._Tap__getSuitableOutputFile(True,
                                                          output_file,
                                                          response.getheaders(),
                                                          isError,
                                                          output_format)
        job.set_output_file(suitableOutputFile)
        job.set_response_status(response.status, response.reason)
        job.set_output_format(output_format)
        if isError:
            job.set_failed(True)
            if dump_to_file:
                self._Tap__connHandler.dump_to_file(suitableOutputFile, response)
            raise requests.exceptions.HTTPError(response.reason)
        else:
            location = self._Tap__connHandler.find_header(
                response.getheaders(),
                "location")
            jobid = self._Tap__getJobId(location)
            if verbose:
                print("job " + str(jobid) + ", at: " + str(location))
            job.set_jobid(jobid)
            job.set_remote_location(location)
            if not background:
                if verbose:
                    print("Retrieving async. results...")
                # saveResults or getResults will block (not background)
                if dump_to_file:
                    job.save_results(verbose)
                else:
                    job.get_results()
                    print("Query finished.")
        return job


    def __launchJob(self, query, outputFormat, context, verbose, name=None, lang='ADQL', queue=None):
        args = {
            "REQUEST": "doQuery",
            "LANG": lang or "ADQL",
            "FORMAT": str(outputFormat),
            "tapclient": str(TAP_CLIENT_ID),
            "PHASE": "RUN",
            "QUERY": str(query)}

        if name is not None:
            args['TABLENAME'] = name
        if queue is not None:
            args['QUEUE'] = queue

        data = self._Tap__connHandler.url_encode(args)
        response = self._Tap__connHandler.execute_post(context, data)
        if verbose:
            print(response.status, response.reason)
            print(response.getheaders())
        return response

    def retrieve_async_job(self, job_id, verbose=False):
        response = self._Tap__connHandler.execute_get('async/%s' % job_id)
        if verbose:
            print(response.status, response.reason)
            print(response.getheaders())
        isError = self._Tap__connHandler.check_launch_response_status(response,
                                                                      verbose,
                                                                      200)
        if isError:
            print(response.reason)
            raise requests.exceptions.HTTPError(response.reason)
            return None


        # parse job
        jsp = JobSaxParser(async_job=True)
        jobs = jsp.parseData(response)

        try:
            job = jobs[0]
            job.set_connhandler(self._Tap__connHandler)
            return job
        except IndexError:
            return None

    def archive_async_job(self, job_id, verbose=False):
        response = self._Tap__connHandler.execute_delete('async/%s' % job_id)
        if verbose:
            print(response.status, response.reason)
            print(response.getheaders())
        isError = self._Tap__connHandler.check_launch_response_status(response,
                                                                      verbose,
                                                                      303)
        if isError:
            print(response.reason)
            raise requests.exceptions.HTTPError(response.reason)
            return None
