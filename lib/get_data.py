# Load libraries
import requests as re
import pandas as pd
from time import gmtime, strftime
from datetime import datetime, timedelta
from dateutil import parser
import yaml
import os.path
import numpy as np

import os
os.chdir('/home/joebrew/Documents/insider/lib')

# For the facebook library, install as follows via terminal:
# # pip install -e git+https://github.com/mobolic/facebook-sdk.git#egg=facebook-sdk
import facebook

# Import credentials
stram = open("../credentials/credentials.yaml", "r")
credentials = yaml.load(stram)

# Define today
today = strftime("%Y-%m-%d %H:%M:%S", gmtime())

# Define access token
# expires september 17th
# may need to be managed (debugged) thereafter at
# https://developers.facebook.com/tools/accesstoken/
token = credentials['app_token']

# Connect to the api, creating a connection object named graph
# https://medium.com/towards-data-science/how-to-use-facebook-graph-api-and-extract-data-using-python-1839e19d6999
graph = facebook.GraphAPI(access_token=token, version = 2.7)

# Define a function for retrieving the "total likes as of today"
def get_likes_today(name = "Insiderinventions"):
	likes = graph.request(name + "?fields=fan_count")
	likes = likes.get("fan_count")
	df = pd.DataFrame({'end_time':today, 'value':likes, 'name': name, 'key':'fan_count'}, index = [0])
	df = df[['end_time', 'value', 'name', 'key']]
	return df

# Define function for getting page views
def get_page_views_date_range(name = "Insiderinventions", start = "2017-06-20", stop = "2017-07-20"):
	# Set start to stop, if necessary
	if stop is None:
		stop = start
	# Parse the times
	start = parser.parse(start)
	stop = parser.parse(stop)
	# change start to unix time
	start = start.strftime("%s")
	stop = stop.strftime("%s")
	query = name + '/insights/page_views?since=' + str(start) + '&until=' + str(stop)
	out = graph.request(query)
	out = out['data'][0]['values']
	series = pd.Series(out)
	out = pd.DataFrame.from_records(series)
	# Clean up the dataframe a bit
	out['name'] = name
	out['key'] = 'page_views'
	return(out)

# Define function for getting page views for all time
def get_page_views_all(name = "Insiderinventions"):
	starts = ['2015-01-01', '2015-04-01', '2015-07-01', '2015-10-01', '2016-01-01', '2016-04-01', '2016-07-01', '2016-10-01', '2017-01-01', '2017-04-01', '2017-07-01', '2017-07-21']
	stops = []
	for i in range(1, len(starts)):
		stops.append((parser.parse(starts[i]) - timedelta(days=1)).strftime('%Y-%m-%d'))
	# Remove the last start (we'll use the not-all-time function for this)
	starts = starts[0:11]
	# Loop through each date range, getting the result for that range
	# out = []
	out = pd.DataFrame()
	for i in range(0, len(starts)):
		this_start = starts[i]
		print '------ ' + this_start
		this_stop = stops[i]
		query = name + '/insights/page_views?since=' + this_start + '&until=' + this_stop
		this_period = graph.request(query)
		the_data = this_period['data'][0]['values']
		series = pd.Series(the_data)
		dataframe = pd.DataFrame.from_records(series)
		out = out.append(dataframe, ignore_index = True)
	# Clean up the dataframe a bit
	out['name'] = name
	out['key'] = 'page_views'
	return(out)

# Define function for getting page fan adds (can only take a range of 93 days max)
def get_page_fan_adds_date_range(name = "Insiderinventions", start = "2017-06-20", stop = '2017-07-20'):
	query = name + '/insights/page_fan_adds?since=' + start + '&until=' + stop
	this_period = graph.request(query)
	the_data = this_period['data'][0]['values']
	series = pd.Series(the_data)
	out = pd.DataFrame.from_records(series)
	# Clean up the dataframe a bit
	out['name'] = name
	out['key'] = 'fan_adds'
	return(out)

# Define function for getting page fan adds over all time
def get_page_fan_adds_all(name = "Insiderinventions"):
	starts = ['2015-01-01', '2015-04-01', '2015-07-01', '2015-10-01', '2016-01-01', '2016-04-01', '2016-07-01', '2016-10-01', '2017-01-01', '2017-04-01', '2017-07-01', '2017-07-21']
	stops = []
	for i in range(1, len(starts)):
		stops.append((parser.parse(starts[i]) - timedelta(days=1)).strftime('%Y-%m-%d'))
	# Remove the last start (we'll use the not-all-time function for this)
	starts = starts[0:11]
	# Loop through each date range, getting the result for that range
	# out = []
	out = pd.DataFrame()
	for i in range(0, len(starts)):
		this_start = starts[i]
		print '------ ' + this_start
		this_stop = stops[i]
		query = name + '/insights/page_fan_adds?since=' + this_start + '&until=' + this_stop
		this_period = graph.request(query)
		the_data = this_period['data'][0]['values']
		series = pd.Series(the_data)
		dataframe = pd.DataFrame.from_records(series)
		out = out.append(dataframe, ignore_index = True)
	# Clean up the dataframe a bit
	out['name'] = name
	out['key'] = 'fan_adds'
	return(out)

# Define a list of the pages for which we're doing this
facebook_pages = ["Insiderinventions", "Insiderfood", "thisisinsiderfitness", "Insidercheese", "INSIDERpopculture", "Insiderdessert", "Insiderscience", "thisisinsiderart", "thisisinsiderdesign", "thisisinsider", "thisisinsiderstyle", "thisisinsidertravel", "thisisinsidervideo", "Insiderbeauty", "thisisinsiderhome", "insiderkitchen"]

# Get this historical stuff (through the end of June 2017)
# And save to csvs (only need to do this once)
historical_file = '../data/historical.csv'
if os.path.isfile(historical_file):
	# The historical data already exists - read it in
	historical = pd.read_csv(historical_file)
else:
	# The historical data does not yet exist - create and save it
	historical = pd.DataFrame()
	for i in range(0, len(facebook_pages)):
		# Define this page
		this_page = facebook_pages[i]
		print 'Working on history for ' + this_page
		# Get all page views ever
		print '--- Getting all page views for ' + this_page
		page_views_all = get_page_views_all(name = this_page)
		# Get all fan adds ever
		print '--- Getting all fan adds for ' + this_page
		fan_adds_all = get_page_fan_adds_all(name = this_page)
		# Bind the two dataframes
		bound = page_views_all.append(fan_adds_all)
		# Bind those dataframes to the master one
		print '--- Combining data from ' + this_page + ' with other pages'
		historical = historical.append(bound)

	# Write the historical data to a csv
	historical.to_csv('../data/historical.csv')

# Now that we have the historical data, we'll also save a snapshot at today
# (in case things ever break in the future)
historical.to_csv('../data/backups/' + str(today) + '.csv')

# Convert to date
historical['date'] = historical['end_time'].astype('datetime64[ns]')

# Now that we have historical, we'll read everything between
# the end of historical and now (ie, more recent data)
end_of_historical = historical['date'].max()
end_of_historical_f = end_of_historical.strftime("%Y-%m-%d")
today_nf = np.datetime64(today)
today_nf = pd.to_datetime(today_nf)
today_f = today_nf.strftime("%Y-%m-%d")

# For good measure, we'll replace the last day of historical
# in case it was incomplete
recent_start = end_of_historical - timedelta(days=1)
recent_start_f = recent_start.strftime("%Y-%m-%d")

# Also for good measure, we'll get data through tomorrow (even though this)
# is impossbile) to make sure we're getting all data through today
recent_stop = today_nf + timedelta(days=1)
recent_stop_f = recent_stop.strftime("%Y-%m-%d")

# In case we're ahead of historical, get the data for which we're ahead
recent = pd.DataFrame()
for i in range(0, len(facebook_pages)):
	# Define this page
	this_page = facebook_pages[i]
	print 'Working on recent data for ' + this_page
	# Get all page views ever
	print '--- Getting recent page views for ' + this_page
	page_views_recent = get_page_views_date_range(name = this_page, start = recent_start_f, stop = recent_stop_f)
	# Get all fan adds ever
	print '--- Getting recent fan adds for ' + this_page
	fan_adds_recent = get_page_fan_adds_date_range(name = this_page, start = recent_start_f, stop = recent_stop_f)
	# Get likes as of today
	print '--- Getting likes as of today for ' + this_page
	likes_now = get_likes_today(name = this_page)
	# Bind the three dataframes
	bound = page_views_recent.append(fan_adds_recent)
	bound = bound.append(likes_now)
	# Bind those dataframes to the master one
	print '--- Combining data from ' + this_page + ' with other pages'
	recent = recent.append(bound)

# Add a date column, so as to be compatible with historical
recent['date'] = recent['end_time'].astype('datetime64[ns]')
# Remove from historical the time which overlaps with the recent time
# but never removes "likes as of today" (since we can't retrieve that historically)
historical = historical[(historical['date'] < recent['date'].min()) | (historical['key'] == 'fan_count')]
# Combine with the recent data and historical data
historical = historical.append(recent)

# Clean up columns
historical = historical[['date', 'end_time', 'key', 'name', 'value']]

# Over-write the historical csv
historical.to_csv('../data/historical.csv')
