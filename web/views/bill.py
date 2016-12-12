from view_imports import *

from dateutil import parser
import json

class CreateBill(BaseHandler):
    @check_credentials
    def post(self, account_id):
        # Put the file in GCS first and get the stage filepath
        # Send that info to the API so that it would move the file to the right path
        file_data = self.request.POST['filename']
        if isFileUploaded(self,'filename'):
            staging_filepath = uploadBillImageToStaging(file_data)

        bills_service = get_service(self.session, 'bills')
        bill_date = parser.parse(self.request.get('bill_date'))
        tags = self.request.get('bill_tags', allow_multiple=True)
        tags_json = []
        for tag in tags:
            tags_json.append({'data': tag})
        tags_json = listToStringMessages(tags)

        body = {
            'accountId': account_id,
            'desc': self.request.get('bill_desc'),
            'currency_code': self.request.get('bill_currency_code'),
            'amount': self.request.get('bill_amount'),
            'date': self.request.get('bill_date'),
            'tags': tags_json
        }
        if isFileUploaded(self, 'filename'):
            body['staging_filepaths'] = [{'data': staging_filepath}]
        response = bills_service.createBill(body=body).execute()

        self.redirect('/account/' + account_id)


class EditBill(BaseHandler):
    @check_credentials
    def get(self, account_id, bill_id):
        profiles_service = get_service(self.session, 'profiles')
        profile = profiles_service.getProfile().execute()

        bills_service = get_service(self.session, 'bills')
        bill = bills_service.getBill(body={'accountId': account_id, 'billId':bill_id}).execute()

        template_values = {
            'profile': profile,
            'account_id': account_id,
            'bill': bill,
            'supported_currencies': settings.SUPPORTED_CURRENCIES
        }

        template = JINJA_ENVIRONMENT.get_template('edit_bill.html')
        self.response.out.write(template.render(template_values))

    @check_credentials
    def post(self, account_id, bill_id):
        bills_service = get_service(self.session, 'bills')
        bill = bills_service.updateBill(
                body={
                    'accountId': account_id,
                    'billId': bill_id,
                    'desc': self.request.get('bill_desc'),
                    'currency_code': self.request.get('bill_currency_code'),
                    'amount': self.request.get('bill_amount'),
                    'date': self.request.get('bill_date')
                    }
                ).execute()

        self.redirect('/account/' + account_id + '/' + bill_id + '/edit_bill')

class AddFileToBill(BaseHandler):
    @check_credentials
    def post(self, account_id, bill_id):
        bills_service = get_service(self.session, 'bills')

        if isFileUploaded(self, 'filename'):
            file_data = self.request.POST['filename']
            staging_filepath = uploadBillImageToStaging(file_data)
            body = {
                    'accountId': account_id,
                    'billId': bill_id,
                    'staging_filepaths': [{'data': staging_filepath}]
            }
            bills_service.addFileToBill(body=body).execute()

        self.redirect('/account/' + account_id + '/' + bill_id + '/edit_bill')

class RemoveFileFromBill(BaseHandler):
    @check_credentials
    def post(self, account_id, bill_id):
        file_to_delete = self.request.POST['file_to_delete']
        pprint.pprint(file_to_delete)

        bills_service = get_service(self.session, 'bills')

        if file_to_delete:
            body = {
                    'accountId': account_id,
                    'billId': bill_id,
                    'filepaths': [{'data': file_to_delete}]
            }
            bills_service.removeFileFromBill(body=body).execute()

        self.redirect('/account/' + account_id + '/' + bill_id + '/edit_bill')

class SearchBill(BaseHandler):
    @check_credentials
    def get(self, account_id):
        # Fetch Bills to display
        search_query = self.request.get('search_query')
        search_start_date = self.request.get('search_start_date')
        search_end_date = self.request.get('search_end_date')
        search_tags = self.request.get('search_tags', allow_multiple=True)
        search_bills_service = get_service(self.session, 'search_bills')

        search_request_body = {
                    'accountId': account_id,
                    'start_date': search_start_date,
                    'end_date': search_end_date,
                    'tags': listToStringMessages(search_tags),
                    'query': search_query
                }

        response_bills = search_bills_service.searchBills(body=search_request_body).execute()
        self.response.headers['Content-Type'] = "application/json"
        self.response.out.write(json.dumps(response_bills))
