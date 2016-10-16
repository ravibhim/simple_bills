import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote

from api_models import StringMessage

EMAIL_SCOPE = endpoints.EMAIL_SCOPE
API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID


@endpoints.api( name='simple_bills',
                version='v1',
                allowed_client_ids=[API_EXPLORER_CLIENT_ID],
                scopes=[EMAIL_SCOPE])
class SimpleBillApi(remote.Service):

    @endpoints.method(message_types.VoidMessage, StringMessage,
            path='getAccountIdsCreated',
            http_method='POST', name='getAccountIdsCreated')
    def getAccountIdsCreated(self, request):
        return StringMessage(data="You start somewhere")





# register API
api = endpoints.api_server([SimpleBillApi])
