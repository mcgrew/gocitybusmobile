from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api.urlfetch import fetch
from xml.dom.minidom import parseString
import re

class MainPage( webapp.RequestHandler ):
	def get( self ):
		self.response.headers[ 'Content-Type'] = 'text/html'
		self.response.out.write( "<!DOCTYPE html><html><head>" )
		if self.request.get( 'stop' ):
			self.response.out.write( '<meta http-equiv="refresh" content="60" />' )
		self.response.out.write( """
			<meta 
				name="viewport" 
				content="width=device-width;initial-scale=1.0;maximum-scale=1.0;user-scalable=0;" />
			<style type='text/css'>
				html, body {
					font-family: Arial, Helvetica, sans-serif;
					padding: 3px;
					margin: 0;
				}
				h1 {
					font-size: 1.2em;
					font-weight: bold;
				}
				h2 {
					font-size: 1.1em;
					font-weight: bold;
					padding: 0;
					margin: 0;
				}
				.bus {
					padding-bottom: 10px;
				}
			</style>
			</head>
			<body>
		""" )
		self.response.out.write( """
		<form method="get">
			<input type="text" name="stop" placeholder="Enter stop ID" />
			<input type="submit" value="Submit" />
		</form>	
		""")
		if self.request.get( 'stop' ):
			api_response = fetch( 
				'http://myride.gocitybus.com/widget/Default1.aspx?pt=30&code=BUS%s' % 
				self.request.get( 'stop' ).upper( ).replace( "BUS", ""))
			if ( api_response.status_code != 200 ):
				self.response.out.write( "<h1>Unable to process your request</h1>" )
			else:
				xml_response = parseString( api_response.content )
				stops = xml_response.getElementsByTagName( 'Stop' )
				for stop in stops:
					self.response.out.write( "<div><h1>%s</h1>" % stop.getAttribute( 'name' ))
					buses = stop.getElementsByTagName( 'Bus' )
					for bus in buses:
						route_name = text_content( bus.getElementsByTagName( 'RouteName' )[ 0 ])
						time_left = text_content( bus.getElementsByTagName( 'TimeTillArrival' )[ 0 ])
						self.response.out.write( """
							<div class="bus">
								<h2 class="busName">%s</h2>
								<div class="time">%s</div>
							</div>
						""" % ( route_name, time_left ))
					self.response.out.write( "</div>" )
			
		self.response.out.write( "</body></html>" )


application = webapp.WSGIApplication([( '/.*', MainPage)], debug=True )

def main( ):
	run_wsgi_app( application )

def text_content( xml_node ):
		return re.sub( "<.*?>", "", xml_node.toxml( ))

if __name__ == "__main__":
	main( )

