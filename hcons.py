import requests
import csv
import json
from datetime import datetime

BASE_URL = 'https://smile.prsma.com/tukxi/api/'

def get_auth_credentials():
	with open('auth.json') as json_file:
    		return json.load(json_file)

def get_auth_header():
	# get access token
	print( 'Obtaining token!' )

	AUTH_URL = BASE_URL + 'auth/token'	

	credentials = get_auth_credentials()
	username = credentials[ 'username' ]
	password = credentials[ 'password' ]
	r = requests.post( AUTH_URL, data = { 'username': username, 'password': password }  )
	auth_json = r.json()
	auth_token = auth_json[ 'access_token' ]
	auth_header = 'Bearer {auth_token}'.format( auth_token = auth_token )

	print( 'Token obtained!' )

	return auth_header

def fetch_hcons():

	auth_header = get_auth_header()

	# get historical consumption
	print( 'Obtaining hcons!' )

	plug_id = '2'
	start = '2019-09-01T00:00:00.000Z'
	end = '2019-10-01T00:00:00.000Z'
	non_0 = 'true'
	hcons_url = BASE_URL + 'plug/{plug_id}/historical-consumption/{start}/{end}/{non_0}'.format( plug_id = plug_id, start = start, end = end, non_0 = non_0 )
	r = requests.get( hcons_url, headers = { 'Authorization': auth_header } )
	hcons = r.json()

	print( 'Hcons obtained!' )

	# filter hcons
	print( 'Filtering hcons!' )

	hcons_current_peak = { 'peak_value': 0 }
	hcons_peaks = [ ]
	hcons_filtered = [ ]

	HCONS_MIN_THRESHOLD = 50
	HCONS_PEAK_THRESHOLD = 320

	for h in hcons:
		measure_cons = float( h[ 'measure_cons' ] )
		timestamp = h[ 'timestamp' ]
		
		# > 50w
		if measure_cons > HCONS_MIN_THRESHOLD:
			hcons_filtered.append( h.copy() )

		else:
			# nada
			pass

		# detect charging
		if measure_cons > HCONS_PEAK_THRESHOLD:

			# new charging period?
			if hcons_current_peak[ 'peak_value' ] == 0:

				# yes, new charging period
				hcons_current_peak[ 'peak_value' ] = measure_cons
				hcons_current_peak[ 'begin_time' ] = timestamp

			else:

				# nope, same charging period
				# if bigger value, update it
				if measure_cons > hcons_current_peak[ 'peak_value' ]:
					hcons_current_peak[ 'peak_value' ] = measure_cons
					hcons_current_peak[ 'peak_time' ] = timestamp

		else:

			# been in a charging period before?
			if hcons_current_peak[ 'peak_value' ] > 0:

				# yes, store end timestamp
				hcons_current_peak[ 'end_time' ] = timestamp
				hcons_peaks.append( hcons_current_peak )
				hcons_current_peak = { 'peak_value' : 0 }

			else:

				#nope, does nothing
				pass							

	print( 'Hcons filtered!' ) 

	export_hcons_filtered( hcons_filtered )
	export_hcons_peaks( hcons_peaks )

def export_hcons_filtered(hcons_filtered):

	# exporting filtered hcons
	print( 'Exporting filtered hcons!' )

	CSV_FILENAME = 'hcons_exported_filtered.csv'
	with open( CSV_FILENAME, mode = 'w' ) as csv_file:

	    csv_writer = csv.writer( csv_file, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL )
	    csv_writer.writerow( [ 'timestamp', 'measure_cons' ] )

	    for h in hcons_filtered:
	    	csv_writer.writerow( [ h[ 'timestamp' ], h[ 'measure_cons'] ] )

	print( 'Filtered Hhcons exported!' )    

def export_hcons_peaks(hcons_peaks):	

	# exporting peak hcons
	print( 'Exporting peak hcons!' )

	CSV_FILENAME = 'hcons_exported_peak.csv'
	with open( CSV_FILENAME, mode = 'w' ) as csv_file:

	    csv_writer = csv.writer( csv_file, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL )
	    csv_writer.writerow( [ 'id', 'begin_time', 'end_time', 'duration', 'peak_time', 'peak_value' ] )

	    for index, h in enumerate( hcons_peaks ):
	    	duration = calculate_tstamp_duration( h[ 'begin_time' ], h[ 'end_time' ] )
	    	csv_writer.writerow( [ index, h[ 'begin_time' ], h[ 'end_time' ], duration, h[ 'peak_time' ], h[ 'peak_value' ] ] )

	print( 'Peak hcons exported!' )   

def calculate_tstamp_duration(begin_time, end_time):
	fmt = '%Y-%m-%dT%H:%M:%S.000Z'
	begin_t = datetime.strptime( begin_time, fmt )
	end_t = datetime.strptime( end_time, fmt )
	dur_minutes = int( round( abs( (begin_t - end_t).total_seconds() ) / 60) )
	return dur_minutes

fetch_hcons()