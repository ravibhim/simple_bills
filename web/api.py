import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote

from api_models import StringMessage
from utils import *

EMAIL_SCOPE = endpoints.EMAIL_SCOPE
API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID


@endpoints.api( name='simplebills',
                version='v1',
                allowed_client_ids=[API_EXPLORER_CLIENT_ID],
                scopes=[EMAIL_SCOPE])
class SimpleBillApi(remote.Service):

    @endpoints.method(message_types.VoidMessage, StringMessage,
            path='getAccountIdsCreated',
            http_method='POST', name='getAccountIdsCreated')
    def getAccountIdsCreated(self, request):
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        profile = getProfile(user)

        return StringMessage(data='Here is the list {}'.format(map(str,profile.accountIds).join(profile.accountIds)))



# register API
api = endpoints.api_server([SimpleBillApi])
