from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api.urlfetch import fetch
from xml.dom.minidom import parseString
import re
import json

class MainPage( webapp.RequestHandler ):
	def get( self ):
		self.response.headers[ 'Content-Type'] = 'application/json'
		api_response = fetch( 
			'http://myride.gocitybus.com/widget/Default1.aspx?pt=30&code=BUS%s' % 
			self.request.get( 'stop' ).upper( ).replace( "BUS", "" ))
		self.response.headers[ 'status' ] = api_response.status_code
		json_out = { 'stops':[]}
		if ( api_response.status_code != 200 ):
			json_out[ 'error' ] = "Unable to process your request"
		else:
			xml_response = parseString( api_response.content )
			stops = xml_response.getElementsByTagName( 'Stop' )
			for stop in stops:
				current_stop = { 'name': stop.getAttribute( 'name' ), 'buses':[]}
				buses = stop.getElementsByTagName( 'Bus' )
				for bus in buses:
					route_name = text_content( bus.getElementsByTagName( 'RouteName' )[ 0 ])
					time_left = text_content( bus.getElementsByTagName( 'TimeTillArrival' )[ 0 ])
					current_stop[ 'buses' ].append({ 'routeName' : route_name, 
					                                 'timeTillArrival' : time_left })
				json_out[ "stops" ].append( current_stop )
			callback = self.request.get( 'callback' )
			if callback:
				self.response.out.write( callback + "(" )
			json.dump( json_out, self.response.out, indent=4 )
			if callback:
				self.response.out.write( ")" )
			


application = webapp.WSGIApplication([( '/.*', MainPage)], debug=True )

def main( ):
	run_wsgi_app( application )

def text_content( xml_node ):
		return re.sub( "<.*?>", "", xml_node.toxml( ))

if __name__ == "__main__":
	main( )


