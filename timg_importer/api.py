from __future__ import unicode_literals
from datetime import datetime
import frappe
import time


@frappe.whitelist(allow_guest=True)
def notify():
    with open('/tmp/last_csv_update.txt', 'w') as outfile:
        outfile.write(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
