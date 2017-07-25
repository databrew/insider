# Load libraries
import requests as re
import pandas as pd
import time
from time import gmtime, strftime
from datetime import datetime, timedelta
from dateutil import parser
import yaml
import os.path
import numpy as np
from itertools import chain
import re

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

# Define a function for retrieving a page metric, like
# "page_negative_feedback"
def get_page_metric_date_range(name = 'Insiderinventions', start = "2017-06-20", stop = "2017-07-20", metric = "page_negative_feedback"):
	query = name + '/insights/' + metric + '?period=day&since=' + start + '&until=' + stop
	try:
		this_period = graph.request(query)
		# time.sleep(0.25)
		the_data = this_period['data'][0]['values']
		# Differential handling of those which have values broken down by type
		if "_by_" in metric:
			out = pd.DataFrame()
			for i in range(0, len(the_data)):
				sub_data = the_data[i]['value']
				sub_df = pd.DataFrame(pd.Series(sub_data), columns = {'value'})
				sub_df['sub_key'] = sub_df.index
				end_time = pd.Series(the_data[i]["end_time"]).tolist
				sub_df['end_time'] = pd.Series(the_data[i]["end_time"], index = sub_df.index)
				sub_df['key'] = metric
				sub_df['name'] = name
				sub_df = sub_df.reset_index()
				out = out.append(sub_df)
			out = out[["end_time", "value", "name", "key", "sub_key"]]
			# out = out.reset_index()
		else:
			series = pd.Series(the_data)
			out = pd.DataFrame.from_records(series)
			# Clean up the dataframe a bit
			out['name'] = name
			out['key'] = metric
			out['sub_key'] = 'NA'
		return(out)
	except:
		print " ERROR FOR " + query

# Define a function for retrieving page_negative_feedback (or other metrics) over all time
def get_page_metric_all(name = 'Insiderinventions', metric = "page_negative_feedback"):
	starts = ['2015-01-01', '2015-04-01', '2015-07-01', '2015-10-01', '2016-01-01', '2016-04-01', '2016-07-01', '2016-10-01', '2017-01-01', '2017-04-01', '2017-07-01', '2017-07-21']
	stops = []
	for i in range(1, len(starts)):
		stops.append((parser.parse(starts[i]) - timedelta(days=1)).strftime('%Y-%m-%d'))
	# Remove the last start (we'll use the not-all-time function for this)
	starts = starts[0:11]
	# Loop through each date range, getting the result for that range
	# out = []
	this_name = name
	this_metric = metric
	out = pd.DataFrame()
	for i in range(0, len(starts)):
		# time.sleep(0.1)
		this_start = starts[i]
		print '------ ' + this_start
		this_stop = stops[i]
		dataframe = get_page_metric_date_range(name = this_name, start = this_start, stop = this_stop, metric = this_metric)
		out = out.append(dataframe, ignore_index = True)
	return(out)

# Define a function for retrieving the "total likes as of today"
def get_likes_today(name = "Insiderinventions"):
	likes = graph.request(name + "?fields=fan_count")
	likes = likes.get("fan_count")
	df = pd.DataFrame({'end_time':today, 'value':likes, 'name': name, 'key':'fan_count', "sub_key":"NA"}, index = [0])
	df = df[['end_time', 'value', 'name', 'key','sub_key']]
	return df

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
		page_views_all = get_page_metric_all(name = this_page, metric = "page_views")
		# Get all fan adds ever
		print '--- Getting all fan adds for ' + this_page
		fan_adds_all = get_page_metric_all(name = this_page, metric = "page_fan_adds")
		# Get all negative feedback ever
		print '--- Getting all negative feedback for ' + this_page
		negative_feedback_all = get_page_metric_all(name = this_page, metric = "page_negative_feedback")
		# Get storytellers by country
		print '--- Getting storytellers by country for ' + this_page
		page_storytellers_by_country = get_page_metric_all(name = this_page, metric = "page_storytellers_by_country")
		# Get storytellers by city
		print '--- Getting storytellers by city for ' + this_page
		page_storytellers_by_city = get_page_metric_all(name = this_page, metric = "page_storytellers_by_city")
		# Get page_video_views
		print '--- Getting page_video_views for' + this_page
		page_video_views = get_page_metric_all(name = this_page, metric = "page_video_views")
		# Get page_storytellers_by_age_gender
		print '--- Getting page_storytellers_by_age_gender for' + this_page
		page_storytellers_by_age_gender = get_page_metric_all(name = this_page, metric = "page_storytellers_by_age_gender")
		# Bind together everything
		bound = page_views_all.append(fan_adds_all)
		bound = bound.append(negative_feedback_all)
		bound = bound.append(page_storytellers_by_country)
		bound = bound.append(page_storytellers_by_city)
		bound = bound.append(page_video_views)
		bound = bound.append(page_storytellers_by_age_gender)
		# Bind those dataframes to the master one
		try:
			print '--- Combining data from ' + this_page + ' with other pages'
			historical = historical.append(bound)
		except:
			continue
	# Write the historical data to a csv
	historical.to_csv('../data/historical.csv', index = False, encoding='utf-8')

# Now that we have the historical data, we'll also save a snapshot at today
# (in case things ever break in the future)
historical.to_csv('../data/backups/' + str(today) + '.csv', index = False, encoding='utf-8')

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
	# Get all page views recent
	print '--- Getting recent page views for ' + this_page
	page_views_recent = get_page_metric_date_range(name = this_page, start = recent_start_f, stop = recent_stop_f, metric = "page_views")
	# Get all fan adds recent
	print '--- Getting recent fan adds for ' + this_page
	fan_adds_recent = get_page_metric_date_range(name = this_page, start = recent_start_f, stop = recent_stop_f, metric = "page_fan_adds")
	# Get likes as of today
	print '--- Getting likes as of today for ' + this_page
	likes_now = get_likes_today(name = this_page)
	# Get negative feedback recently
	print '--- Getting recent negative feedback for ' + this_page
	page_negative_feedback_recent = get_page_metric_date_range(name = this_page, start = recent_start_f, stop = recent_stop_f, metric = "page_negative_feedback")
	# Get storytellers by country
	print '--- Getting storytellers by country for ' + this_page
	page_storytellers_by_country = get_page_metric_date_range(name = this_page, metric = "page_storytellers_by_country", start = recent_start_f, stop = recent_stop_f)
	# Get storytellers by city
	print '--- Getting storytellers by city for ' + this_page
	page_storytellers_by_city = get_page_metric_date_range(name = this_page, metric = "page_storytellers_by_city", start = recent_start_f, stop = recent_stop_f)
	# Get page_video_views
	print '--- Getting page_video_views for ' + this_page
	page_video_views = get_page_metric_date_range(name = this_page, metric = "page_video_views", start = recent_start_f, stop = recent_stop_f)
	# Get page_video_views
	print '--- Getting page_storytellers_by_age_gender for ' + this_page
	page_storytellers_by_age_gender = get_page_metric_date_range(name = this_page, metric = "page_storytellers_by_age_gender", start = recent_start_f, stop = recent_stop_f)

	# Bind the dataframes
	bound = page_views_recent.append(fan_adds_recent)
	bound = bound.append(likes_now)
	bound = bound.append(page_negative_feedback_recent)
	bound = bound.append(page_storytellers_by_country)
	bound = bound.append(page_storytellers_by_city)
	bound = bound.append(page_video_views)
	bound = bound.append(page_storytellers_by_age_gender)
	# Bind those dataframes to the master one
	try:
		print '--- Combining data from ' + this_page + ' with other pages'
		recent = recent.append(bound)
	except:
		continue

# Add a date column, so as to be compatible with historical
recent['date'] = recent['end_time'].astype('datetime64[ns]')
# Remove from historical the time which overlaps with the recent time
# but never removes "likes as of today" (since we can't retrieve that historically)
historical = historical[(historical['date'] < recent['date'].min()) | (historical['key'] == 'fan_count')]
# Combine with the recent data and historical data
historical = historical.append(recent)

# Clean up columns
historical = historical[['date', 'end_time', 'key', 'sub_key', 'name', 'value']]

# Over-write the historical csv
historical.to_csv('../data/historical.csv', index = False, encoding='utf-8')
