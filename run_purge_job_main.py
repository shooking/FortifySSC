import pyodbc
import os
import sys
import requests
import time
from PurgeArtifactWithCascade import PurgeArtifactWithCascade
from ok_to_purge import ok_to_purge


session = requests.session()
system_url = os.getenv('FORTIFY_HOST')
os.environ['no_proxy'] = system_url

# Get environment variables
PASSWORD = os.getenv('SQLPASS')
print("Attempting to connect")
user_token = os.getenv('FORTIFY_TOKEN')

prod=os.getenv('prod')
prodUser=os.getenv('prodUser')

conn = pyodbc.connect(driver='SQL Server',
        server=f'{prod},1433', database='FTY',
        user=prodUser, password=f'{PASSWORD}', Trusted_Connection='No')
print("Connected")
if conn is None:
    print("Couldnt connect")
    sys.exit(1)

how_many = conn.getinfo(pyodbc.SQL_MAX_CONCURRENT_ACTIVITIES)
print(how_many)


"""
HERE's what we want to achieve

FIND LIST of PVIDs with more then 40 unpurged entries

select projectVersion_id, count(*)
from artifact
where purged='N'
and artifactType='FPR'
group by projectVersion_id
having count(*) > 40
order by count(*) desc

take this set of PVIDs
For each version
    select max(id) from 
    (select top 20 id from artifact
    where projectVersion_id = VERSION
    and artifactType = 'FPR'
    and purged='N'
    and auditUpdated = 'N'
    order by id asc) as t(id)
    
    Wait until no more purges are running
    
        Then take this artifact ID and purge it (and hence at most 20 below)
    
Keep going
"""
delayTime = 2 # seconds       
totalToDo = 0
totalGroups = 0
candidatePVIDs = []
try:
    with conn:
        cursor = conn.cursor()
        cursor.execute("""select top 20 projectVersion_id, count(*)
    from artifact
    where purged='N'
    and artifactType='FPR'
    and auditUpdated = 'N'
    and status = 'PROCESS_COMPLETE'
    group by projectVersion_id
    having count(*) > 40
    order by count(*) asc, projectVersion_id asc""")
    
        for i in cursor:
            totalToDo = totalToDo + i[1]
            totalGroups = totalGroups + 1
            candidatePVIDs.append((i[0], i[1])) # 1st element is pvid, 2nd is count(*)


    print(f"Total Groups {totalGroups}, Total to do {totalToDo}")
    # OK so we have stored the set ... now walk that set
    doneGroupCount = 0
    print(doneGroupCount)

    for candidate in candidatePVIDs:
        pvid = candidate[0]
        with conn:
            cursor = conn.cursor()
            cursor.execute( f"""select max(id) from 
        (select top 20 id from artifact
        where projectVersion_id = {pvid}
        and artifactType = 'FPR'
        and purged='N'
        and status='PROCESS_COMPLETE'
        and auditUpdated = 'N'
        order by id asc) as t(id)""" )
            
            for artifact in cursor:
                # this is the canidateArtifact
                #print("Check purge jobs")
                print(artifact)
                art_id = artifact[0]
                isok = ok_to_purge(session, system_url, user_token, pvid)
            
                if isok is None:
                    print("System error, bailing")
                    time.sleep(30)
                    continue # at least give next group a chance sys.exit(1)
                elif isok == False:
                    waitStates = 0;
                    # well at this point we are in the middle of deleting? Wait here until we can move
                    while isok == False:
                        print("\tPVID: {}. Waited {}\tWaiting {} seconds".format(pvid, waitStates * delayTime, delayTime))
                        waitStates = waitStates + 1
                        time.sleep(delayTime)
                        isok = ok_to_purge(session, system_url, user_token, pvid)
                        if isok is None:
                            print("System error, bailing")
                            time.sleep(30)
                            continue # at least give next group a chance sys.exit(1)
                        elif isok == False:
                            if waitStates > int(60/delayTime) * 60 * 2: # 2 hours
                                print("Waited too long - cancelling script")
                                # BUT should I cancel, or move to the next group?
                                # perhaps a parameter to control this
                                #sys.exit(2)
                                continue # to next group
                # ok we are here because isok was True at one point ...

                try:
                    PurgeArtifactWithCascade(session, system_url, user_token, art_id)
                    doneGroupCount = doneGroupCount + 1
                    print(f'Group {doneGroupCount} of {totalGroups}\t PVID: {pvid!r}')
                except:
                    print("Error ... trying next")
                    
                       
finally:
   conn.commit()
   conn.close()