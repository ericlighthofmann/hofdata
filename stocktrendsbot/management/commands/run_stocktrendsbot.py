import csv
import logging
import configparser

import praw
from tqdm import tqdm

from django.core.management.base import BaseCommand, CommandError

from stocktrendsbot.models import Company


class Command(BaseCommand):
    help = 'Runs StockTrendsBot - a reddit bot for posting stock performance.'

    def handle(self, *args, **options):

        # test flag
        test = True

        # log config
        logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

        # defining variables
        config = configparser.ConfigParser()
        config.read('data/stocktrendsbot/stocktrendsbot.ini')
        reddit_id = config.get('Login', 'REDDIT_ID') # stored in .ini file
        reddit_secret = config.get('Login', 'REDDIT_SECRET') # stored in .ini file
        reddit_user_agent = config.get('Login', 'REDDIT_USER_AGENT') # stored in .ini file
        subreddit_list = ['asx', 'ausstocks', 'business', 'stocks',
            'investing', 'finance', 'stockmarket', 'investmentclub',
            'earningreports', 'economy', 'technology'
        ]
        if test:
            subreddit_list = ['testingground4bots']

        all_companies_in_db = Company.objects.all().values_list('symbol', flat=True)

        # @fold
        def get_company_objects():

            '''
            get a list of publicly traded companies from this url:
            https://www.nasdaq.com/screening/company-list.aspx and load into
            the database
            '''

            logging.info('Loading companies into database...')
            with open('data/stocktrendsbot/companylist.csv', 'r') as csv_file:
                csv_reader = csv.reader(csv_file)
                for row in tqdm(csv_reader):
                    symbol = row[0]
                    if symbol in all_companies_in_db:
                        continue
                    name = row[1]
                    ipo_year = row[4]
                    sector = row[5]
                    industry = row[6]

                    Company.objects.update_or_create(
                        symbol = symbol,
                        defaults = {
                            'name': name,
                            'ipo_year': ipo_year,
                            'sector': sector,
                            'industry': industry
                        }
                    )

        # @fold
        def start_stocktrendsbot():

            praw_object = praw.Reddit(
                client_id = reddit_id,
                client_secret = reddit_secret,
                user_agent=reddit_user_agent
            )
            for subreddit in subreddit_list:
                logging.info('Switching to ' + str(subreddit) + '...')
                for submission in praw_object.subreddit(subreddit).hot(limit=10):
                    print (submission)

        get_company_objects()
        start_stocktrendsbot()
