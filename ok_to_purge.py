from get_jobs_named import get_jobs_named

def ok_to_purge(session, system_url, user_token, pvid):
    steveJobsDel = get_jobs_named(session, system_url, user_token, 'com.fortify.manager.BLL.jobs.ArtifactPurgeJob')
    if steveJobsDel is None:
        print("Error retrieving job list")
        return None
    else:
        # now we need to check - how many running or pending deletes do we have?

        for tj in steveJobsDel['data']:
            # we only want to reject active jobs
            if (tj['state'] == "FINISHED"):
                continue
            # that are also not this pvid. REMOVE the 0 part
            if ( 1 == 1 #tj['projectVersionId'] != pvid
                and ((tj['state'] == "PREPARED") or (tj['state'] == "RUNNING")) ):
                    return False
        return True