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

class BillMessage(messages.Message):
    accountId = messages.IntegerField(1)

    billId = messages.IntegerField(2)
    amount = messages.IntegerField(3)
    date = messages.StringField(4)

    day = messages.IntegerField(5)
    month = messages.IntegerField(6)
    year = messages.IntegerField(7)

class AccountDetailMessage(messages.Message):
    account = messages.MessageField(AccountMessage,1)
    bills = messages.MessageField(BillMessage,2, repeated=True)

class AccountListMessage(messages.Message):
    accounts = messages.MessageField(AccountMessage,1,repeated=True)


