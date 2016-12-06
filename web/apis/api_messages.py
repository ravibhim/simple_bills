from protorpc import messages

class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    data = messages.StringField(1, required=True)

class ProfileMessage(messages.Message):
    userId = messages.StringField(1)
    nickname = messages.StringField(2)

class FileMessage(messages.Message):
    filename = messages.StringField(1)
    original = messages.StringField(2)

class BillMessage(messages.Message):
    accountId = messages.IntegerField(1)

    billId = messages.StringField(2)
    desc = messages.StringField(3)
    currency_code = messages.StringField(4)
    amount = messages.FloatField(5)
    date = messages.StringField(6)
    tags = messages.MessageField(StringMessage,7,repeated=True)

    day = messages.IntegerField(8)
    month = messages.IntegerField(9)
    year = messages.IntegerField(10)
    staging_filepaths = messages.MessageField(StringMessage,11,repeated=True)
    filepaths = messages.MessageField(StringMessage,12,repeated=True)
    files = messages.MessageField(FileMessage,13,repeated=True)

class AccountMessage(messages.Message):
    accountId = messages.IntegerField(1)
    name = messages.StringField(2)
    tagstr = messages.StringField(3)
    default_currency_code = messages.StringField(4)
    tags = messages.MessageField(StringMessage,5, repeated=True)
    bills = messages.MessageField(BillMessage,6, repeated=True)

class AccountListMessage(messages.Message):
    accounts = messages.MessageField(AccountMessage,1,repeated=True)

class DayActivityMessage(messages.Message):
    date = messages.StringField(1)
    num_bills = messages.IntegerField(2)

class AccountActivityMessage(messages.Message):
    accountId = messages.IntegerField(1)
    name = messages.StringField(2)
    activity = messages.MessageField(DayActivityMessage,3,repeated=True)

class AccountsActivityMessage(messages.Message):
    data = messages.MessageField(AccountActivityMessage,1,repeated=True)

class SearchBillsRequest(messages.Message):
    accountId = messages.IntegerField(1)
    tags = messages.MessageField(StringMessage,2, repeated=True)
    start_date = messages.StringField(3)
    end_date = messages.StringField(4)
    query = messages.StringField(5)

class SearchBillsResponse(messages.Message):
    request = messages.MessageField(SearchBillsRequest,1)

    num_results = messages.IntegerField(2)
    results = messages.MessageField(BillMessage,3, repeated=True)
