from protorpc import messages

class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    data = messages.StringField(1, required=True)

class ProfileMessage(messages.Message):
    userId = messages.StringField(1)
    nickname = messages.StringField(2)

class ImageMessage(messages.Message):
    original = messages.StringField(1)

class BillMessage(messages.Message):
    accountId = messages.IntegerField(1)

    billId = messages.StringField(2)
    desc = messages.StringField(3)
    amount = messages.IntegerField(4)
    date = messages.StringField(5)
    tags = messages.MessageField(StringMessage,6,repeated=True)

    day = messages.IntegerField(7)
    month = messages.IntegerField(8)
    year = messages.IntegerField(9)
    staging_filepaths = messages.MessageField(StringMessage,10,repeated=True)
    filepaths = messages.MessageField(StringMessage,11,repeated=True)
    img_urls = messages.MessageField(ImageMessage,12,repeated=True)

class AccountMessage(messages.Message):
    accountId = messages.IntegerField(1)
    name = messages.StringField(2)
    tagstr = messages.StringField(3)
    tags = messages.MessageField(StringMessage,4, repeated=True)
    bills = messages.MessageField(BillMessage,5, repeated=True)

class AccountListMessage(messages.Message):
    accounts = messages.MessageField(AccountMessage,1,repeated=True)
