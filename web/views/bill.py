from view_imports import *

import os
from dateutil import parser
from utils import uploadBillImageToStaging

class CreateBill(BaseHandler):
    def _isFileUploaded(self):
        file_data = self.request.POST['filename']
        return True if file_data != u'' else False

    @check_credentials
    def post(self, account_id):
        # Put the file in GCS first and get the stage filepath
        # Send that info to the API so that it would move the file to the right path
        file_data = self.request.POST['filename']
        pprint.pprint(self._isFileUploaded())
        if self._isFileUploaded():
            staging_filepath = uploadBillImageToStaging(file_data)

        bills_service = get_service(self.session, 'bills')
        bill_date = parser.parse(self.request.get('bill_date'))
        tags = self.request.get('bill_tags', allow_multiple=True)
        tags_json = []
        for tag in tags:
            tags_json.append({'data': tag})

        body = {
            'accountId': account_id,
            'desc': self.request.get('bill_desc'),
            'amount': self.request.get('bill_amount'),
            'date': self.request.get('bill_date'),
            'tags': tags_json
        }
        if self._isFileUploaded():
            body['staging_filepaths'] = [{'data': staging_filepath}]
        pprint.pprint(body)
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
            'bill': bill
        }

        path = 'templates/edit_bill.html'
        self.response.out.write(template.render(path, template_values))

    @check_credentials
    def post(self, account_id, bill_id):
        bills_service = get_service(self.session, 'bills')
        bill = bills_service.updateBill(
                body={
                    'accountId': account_id,
                    'billId': bill_id,
                    'desc': self.request.get('bill_desc'),
                    'amount': self.request.get('bill_amount'),
                    'date': self.request.get('bill_date')
                    }
                ).execute()

        self.redirect('/account/' + account_id + '/' + bill_id + '/edit_bill')

