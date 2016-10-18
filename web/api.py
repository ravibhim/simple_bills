import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote

from google.appengine.ext.ndb import Key

from api_models import *
from models import *
from utils import *

EMAIL_SCOPE = endpoints.EMAIL_SCOPE
API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID


@endpoints.api( name='simplebills',
                version='v1',
                allowed_client_ids=[API_EXPLORER_CLIENT_ID],
                scopes=[EMAIL_SCOPE])
class SimpleBillApi(remote.Service):

    def _copyAccountIdsMessage(self, profile):
        aim = AccountIdsMessage()
        for accountId in profile.accountIds:
            aim.data.append(accountId)
        aim.check_initialized()
        return aim

    @endpoints.method(message_types.VoidMessage, AccountIdsMessage,
            path='getAccountIdsCreated',
            http_method='POST', name='getAccountIdsCreated')
    def getAccountIdsCreated(self, request):
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        profile = getProfile(user)
        return self._copyAccountIdsMessage(profile)


    def _copyAccountBills(self, accountId):
        blm = BillListMessage()

        account_key = Key(Account, accountId)
        account = account_key.get()
        bills = Bill.query(ancestor=account_key).order(-Bill.date)
        for bill in bills:
            bm = BillMessage()
            bm.billId = bill.key.id()
            bm.amount = bill.amount

            bm.day = bill.day
            bm.month = bill.month
            bm.year = bill.year
            bm.check_initialized()

            blm.bills.append(bm)
        blm.check_initialized()
        return blm

    @endpoints.method(BillListFormMessage, BillListMessage,
            path='getBillsList',
            http_method='POST', name='getBillsList')
    def getBills(self, request):
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        profile = getProfile(user)
        if request.accountId in profile.accountIds:
            return self._copyAccountBills(request.accountId)
        else:
            raise endpoints.ForbiddenException('Current user not authorized to access account_id {}'.format(request.accountId))



# register API
api = endpoints.api_server([SimpleBillApi])
