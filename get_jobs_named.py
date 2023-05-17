import datetime
import time
import sys
import math
import requests
import json

from requests.utils import quote

def get_jobs_named(session, system_url, user_token, jobName, thelimit=60):
    # example jobName is com.fortify.manager.BLL.jobs.ArtifactDeleteJob
    #
    # VERY IMPORTANT. 22.1.2 now accepts jobClass as well as jobClassName.
    # but 21.2.x only accepts jobClassName - so I am changing the API to allow JobClassName and we can change it eventually.
    url = system_url + '/ssc/api/v1/jobs/?fields=jobName,jobClass,projectVersionId,state&start=0&limit={}&q=jobClassName:{}'.format(thelimit, jobName)
    header = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'FortifyToken {}'.format(user_token)
    }

    response = session.get(url, headers=header,  verify=True)
    if not response.status_code == requests.codes.ok:
        print( 'Failed retrieval of recent jobs name' )
        print( response.json() )
        return None
    return response.json()