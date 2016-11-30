from api_imports import *

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
