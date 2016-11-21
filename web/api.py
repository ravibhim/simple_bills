from apis.profiles import *
from apis.accounts import *
from apis.bills import *

# register API
api = endpoints.api_server([ProfilesApi, AccountsApi, BillsApi])
