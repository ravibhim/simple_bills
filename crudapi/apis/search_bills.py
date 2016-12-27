from api_imports import *

@endpoints.api(name='search_bills',
                version='v1',
                allowed_client_ids=[WEB_CLIENT_ID, API_EXPLORER_CLIENT_ID],
                scopes=[EMAIL_SCOPE])
class SearchBillsApi(remote.Service):
    @endpoints.method(SearchBillsRequest, SearchBillsResponse,
            path='searchBills',
            http_method='POST', name='searchBills')
    def searchBills(self, request):
        user = endpoints.get_current_user()
        raise_unless_user(user)

        accountId = request.accountId
        checkAccountAccess(user, accountId)
        account = Account.get(accountId)


        # Get all bills for the date range
        #bills = Bill.query(ancestor=accountKey).order(-Bill.date)



        bills = account.search_bills(
                    parser.parse(request.start_date),
                    parser.parse(request.end_date),
                    extractArrayFromStringMessageArray(request.tags),
                    request.query
                    )

        sb_response = SearchBillsResponse()
        sb_response.request = request
        for bill in bills:
            bm = buildBillMessage(bill)
            sb_response.results.append(bm)
        sb_response.num_results = bills.count()

        sb_response.check_initialized()
        return sb_response

'''
        # Do a brute force token intersection for now.
        if request.query:
            search_bills = []
            query_tokens_set = set([w.lower() for w in request.query.split()])
            for bill in bills:
                bill_tokens_set = set([w.lower() for w in bill.desc.split()])
                if query_tokens_set.intersection(bill_tokens_set):
                    search_bills.append(bill)
            # Reset bills based on query.
            bills = search_bills
            num_results = len(bills)
        else:
            num_results = bills.count()
'''
