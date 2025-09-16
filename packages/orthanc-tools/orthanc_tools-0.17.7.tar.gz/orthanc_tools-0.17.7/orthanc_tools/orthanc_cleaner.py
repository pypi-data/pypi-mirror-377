'''
# Summary
This script will clean the Orthanc by deleting the oldest studies according to the labels applied on them, and
potentially to the modality type.

# How it works
The script will run every day at specified time.
It will read a configuration file defining what should be done:

LABEL1,6,
LABEL2,12,
LABEL2,4,CT

With that sample, all studies with the LABEL1 and older than 6 weeks will be deleted
all studies with the LABEL2 and older than 12 weeks will be deleted;
all studies which have CT in the 'ModalitiesInStudy' tag and older than 4 weeks will be deleted;

Note: studies are deleted only if they were uploaded/modified in Orthanc before the retention period
'''

import datetime

import schedule
import time
import argparse
import logging
from typing import List
import os
from orthanc_api_client import OrthancApiClient, helpers
import csv

logger = logging.getLogger(__name__)

class LabelRule:
    def __init__(self,
                 label_name: str,
                 retention_duration: int,    # unit: week
                 modality: str = ""
                 ):
        self.label_name = label_name
        self.retention_duration = retention_duration
        self.modality = modality

class OrthancCleaner:

    def __init__(self,
                 api_client: OrthancApiClient,
                 execution_time: str,
                 labels_file_path: str
                 ):
        '''
        If execution_time value is 'None', the clean up will be ran only once (use case: unit tests)
        '''
        self._api_client = api_client
        self._execution_time = execution_time
        self._labels_file_path = labels_file_path

    def clean(self):
        '''
        Get information from the csv file (label and retention duration);
        Query Orthanc based on this information;
        Delete the studies found.
        '''

        # Get the information from  the csv file
        logger.info("Starting daily clean up...")
        labels_rules = self.parse_csv_file()

        logger.info(f"Rules found:")
        for rule in labels_rules:
            logger.info(f"Label: {rule.label_name} - {rule.retention_duration} weeks - Modality: {rule.modality}")

        # get the list of studies to delete
        studies_ids_to_delete = self.get_studies_to_delete(labels_rules=labels_rules)

        while len(studies_ids_to_delete) > 0:
            
            # Delete the found studies
            for id in studies_ids_to_delete:
                try:
                    logger.info(f"Deleting study {id} from {self._api_client.studies.get(id).main_dicom_tags.get('StudyDate')}...")
                    self._api_client.studies.delete(id)
                except Exception as ex:
                    logger.error(f"ERROR: {str(ex)}")
            
            # Get one more time the list of studies to delete (because we may have been limited to the value of 'LimitFindResults')
            studies_ids_to_delete = self.get_studies_to_delete(labels_rules=labels_rules)

        logger.info("Clean up done!")

    def get_studies_to_delete(self, labels_rules: List[LabelRule]) -> set():
        '''
        Query Orthanc to get the list of orthanc ids of the studies to delete (depending on the date and the label)
        '''
        studies_to_delete = set()
        for label_rule in labels_rules:

            # Let's compute the date
            limit_date = self.compute_limit_date(label_rule.retention_duration)

            # Query Orthanc based on the date and the label
            studies_to_delete_by_study_date = self._api_client.studies.find(
                query={
                    'StudyDate': f'-{helpers.to_dicom_date(limit_date)}',
                    'ModalitiesInStudy': label_rule.modality
                },
                labels=[label_rule.label_name]
                )

            # Filter out the old studies which were recently stored in Orthanc
            for s in studies_to_delete_by_study_date:
                if limit_date > s.last_update.date():
                    studies_to_delete.add(s.orthanc_id)

        logger.info(f"Found {len(studies_to_delete)} studies to delete...")
        return studies_to_delete

    def compute_limit_date(self, number_of_weeks) -> datetime.date:
        limit_date = datetime.date.today() - datetime.timedelta(weeks=number_of_weeks)
        return limit_date

    def parse_csv_file(self) -> List[LabelRule]:
        '''
        Read the csv file, extract info and return a list of 'LabelRule' objects
        '''

        labels_rules = []
        with open(self._labels_file_path, 'r') as csv_file:
            reader = csv.reader(csv_file)

            for row in reader:
                labels_rules.append(LabelRule(row[0], int(row[1]), row[2]))
        return labels_rules


    def execute(self):
        logger.info("----- Initializing Orthanc Cleaner...")
        if self._execution_time is None:
            # unit test case
            self.clean()
        else:
            # regular (prod) case
            schedule.every().day.at(self._execution_time).do(self.clean)
            while True:
                schedule.run_pending()
                time.sleep(1)


# example:
# python orthanc_tools/orthanc_cleaner.py --orthanc_url=http://192.168.0.10:8042 --orthanc_user=user --orthanc_pwd=pwd --execution_time=23:30 --labels_file_path=./tests/stimuli/labels.csv

if __name__ == '__main__':
    level = logging.INFO

    if os.environ.get('VERBOSE_ENABLED'):
        level = logging.DEBUG

    logging.basicConfig(level=level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    parser = argparse.ArgumentParser(description='Clean the Orthanc by deleting the oldest studies according to the labels applied on them.')
    parser.add_argument('--orthanc_url', type=str, default=None, help='Orthanc source url')
    parser.add_argument('--orthanc_user', type=str, default=None, help='Orthanc source user name')
    parser.add_argument('--orthanc_pwd', type=str, default=None, help='Orthanc source password')
    parser.add_argument('--orthanc_api_key', type=str, default=None, help='Orthanc api-key')
    parser.add_argument('--execution_time', type=str, default='02:30', help='Time for script execution (format: 23:30 or 23:30:14).')
    parser.add_argument('--labels_file_path', type=str, default=None, help='Path of the file containing the labels to handle and retention duration')

    args = parser.parse_args()

    orthanc_url = os.environ.get("ORTHANC_URL", args.orthanc_url)
    orthanc_user = os.environ.get("ORTHANC_USER", args.orthanc_user)
    orthanc_pwd = os.environ.get("ORTHANC_PWD", args.orthanc_pwd)
    orthanc_api_key = os.environ.get("ORTHANC_API_KEY", args.orthanc_api_key)
    execution_time = os.environ.get("EXECUTION_TIME", args.execution_time)
    labels_file_path = os.environ.get("LABELS_FILE_PATH", args.labels_file_path)


    api_client = None
    if orthanc_api_key is not None:
        api_client=OrthancApiClient(orthanc_url, headers={"api-key":orthanc_api_key})
    else:
        api_client=OrthancApiClient(orthanc_url, user=orthanc_user, pwd=orthanc_pwd)

    cleaner = OrthancCleaner(
        api_client=api_client,
        execution_time=execution_time,
        labels_file_path=labels_file_path
    )

    cleaner.execute()



