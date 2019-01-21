import logging
import configparser
import requests
import time
import json

from tqdm import tqdm

from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail

from fec.models import Candidate


class Command(BaseCommand):
    help = ('Polls the FEC.gov API to gather donor info. To view the '+
        'fec\'s API documentation and database models use the Swagger '+
        'UI here: http://petstore.swagger.io/ and input the following URL '+
        'at the top: https://api.open.fec.gov/swagger/')

    def handle(self, *args, **options):

        def poll_api():
            '''
            Structure your API calls like the following:
            https://api.open.fec.gov/v1/candidates/?api_key=YOUR_API_KEY
            '''

            config = configparser.ConfigParser()
            config.read('data/fec/fec.ini')
            api_key = config.get('API', 'API_KEY') # stored in .ini file

            url = 'https://api.open.fec.gov/v1/candidates/?api_key='+api_key
            response = json.loads(requests.get(url).content)
            counter = 0
            for key in response['results']:
                for k, v in key.items():
                    print (k, v)
                counter += 1
            print (counter)

        #poll_api()

        def load_from_csv():
            delimiter = '|'
            with open('data/fec/all_candidates.txt', 'r') as f:
                lines = f.readlines()
                for line in tqdm(lines):
                    row = line.split('|')
                    cand_id = row[0]
                    cand_name = row[1]
                    incumbent_challenge_status = row[2]
                    candidate_party_affiliation = row[4]
                    candidate_state = row[18]
                    candidate_district = row[19]

                    Candidate.objects.update_or_create(
                        candidate_id=cand_id,
                        defaults = {
                            'name': cand_name,
                            'candidate_status': incumbent_challenge_status,
                            'party': candidate_party_affiliation,
                            'state': candidate_state,
                            'district': candidate_district,
                        }
                    )

        load_from_csv()
