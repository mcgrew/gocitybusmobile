import webapp2
from google.appengine.api.urlfetch import fetch
from xml.dom.minidom import parseString
import re
import json
from math import pi, cos, sin, acos
#from zipfile import ZipFile
from csv import DictReader

class MainPage( webapp2.RequestHandler ):
	def get( self ):
		stop_param = self.request.get( 'stop' )
		lat_param = self.request.get( 'lat' )
		lon_param = self.request.get( 'lon' )
		json_out = { 'stops':[]}
		self.response.headers[ 'Content-Type'] = 'application/json'

		if lat_param and lon_param:
			distance_param = self.request.get( 'distance' )
			if not distance_param:
				distance_param = 1
			limit_param = self.request.get( 'limit' )
			if limit_param:
				limit_param = int( limit_param )
			else:
				limit_param = 1000

			stops = get_stops_sorted( float( lat_param ), float( lon_param ))
			for stop in stops:
				if stop[ 'distance' ] < distance_param and limit_param > 0:
					json_out[ 'stops' ].append( stop )
					limit_param -= 1

		if ( stop_param ):
			json_out[ 'stops' ].append( get_times( stop_param ))

		callback = self.request.get( 'callback' )
		if callback:
			self.response.out.write( callback + "(" )
		json.dump( json_out, self.response.out, indent=4 )
		if callback:
			self.response.out.write( ")" )


def get_times( stop_id ):			
	"""
	Returns a dictionary containing incoming bus times.

		:Parameters:
			stop_id : str
				The id of the stop to request times for, in the form of BUS###. The 
				'BUS' part may be omitted.
	"""
	stop_id = "BUS" + stop_id.upper( ).replace( "BUS", "" )
	api_response = fetch( 
		'http://myride.gocitybus.com/widget/Default1.aspx?pt=30&code=%s' % 
		stop_id )

	if ( api_response.status_code == 200 ):
		xml_response = parseString( api_response.content )
		stop = xml_response.getElementsByTagName( 'Stop' )[ 0 ]
		current_stop = { 'stop_name': stop.getAttribute( 'name' ), 'buses':[]}
		buses = stop.getElementsByTagName( 'Bus' )
		for bus in buses:
			route_name = text_content( bus.getElementsByTagName( 'RouteName' )[ 0 ])
			time_left = text_content( bus.getElementsByTagName( 'TimeTillArrival' )[ 0 ])
			current_stop[ 'buses' ].append({ 'stop_code' : stop_id,
			                                 'route_name' : route_name, 
																			 'time_till_arrival' : time_left })
		return current_stop
	return {}

def get_stops_sorted( latitude, longitude ):
	"""
	Returns a sorted list of stops, sorted by distance from the given point.

		:Parameters:
			latitude : float
				The latitude of the point to measure from
			longitude : float
				The longitude of the point to measure from
	"""
	returnvalue = []
	stops_file = open( 'google_transit/stops.txt' )
	stops_iter = DictReader( stops_file )
	for stop in stops_iter:
		distance = angular_distance( latitude, longitude, 
							 float( stop[ 'stop_lat' ] ), float( stop[ 'stop_lon' ]))
		stop[ 'distance' ] = distance * MI
		returnvalue.append(( distance, stop ))
	stops_file.close( )
	returnvalue.sort( )
	return [ y for x,y in returnvalue ]

MI = 3963.1
"Multiplier to convert angular distance to miles"
KM = 6378
"Multiplier to convert angular distance to kilometers"

def angular_distance( lat1, lon1, lat2, lon2 ):
	"""
	Returns the angular distance between two points

		:Parameters:
			lat1 : float
				latitude of the first point.
			lon1 : float
				longitude of the first point.
			lat2 : float
				latitude of the second point.
			lon2 : float
				longitude of the second point.
	"""
	pi_180 = pi / 180
	return acos( cos( lat1 * pi_180 ) * cos( lon1 * pi_180 ) * cos( lat2 * pi_180) * cos( lon2 * pi_180 ) + 
			cos( lat1 * pi_180) * sin( lon1 * pi_180 ) * cos( lat2 * pi_180) * sin( lon2 * pi_180 ) + 
			sin( lat1 * pi_180 ) * sin( lat2 * pi_180 ))
		


application = webapp2.WSGIApplication([( '/.*', MainPage)], debug=True )

def main( ):
	application.run( )

def text_content( xml_node ):
		return re.sub( "<.*?>", "", xml_node.toxml( ))

if __name__ == "__main__":
	main( )


