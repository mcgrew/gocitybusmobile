from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api.urlfetch import fetch
from xml.dom.minidom import parseString
import re
import json
from math import pi, cos, sin, acos

class MainPage( webapp.RequestHandler ):
	def get( self ):
		stop_param = self.request.get( 'stop' )
		location_param = self.request.get( 'location' )
		json_out = { 'stops':{}}

		if ( location_param ):
			distance_param = self.request.get( 'distance' )
			if not distance_param:
				distance_param = 1
			stops = self.get_stops_sorted( *[ float( i ) for i in location_param.split( ',' )])
			for distance,stop in stops:
				if ( distance < distance_param ):
					json_out[ 'stops' ][ stop[ 'id' ]] = stop

		if ( stop_param ):
			json_out[ stop_param ] = self.get_times( stop_param )

		callback = self.request.get( 'callback' )
		if callback:
			self.response.out.write( callback + "(" )
		json.dump( json_out, self.response.out, indent=4 )
		if callback:
			self.response.out.write( ")" )

	def get_times( self, stop_param ):			
		stop_param = stop_param.upper( )
		self.response.headers[ 'Content-Type'] = 'application/json'
		api_response = fetch( 
			'http://myride.gocitybus.com/widget/Default1.aspx?pt=30&code=BUS%s' % 
			self.request.get( 'stop' ).replace( "BUS", "" ))
		self.response.headers[ 'status' ] = api_response.status_code
		if ( api_response.status_code == 200 ):
			xml_response = parseString( api_response.content )
			stop = xml_response.getElementsByTagName( 'Stop' )[ 0 ]
			current_stop = { 'name': stop.getAttribute( 'name' ), 'buses':[]}
			buses = stop.getElementsByTagName( 'Bus' )
			for bus in buses:
				route_name = text_content( bus.getElementsByTagName( 'RouteName' )[ 0 ])
				time_left = text_content( bus.getElementsByTagName( 'TimeTillArrival' )[ 0 ])
				current_stop[ 'buses' ].append({ 'routeName' : route_name, 
																				 'timeTillArrival' : time_left })
			return current_stop
		return {}
	
	def get_stops_sorted( self, latitude, longitude ):
		returnvalue = []
		stops_json = open(  'stops.json' )
		stops = json.load( stops_json )[ 'stops' ]
		stops_json.close( )
		for stop_id in stops:
			stop = stops[ stop_id ]
			distance = self.distance_mi( latitude, longitude, 
			                             *[ float( i ) for i in stop[ 'location' ]])
			stop[ 'distance' ] = distance
			returnvalue.append(( distance, stop ))
		returnvalue.sort( )
		return returnvalue
	
	def distance_mi( self, lat1, lon1, lat2, lon2 ):
		pi_180 = pi / 180
		return ( acos( cos( lat1 * pi_180 ) * cos( lon1 * pi_180 ) * cos( lat2 * pi_180) * cos( lon2 * pi_180 ) + 
				cos( lat1 * pi_180) * sin( lon1 * pi_180 ) * cos( lat2 * pi_180) * sin( lon2 * pi_180 ) + 
				sin( lat1 * pi_180 ) * sin( lat2 * pi_180 )) * 3963.1)
			


application = webapp.WSGIApplication([( '/.*', MainPage)], debug=True )

def main( ):
	run_wsgi_app( application )

def text_content( xml_node ):
		return re.sub( "<.*?>", "", xml_node.toxml( ))

if __name__ == "__main__":
	main( )


