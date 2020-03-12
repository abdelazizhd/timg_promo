from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
import re


class ImporterCategoriesSettings(Document):
    def validate(self):
        pass

    def on_update(self):
        pass

