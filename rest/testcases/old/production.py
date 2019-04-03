"""
The server that handles all requests to the backend
"""

"""
The database used by default
"""
DATABASE = "biobank"

# import oauth2
# from oauth2.store.memory import ClientStore, TokenStore

def application(environ, start_response):
	status = '200 OK'
	output = '%s\n' % '\n'.join(sys.path)
	# output = sys.version
	output = output.encode("utf-8")
	response_headers = [('Content-type', 'text/plain'),
				('Content-Length', str(len(output)))]
	start_response(status, response_headers)
	return [output]
