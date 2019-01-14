import csv
import logging
import configparser
import re
from datetime import datetime
import requests
from dateutil.relativedelta import relativedelta
import time
import json

import praw
from tqdm import tqdm
from iexfinance.stocks import Stock
from iexfinance.stocks import get_historical_data


from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail

from stocktrendsbot.models import Company, PostRepliedTo


class Command(BaseCommand):
    help = 'Runs StockTrendsBot - a reddit bot for posting stock performance.'

    def handle(self, *args, **options):

        stock_object = Stock('TSLA')
        price = round(float(stock_object.get_price()),2)
        print (price)

        start = datetime(2017, 1, 1)
        end = datetime(2017, 1, 3)
        historical_price = get_historical_data("TSLA", start, end, output_format='json')
        print (historical_price[datetime.strftime(end, '%Y-%m-%d')]['close'])
