from protorpc import messages

class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    data = messages.StringField(1, required=True)

class ProfileMessage(messages.Message):
    userId = messages.StringField(1)
    nickname = messages.StringField(2)

class AccountMessage(messages.Message):
    accountId = messages.IntegerField(1)
    name = messages.StringField(2)
    tags = messages.MessageField(StringMessage,3, repeated=True)

class ImageMessage(messages.Message):
    original = messages.StringField(1)

class BillMessage(messages.Message):
    accountId = messages.IntegerField(1)

    billId = messages.StringField(2)
    desc = messages.StringField(3)
    amount = messages.IntegerField(4)
    date = messages.StringField(5)

    day = messages.IntegerField(6)
    month = messages.IntegerField(7)
    year = messages.IntegerField(8)
    staging_filepaths = messages.MessageField(StringMessage,9,repeated=True)
    filepaths = messages.MessageField(StringMessage,10,repeated=True)
    img_urls = messages.MessageField(ImageMessage,11,repeated=True)

class AccountDetailMessage(messages.Message):
    account = messages.MessageField(AccountMessage,1)
    bills = messages.MessageField(BillMessage,2, repeated=True)

class AccountListMessage(messages.Message):
    accounts = messages.MessageField(AccountMessage,1,repeated=True)
