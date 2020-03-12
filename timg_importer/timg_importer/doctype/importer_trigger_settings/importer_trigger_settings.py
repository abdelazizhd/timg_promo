from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
import re


class ImporterTriggerSettings(Document):
    def validate(self):
        self.validate_url()

    def on_update(self):
        self.validate_url()

    def validate_url(self):
        if self.hook_url:
            regex = re.compile(
                r'^(?:http|ftp)s?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            if not re.match(regex, self.hook_url):
                frappe.throw(_("Invalid url"))
