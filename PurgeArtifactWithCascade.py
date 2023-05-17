import sys
import argparse
import requests
import json
import os

class Arguments:
    def __init__(self):
        self.parser = argparse.ArgumentParser('PurgeArtifactWithCascade.py')
        self.parser._action_groups.pop()
        self.required = self.parser.add_argument_group('required arguments')
        self.optional = self.parser.add_argument_group('optionel arguments')
        self.define_script_arguments()
    def define_script_arguments(self):
        # Required Arguments
        self.required.add_argument('--art_id', dest='art_id',
                                   nargs=1, help='artifact id; all entries in projectversion LOWER than this will be purged')
        self.required.add_argument('--token', dest='user_token',
                                   nargs=1, help='user_token')
        self.required.add_argument('--host', dest='host',
                                   nargs=1, help='host')
    def get_arguments(self):
        args = Arguments.unpack_argument_lists(self.parser.parse_args())
        Arguments.validate_arguments(args)
        return args
    @staticmethod
    def unpack_argument_lists(args):
        args.art_id = next(iter(args.art_id or []), None)
        args.user_token = next(iter(args.user_token or []), None)
        args.host = next(iter(args.host or []), None)
        return args
    @staticmethod
    def validate_arguments(args):
        # Fast Exit if there are not all required params provided
        if args.art_id is None:
            sys.exit('ERROR: --art_id is a mandatory parameter')
        if args.user_token is None:
            sys.exit('ERROR: --token is a mandatory parameter')
        if args.host is None:
            sys.exit('ERROR: --host is a mandatory parameter')


def main():
#############################################
# Initialization of Script Arguments
#############################################
    script_arguments = Arguments()
    args = script_arguments.get_arguments()

    system_url = 'https://' + args.host
    os.environ['no_proxy'] = args.host

# Start a new session
    session = requests.session()

    retval = PurgeArtifactWithCascade(session, system_url, args.user_token, args.art_id)
    return


def PurgeArtifactWithCascade(session, system_url, user_token, art_id):
    url = system_url + '/ssc/api/v1/artifacts/action/purge'
    header = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'FortifyToken {}'.format(user_token)
    }

    paramsdata = {
        'artifactIds': [ art_id ]
    }
    #print(paramsdata)
    response = session.post(url, data = json.dumps(paramsdata), headers=header, verify=True)
    if not response.status_code == requests.codes.ok:
        print(f"{url}, {paramsdata}")
        print('Failed Purge with status {}'.format(response.status_code))
    return response.json()


if __name__ == "__main__":
    main()
