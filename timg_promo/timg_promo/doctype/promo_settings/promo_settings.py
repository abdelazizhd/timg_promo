from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class PromoSettings(Document):
    def validate(self):
        self.validate_credentials()

    def on_update(self):
        pass

    def validate_credentials(self):
        pass
        #  if not(self.api_endpoint_url and self.consumer_key and self.consumer_secret and self.private_key):
            #  frappe.msgprint(_('Please check your Xero API Credentials.'), raise_exception=1)