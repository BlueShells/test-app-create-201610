#!/usr/bin/env python
import yaml
import time
import argparse
import datetime

import logging
logging.basicConfig(
    format='%(asctime)s - %(relativeCreated)6d - %(levelname)-8s - %(message)s',
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

projects = yaml.load('''
apiVersion: v1
items:
- apiVersion: v1
  kind: Project
  metadata:
    creationTimestamp: 2016-10-20 04:09:00
    deletionTimestamp: 2016-10-20 04:10:55
    name: terminating2
  spec:
    finalizers: [kubernetes]
  status: {phase: Terminating}
- apiVersion: v1
  kind: Project
  metadata:
    creationTimestamp: 2016-10-20 03:45:34
    deletionTimestamp: 2016-10-25 03:45:54
    name: tempinating1
  spec:
    finalizers: [kubernetes]
  status: {phase: Terminating}
- apiVersion: v1
  kind: Project
  metadata:
    creationTimestamp: 2016-10-19 11:37:45
    name: test1
  spec:
    finalizers: [openshift.io/origin, kubernetes]
  status: {phase: Active}
kind: List
metadata: {}
''')

def parse_args():
    """ parse the args from the cli """

    parser = argparse.ArgumentParser(description='OpenShift Monitoring Project Termination Stats')
    parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
    return parser.parse_args()

def testProjects(projects, current_time=None,):
    logger.info('testProjects() count of projects: %s', len(projects))

    time_keeps_max = 0
    for project in projects:
        logger.debug(
            "Project: %s Status: %s",
            project['metadata']['name'],
            project['status']['phase']
        )

        if project['status']['phase'] == 'Terminating':
            logger.debug('project[\'metadata\'][\'deletionTimestamp\'] %s', project['metadata']['deletionTimestamp'])

            old_time = project['metadata']['deletionTimestamp']

            time_keeps = current_time - old_time
            logger.debug('Project in Terminating status for %s', time_keeps.seconds)

            if current_time > old_time:
                time_keeps_max = max(time_keeps_max, time_keeps.seconds)
            else:
                logger.warning('current_time > old_time')

            logger.debug('%s', time_keeps_max)

    return time_keeps_max

def main():
    ''' main() '''
    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    logger.info("Starting")

    time_keeps_max = testProjects(
        projects['items'],
        current_time=datetime.datetime.now()
    )
    logger.info('Oldest Terminating project: %s seconds', time_keeps_max)

if __name__ == "__main__":
    main()
