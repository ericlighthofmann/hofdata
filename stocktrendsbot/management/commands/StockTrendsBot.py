#!/usr/bin/python
import praw
import pdb
import re
import os
import time
import pandas_datareader.data as web
import numpy
import openpyxl
from datetime import datetime, timedelta
import requests
import bs4
import warnings

TickerList = []
CompanyNameList = []
posts_replied_to = []

#------------------------------------------------------------------#
#import company names and tickers from Excel

wb = openpyxl.loa
d_workbook(filename = 'CompanyList_nondup3.xlsx')
sheet = wb.active
print('Getting info from cells...')
for row in range(2, sheet.max_row + 1):
    Ticker       = sheet['A' + str(row)].value
    CompanyName  = sheet['B' + str(row)].value
    TickerList.append(Ticker)
    CompanyNameList.append(CompanyName)

#-----------------------------------------------------------------#
#DEFINE FUNCTIONS TO GET CURRENT PRICE AND CHANGES

#Get current price using Requests and BS4
def getCurrentPrice(ticker):
    res = requests.get('http://finance.yahoo.com/q?s=' + ticker)
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    ticker = ticker.lower()
    try:
        elems = soup.select('#yfs_l84_'+str(ticker))
        elems2 = soup.select('#yfs_j10_'+str(ticker))
        current_price = elems[0].getText()
        market_cap = elems2[0].getText()
        return current_price, market_cap
    except:
        current_price = ''
        market_cap = ''
        return current_price, market_cap

def getWeeklyChange(ticker, current_price):
    start = datetime(1900, 1, 1)
    today = datetime.now()
    if today.hour >= 13:
        end = '%d, %d, %d'%(today.year, today.month, today.day)
    else:
        end = '%d, %d, %d'%(today.year, today.month, today.day-1)
    f = web.DataReader(str(ticker), 'yahoo', start, end)
    for day in range(7,11):
        last_week = (today - timedelta(days = day))
        formatted_week = last_week.strftime('%Y, %#m, %#d')
        try:
            weekly_price = f.ix[str(formatted_week)]['Adj Close']
            weekly_change = (float(current_price)-float(weekly_price))/float(weekly_price)*100
            weekly_change = '{:.2f}'.format(weekly_change)
            return weekly_change
            break
        except:
            continue

def getMonthlyChange(ticker, current_price):
    start = datetime(1900, 1, 1)
    today = datetime.now()
    if today.hour >= 13:
        end = '%d, %d, %d'%(today.year, today.month, today.day)
    else:
        end = '%d, %d, %d'%(today.year, today.month, today.day-1)
    f = web.DataReader(str(ticker), 'yahoo', start, end)
    for day in range(30, 34):
        last_month = (today - timedelta(days = day))
        formatted_month = last_month.strftime('%Y, %#m, %#d')
        try:
            monthly_price = f.ix[str(formatted_month)]['Adj Close']
            monthly_change = (float(current_price)-float(monthly_price))/float(monthly_price)*100
            monthly_change = '{:.2f}'.format(monthly_change)
            return monthly_change
            break
        except:
            continue

def getYearlyChange(ticker, current_price):
    start = datetime(1900, 1, 1)
    today = datetime.now()
    if today.hour >= 13:
        end = '%d, %d, %d'%(today.year, today.month, today.day)
    else:
        end = '%d, %d, %d'%(today.year, today.month, today.day-1)
    f = web.DataReader(str(ticker), 'yahoo', start, end)
    for day in range(365, 369):
        last_year = (today - timedelta(days = day))
        formatted_year = last_year.strftime('%Y, %#m, %#d')
        try:
            yearly_price = f.ix[str(formatted_year)]['Adj Close']
            yearly_change = (float(current_price)-float(yearly_price))/float(yearly_price)*100
            yearly_change = '{:.2f}'.format(yearly_change)
            return yearly_change
            break
        except:
            continue

#------------------------------------------------------------------#
#FORMAT THE TEXT TO COMMENT INTO REDDIT

def current_output_text(ticker, CompanyName, current_price):
    current_price_text = ('Current price: $' + str(current_price) + '.')
    return current_price_text

def weekly_output_text(ticker, weekly_change):
    weekly_change = float(weekly_change)
    if weekly_change > 0.0:
        change_marker = '&#x25B2; +'
    elif weekly_change < 0.0:
        change_marker = '&#x25BC;'
    else:
        change_marker = 'even at '

    weekly_text = ('Over the past week, ' + ticker + ' is ' + change_marker + str(weekly_change) + '%.')
    return weekly_text

def monthly_output_text(ticker, monthly_change):
    try:
        monthly_change = float(monthly_change)
        if monthly_change > 0.0:
            month_marker = '&#x25B2; +'
        elif monthly_change < 0.0:
            month_marker = '&#x25BC;'
        else:
            month_marker = 'even at '
    except:
        pass

    if monthly_change != '':
        monthly_text = ('Over the past month, ' + ticker + ' is ' + month_marker + str(monthly_change) + '%.')
    else:
        monthly_text = ''
    return monthly_text

def yearly_output_text(ticker, yearly_change):
    try:
        yearly_change = float(yearly_change)
        if yearly_change > 0.0:
            year_marker = '&#x25B2; +'
        elif yearly_change < 0.0:
            year_marker = '&#x25BC;'
        else:
            year_marker = 'even at '
    except:
        pass

    if yearly_change != '':
        yearly_text = ('Over the past year, ' + ticker + ' is ' + year_marker + str(yearly_change) + '%.')
    else:
        yearly_text = ''
    return yearly_text

def market_cap_output_text(market_cap):
    if market_cap != '':
        market_cap_text = ('Current market cap: $' + str(market_cap) + '.')
        return market_cap_text
    else:
        market_cap_text = ''
        return market_cap_text


#------------------------------------------------------------------#
#Boot up the Reddit Bot by logging in and scanning subreddits

REDDIT_USERNAME = 'StockTrendsBot' #YOUR USERNAME as string
REDDIT_PASS = 'R@ilro2d' # YOUR PASSWORD as string

user_agent = ("StockTrendsBot")
r = praw.Reddit(user_agent = user_agent)
subredditList = ['asx', 'ausstocks', 'business', 'stocks', 'investing', 'finance', 'stockmarket', 'investmentclub', 'earningreports', 'economy', 'technology']

r.login(REDDIT_USERNAME, REDDIT_PASS, disable_warning=True)

def job():
    if not os.path.isfile("posts_replied_to.txt"):
        posts_replied_to = []
    else:
        with open("posts_replied_to.txt", "r") as f:
           posts_replied_to = f.read()
           posts_replied_to = posts_replied_to.split("\n")
           posts_replied_to = list(filter(None, posts_replied_to))

    for subreddit in subredditList:
        try:
            print('Switchin to ' + subreddit + '...')
            if subreddit not in ['ausstocks', 'asx']:
                subreddit = r.get_subreddit(subreddit)
                for submission in subreddit.get_new(limit=5):
                    if submission.id not in posts_replied_to:
                        for CompanyName, ticker in zip(CompanyNameList, TickerList):
                            CompanyName = re.escape(str(CompanyName))
                            CompanyName = '\\b'+CompanyName+'\\b'
                            ticker = re.escape(str(ticker))
                            if re.search(CompanyName, submission.title, re.IGNORECASE):
                                CompanyName = CompanyName.replace('\\b', '')
                                CompanyName = CompanyName.replace('\\', '')
                                current_price = getCurrentPrice(ticker)
                                market_cap = current_price[1]
                                current_price = current_price[0]
                                weekly_change = getWeeklyChange(ticker, current_price)
                                monthly_change = getMonthlyChange(ticker, current_price)
                                yearly_change = getYearlyChange(ticker, current_price)
                                current_text = current_output_text(ticker, CompanyName, current_price)
                                weekly_text = weekly_output_text(ticker, weekly_change)
                                monthly_text = monthly_output_text(ticker, monthly_change)
                                yearly_text = yearly_output_text(ticker, yearly_change)
                                market_cap_text = market_cap_output_text(market_cap)
                                if market_cap_text != '':
                                    if yearly_text != '':
                                        output = '**' + CompanyName + ' (' + ticker + ')**' + '\n\n' + current_text + '\n\n' + weekly_text + '\n\n' + monthly_text + '\n\n' + yearly_text + '\n\n' + market_cap_text + '\n\n' + '*****' + '\n\n' + 'Beep Boop, I am a bot. Message [HomerG](\/u\/HomerG) with any suggestions, ideas, death threats, etc.' + '\n\n' + 'To see source code and how I was made, click [here.](http:\/\/www.hofdata.com)'
                                    elif yearly_text == '':
                                        output = '**' + CompanyName + ' (' + ticker + ')**' + '\n\n' + current_text + '\n\n' + weekly_text + '\n\n' + monthly_text + '\n\n' + market_cap_text + '\n\n' + '*****' + '\n\n' + 'Beep Boop, I am a bot. Message [HomerG](\/u\/HomerG) with any suggestions, ideas, death threats, etc.' + '\n\n' + 'To see source code and how I was made, click [here.](http:\/\/www.hofdata.com)'
                                    elif monthly_text == '':
                                        output = '**' + CompanyName + ' (' + ticker + ')**' + '\n\n' + current_text + '\n\n' + weekly_text + '\n\n' + market_cap_text + '\n\n' + '*****' + '\n\n' + 'Beep Boop, I am a bot. Message [HomerG](\/u\/HomerG) with any suggestions, ideas, death threats, etc.' + '\n\n' + 'To see source code and how I was made, click [here.](http:\/\/www.hofdata.com)'
                                    elif weekly_text == '':
                                        output = '**' + CompanyName + ' (' + ticker + ')**' + '\n\n' + current_text + '\n\n' + market_cap_text + '\n\n' + '*****' + '\n\n' + 'Beep Boop, I am a bot. Message [HomerG](\/u\/HomerG) with any suggestions, ideas, death threats, etc.' + '\n\n' + 'To see source code and how I was made, click [here.](http:\/\/www.hofdata.com)'
                                elif market_cap_text == '':
                                    if yearly_text != '':
                                        output = '**' + CompanyName + ' (' + ticker + ')**' + '\n\n' + current_text + '\n\n' + weekly_text + '\n\n' + monthly_text + '\n\n' + yearly_text + '\n\n' + '*****' + '\n\n' + 'Beep Boop, I am a bot. Message [HomerG](\/u\/HomerG) with any suggestions, ideas, death threats, etc.' + '\n\n' + 'To see source code and how I was made, click [here.](http:\/\/www.hofdata.com)'
                                    elif yearly_text == '':
                                        output = '**' + CompanyName + ' (' + ticker + ')**' + '\n\n' + current_text + '\n\n' + weekly_text + '\n\n' + monthly_text + '\n\n' + '*****' + '\n\n' + 'Beep Boop, I am a bot. Message [HomerG](\/u\/HomerG) with any suggestions, ideas, death threats, etc.' + '\n\n' + 'To see source code and how I was made, click [here.](http:\/\/www.hofdata.com)'
                                    elif monthly_text == '':
                                        output = '**' + CompanyName + ' (' + ticker + ')**' + '\n\n' + current_text + '\n\n' + weekly_text + '\n\n' + '*****' + '\n\n' + 'Beep Boop, I am a bot. Message [HomerG](\/u\/HomerG) with any suggestions, ideas, death threats, etc.' + '\n\n' + 'To see source code and how I was made, click [here.](http:\/\/www.hofdata.com)'
                                    elif weekly_text == '':
                                        output = '**' + CompanyName + ' (' + ticker + ')**' + '\n\n' + current_text + '\n\n' + '*****' + '\n\n' + 'Beep Boop, I am a bot. Message [HomerG](\/u\/HomerG) with any suggestions, ideas, death threats, etc.' + '\n\n' + 'To see source code and how I was made, click [here.](http:\/\/www.hofdata.com)'
                                try:
                                    submission.add_comment(output)
                                    print ("Bot replying to : ", submission.title)
                                    #if posts_replied_to != '':
                                    posts_replied_to.append(str(submission.id))
                                except Exception as e:
                                    e = str(e)
                                    wait_time = [int(s) for s in e.split() if s.isdigit()]
                                    if wait_time != '':
                                        for item in wait_time:
                                            wait_time = item*60
                                            print('Sleeping for ' + str(item) + ' minutes...')
                                            time.sleep(wait_time)
                                            continue
                                    else:
                                        print('Sleeping for 10 minutes...')
                                        time.sleep(600)
                                        continue
                with open("posts_replied_to.txt", "w") as f:
                    for post_id in posts_replied_to:
                        f.write(str(post_id) + "\n")
                time.sleep(60)

            else:
                subreddit = r.get_subreddit(subreddit)
                for submission in subreddit.get_new(limit=5):
                    if submission.id not in posts_replied_to:
                        for CompanyName, ticker in zip(CompanyNameList[5749:], TickerList[5749:]):
                            CompanyName = re.escape(str(CompanyName))
                            CompanyName = '\\b'+CompanyName+'\\b'
                            ticker = re.escape(str(ticker))
                            if re.search(CompanyName, submission.title, re.IGNORECASE):
                                CompanyName = CompanyName.replace('\\b', '')
                                CompanyName = CompanyName.replace('\\', '')
                                ticker = ticker.replace('\\', '')
                                current_price = getCurrentPrice(ticker)
                                market_cap = current_price[1]
                                current_price = current_price[0]
                                weekly_change = getWeeklyChange(ticker, current_price)
                                monthly_change = getMonthlyChange(ticker, current_price)
                                yearly_change = getYearlyChange(ticker, current_price)
                                current_text = current_output_text(ticker, CompanyName, current_price)
                                weekly_text = weekly_output_text(ticker, weekly_change)
                                monthly_text = monthly_output_text(ticker, monthly_change)
                                yearly_text = yearly_output_text(ticker, yearly_change)
                                market_cap_text = market_cap_output_text(market_cap)
                                if market_cap_text != '':
                                    if yearly_text != '':
                                        output = '**' + CompanyName + ' (' + ticker + ')**' + '\n\n' + current_text + '\n\n' + weekly_text + '\n\n' + monthly_text + '\n\n' + yearly_text + '\n\n' + market_cap_text + '\n\n' + '*****' + '\n\n' + 'Beep Boop, I am a bot. Message [HomerG](\/u\/HomerG) with any suggestions, ideas, death threats, etc.' + '\n\n' + 'To see source code and how I was made, click [here.](http:\/\/www.hofdata.com)'
                                    elif yearly_text == '':
                                        output = '**' + CompanyName + ' (' + ticker + ')**' + '\n\n' + current_text + '\n\n' + weekly_text + '\n\n' + monthly_text + '\n\n' + market_cap_text + '\n\n' + '*****' + '\n\n' + 'Beep Boop, I am a bot. Message [HomerG](\/u\/HomerG) with any suggestions, ideas, death threats, etc.' + '\n\n' + 'To see source code and how I was made, click [here.](http:\/\/www.hofdata.com)'
                                    elif monthly_text == '':
                                        output = '**' + CompanyName + ' (' + ticker + ')**' + '\n\n' + current_text + '\n\n' + weekly_text + '\n\n' + market_cap_text + '\n\n' + '*****' + '\n\n' + 'Beep Boop, I am a bot. Message [HomerG](\/u\/HomerG) with any suggestions, ideas, death threats, etc.' + '\n\n' + 'To see source code and how I was made, click [here.](http:\/\/www.hofdata.com)'
                                    elif weekly_text == '':
                                        output = '**' + CompanyName + ' (' + ticker + ')**' + '\n\n' + current_text + '\n\n' + market_cap_text + '\n\n' + '*****' + '\n\n' + 'Beep Boop, I am a bot. Message [HomerG](\/u\/HomerG) with any suggestions, ideas, death threats, etc.' + '\n\n' + 'To see source code and how I was made, click [here.](http:\/\/www.hofdata.com)'
                                elif market_cap_text == '':
                                    if yearly_text != '':
                                        output = '**' + CompanyName + ' (' + ticker + ')**' + '\n\n' + current_text + '\n\n' + weekly_text + '\n\n' + monthly_text + '\n\n' + yearly_text + '\n\n' + '*****' + '\n\n' + 'Beep Boop, I am a bot. Message [HomerG](\/u\/HomerG) with any suggestions, ideas, death threats, etc.' + '\n\n' + 'To see source code and how I was made, click [here.](http:\/\/www.hofdata.com)'
                                    elif yearly_text == '':
                                        output = '**' + CompanyName + ' (' + ticker + ')**' + '\n\n' + current_text + '\n\n' + weekly_text + '\n\n' + monthly_text + '\n\n' + '*****' + '\n\n' + 'Beep Boop, I am a bot. Message [HomerG](\/u\/HomerG) with any suggestions, ideas, death threats, etc.' + '\n\n' + 'To see source code and how I was made, click [here.](http:\/\/www.hofdata.com)'
                                    elif monthly_text == '':
                                        output = '**' + CompanyName + ' (' + ticker + ')**' + '\n\n' + current_text + '\n\n' + weekly_text + '\n\n' + '*****' + '\n\n' + 'Beep Boop, I am a bot. Message [HomerG](\/u\/HomerG) with any suggestions, ideas, death threats, etc.' + '\n\n' + 'To see source code and how I was made, click [here.](http:\/\/www.hofdata.com)'
                                    elif weekly_text == '':
                                        output = '**' + CompanyName + ' (' + ticker + ')**' + '\n\n' + current_text + '\n\n' + '*****' + '\n\n' + 'Beep Boop, I am a bot. Message [HomerG](\/u\/HomerG) with any suggestions, ideas, death threats, etc.' + '\n\n' + 'To see source code and how I was made, click [here.](http:\/\/www.hofdata.com)'
                                try:
                                    submission.add_comment(output)
                                    print ("Bot replying to : ", submission.title)
                                    #if posts_replied_to != '':
                                    posts_replied_to.append(str(submission.id))
                                except Exception as e:
                                    e = str(e)
                                    wait_time = [int(s) for s in e.split() if s.isdigit()]
                                    if wait_time != '':
                                        for item in wait_time:
                                            wait_time = item*60
                                            print('Sleeping for ' + str(item) + ' minutes...')
                                            time.sleep(wait_time)
                                            continue
                                    else:
                                        print('Sleeping for 10 minutes...')
                                        time.sleep(600)
                                        continue
                with open("posts_replied_to.txt", "w") as f:
                    for post_id in posts_replied_to:
                        f.write(str(post_id) + "\n")
                time.sleep(60)

        except:
            continue


while True:
    job()
