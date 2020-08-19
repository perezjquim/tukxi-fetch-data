import requests
import csv
import json

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

	hcons_current_peak = { }
	hcons_current_peak_cons = 0
	hcons_peaks = [ ]
	hcons_filtered = [ ]

	HCONS_MIN_THRESHOLD = 50
	HCONS_PEAK_THRESHOLD = 320

	for h in hcons:
		measure_cons = int( h[ 'measure_cons' ] )
		
		# > 50w
		if measure_cons > HCONS_MIN_THRESHOLD:
			hcons_filtered.append( h )

		else:
			
			# nada
			pass

		# detect charging peak
		if measure_cons > HCONS_PEAK_THRESHOLD:

			if measure_cons > hcons_current_peak_cons:
				hcons_current_peak = h
				hcons_current_peak_cons = int( hcons_current_peak[ 'measure_cons' ] )		

		else:

			if hcons_current_peak_cons > 0:
				hcons_peaks.append( hcons_current_peak )
				hcons_current_peak_cons = 0
				hcons_current_peak = { }							

	print( 'Hcons filtered!' )

	# exporting filtered hcons
	print( 'Exporting filtered hcons!' )

	CSV_FILENAME = 'hcons_exported_filtered.csv'
	with open( CSV_FILENAME, mode = 'w' ) as csv_file:
	    csv_writer = csv.writer( csv_file, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL )
	    csv_writer.writerow( [ 'timestamp', 'measure_cons' ] )
	    for h in hcons_filtered:
	    	csv_writer.writerow( [ h[ 'timestamp' ], h[ 'measure_cons'] ] )

	print( 'Filtered Hhcons exported!' )    	

	# exporting peak hcons
	print( 'Exporting peak hcons!' )

	CSV_FILENAME = 'hcons_exported_peak.csv'
	with open( CSV_FILENAME, mode = 'w' ) as csv_file:
	    csv_writer = csv.writer( csv_file, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL )
	    csv_writer.writerow( [ 'timestamp', 'measure_cons' ] )
	    for h in hcons_peaks:
	    	csv_writer.writerow( [ h[ 'timestamp' ], h[ 'measure_cons'] ] )

	print( 'Peak hcons exported!' )    	

fetch_hcons()