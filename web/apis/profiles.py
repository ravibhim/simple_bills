import endpoints
from protorpc import message_types
from protorpc import messages
from protorpc import remote

from models import *
import settings
from api_messages import *
from api_utils import *

EMAIL_SCOPE = endpoints.EMAIL_SCOPE
API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID
WEB_CLIENT_ID = settings.WEB_CLIENT_ID

@endpoints.api(name='profiles',
                version='v1',
                allowed_client_ids=[WEB_CLIENT_ID, API_EXPLORER_CLIENT_ID],
                scopes=[EMAIL_SCOPE])
class ProfilesApi(remote.Service):
    @endpoints.method(message_types.VoidMessage, ProfileMessage,
            path='getProfile',
            http_method='POST', name='getProfile')
    def getProfile(self, request):
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        profile = userProfile(user)

        pm = ProfileMessage()
        pm.userId = profile.userId
        pm.nickname = profile.nickname
        return pm
