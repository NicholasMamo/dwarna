import os
import sys
import signal

from multiprocessing import Process
from wsgiref.simple_server import make_server, WSGIRequestHandler

sys.path.insert(0, os.path.abspath(os.path.realpath(__file__) + '/../../../'))

from oauth2 import Provider
from oauth2.store.memory import ClientStore, TokenStore
from oauth2.tokengenerator import Uuid4
from oauth2.web.wsgi import Application
from oauth2.grant import GrantHandlerFactory, ClientCredentialsGrant, ClientCredentialsHandler, ScopeGrant

class OAuthRequestHandler(WSGIRequestHandler):
    """
    Request handler that enables formatting of the log messages on the console.
    This handler is used by the python-oauth2 application.
    """
    def address_string(self):
        return "python-oauth2"

class CustomClientCredentialsGrant(GrantHandlerFactory, ScopeGrant):
    grant_type = "client_credentials"

    def __call__(self, request, server):
        if request.path != server.token_path:
            return None

        if request.post_param("grant_type") == self.grant_type:
            scope_handler = self._create_scope_handler()
            scope_handler.send_back = True
            return ClientCredentialsHandler(
                access_token_store=server.access_token_store,
                client_authenticator=server.client_authenticator,
                scope_handler=scope_handler,
                token_generator=server.token_generator)
        return None

class TestProvider(Provider):
		
	def dispatch(self, request, environ):
		response = super(TestProvider, self).dispatch(request, environ)
		print(self.grant_types[0])
		for access_token, obj in self.access_token_store.access_tokens.items():
			print("Access token", access_token)
			print("\tbelongs to", obj.client_id)
			print("\texpires at", obj.expires_at, "(Expired)" if obj.is_expired() else "(Not expired)")
			print("\tscopes", ', '.join(obj.scopes))
		return response

def run_auth_server():
    try:
        client_store = ClientStore()
        client_store.add_client(client_id="abc", client_secret="xyz",
                                redirect_uris=[])
        
        token_store = TokenStore()
        token_gen = Uuid4()
        token_gen.expires_in['client_credentials'] = 10

        auth_controller = TestProvider(
            access_token_store=token_store,
            auth_code_store=token_store,
            client_store=client_store,
            token_generator=token_gen)
        client_credentials_grant = CustomClientCredentialsGrant(scopes=["consent", "view_consent", "create_participant", "view"], default_scope="view")
        auth_controller.add_grant(client_credentials_grant)


        app = Application(provider=auth_controller)

        httpd = make_server('', 8080, app, handler_class=OAuthRequestHandler)

        print("Starting implicit_grant oauth2 server on http://localhost:8080/...")
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()

def main():
    auth_server = Process(target=run_auth_server)
    auth_server.start()
    print("To test getting an auth token, execute the following curl command:")
    print(
        "curl --ipv4 -v -X POST"
        " -d 'grant_type=client_credentials&client_id=abc&client_secret=xyz' "
        "http://localhost:8080/token"
    )

    def sigint_handler(signal, frame):
        print("Terminating server...")
        auth_server.terminate()
        auth_server.join()

    signal.signal(signal.SIGINT, sigint_handler)

if __name__ == "__main__":
    main()
