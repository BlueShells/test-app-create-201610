#!/usr/bin/env python
''' OpenShift v3 Monitoring '''

# Adding the ignore because it does not like the naming of the script
# to be different than the class name
# pylint: disable=invalid-name

import time
import argparse
import datetime

from openshift_tools.monitoring.ocutil import OCUtil

# Our jenkins server does not include these rpms.
# In the future we might move this to a container where these
# libs might exist
#pylint: disable=import-error
from openshift_tools.monitoring.zagg_sender import ZaggSender

import logging
logging.basicConfig(
    format='%(asctime)s - %(relativeCreated)6d - %(levelname)-8s - %(message)s',
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def parse_args():
    """ parse the args from the cli """

    parser = argparse.ArgumentParser(description='OpenShift Monitoring Project Termination Stats')
    parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
    return parser.parse_args()

def send_zagg_data(keep_time):
    ''' send data to Zagg'''
    zgs_time = time.time()
    zgs = ZaggSender()
    print "Send data to Zagg"
    zgs.add_zabbix_keys({'openshift.master.project.terminating.time': keep_time})
    try:
        zgs.send_metrics()
    except:
        print "Error sending to Zagg: %s \n %s " % sys.exc_info()[0], sys.exc_info()[1]
    print "Data sent in %s seconds" % str(time.time() - zgs_time)

def main():
    ''' main() '''
    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    projects_info = OCUtil()._run_cmd("oc get projects -o yaml")

    #deletionTimestamp
    print 'start checking'
    print 'current project number is %s' % len(projects_info['items'])
    time_keeps_max = 0
    try:
        for pro in projects_info['items']:
            #print pro['status']['phase']
            if 'Terminating' == pro['status']['phase']:
                print 'found it '
                print pro['metadata']['deletionTimestamp']
                temp_t = pro['metadata']['deletionTimestamp'].replace('T', ' ').replace('Z', '')
                old_time = datetime.datetime.strptime(temp_t, '%Y-%m-%d %H:%M:%S')

                current_time = datetime.datetime.now()

                time_keeps = current_time - old_time
                print 'the project in Terminating status for %s' % time_keeps

                if current_time > old_time:
                    time_keeps_max = max(time_keeps_max, time_keeps.seconds)
                else:
                    print 'something wrong , the pod said its been terminating before created'

                print time_keeps_max

    except ValueError, e:
        print 'something wrong when try to check the project one by one:', e

    send_zagg_data(time_keeps_max)
    print 'the logest Terminating project is there for %s seconds' % time_keeps_max

if __name__ == "__main__":
    main()
