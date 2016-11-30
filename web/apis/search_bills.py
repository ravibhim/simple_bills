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

        sb_response = SearchBillsResponse()
        sb_response.request = request

        profile = userProfile(user)
        accountId = int(request.accountId)
        checkAccountBelongsToUser(user, accountId)

        accountKey = Key(Account, accountId)

        # Get all bills
        bills = Bill.query(ancestor=accountKey).order(-Bill.date)

        # Filter on tags if present
        if len(request.tags):
            bills = bills.filter(Bill.tags.IN(extract_array_from_data_list(request.tags)))

        # Filter on start_date if present
        if request.start_date:
            bills = bills.filter(Bill.date >= parser.parse(request.start_date))

        # Filter on end_date if present
        if request.end_date:
            bills = bills.filter(Bill.date <= parser.parse(request.end_date))

        # Filter on amount is present
        if request.amount:
            bills = bills.filter(Bill.amount == int(request.amount))

        for bill in bills:
            bm = buildBillMessage(bill)
            sb_response.results.append(bm)
        sb_response.num_results = bills.count()

        sb_response.check_initialized()
        return sb_response

