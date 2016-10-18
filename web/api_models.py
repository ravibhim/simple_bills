from protorpc import messages

class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    data = messages.StringField(1, required=True)

class AccountIdsMessage(messages.Message):
    data = messages.IntegerField(1, repeated=True)

class BillListFormMessage(messages.Message):
    accountId = messages.IntegerField(1, required=True)

class BillMessage(messages.Message):
    billId = messages.IntegerField(1, required=True)
    amount = messages.IntegerField(2)

    day = messages.IntegerField(3)
    month = messages.IntegerField(4)
    year = messages.IntegerField(5)

class BillListMessage(messages.Message):
    bills = messages.MessageField(BillMessage,1,repeated=True)



