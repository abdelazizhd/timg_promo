from __future__ import unicode_literals
from frappe import _


def get_data():
    return [
        {
            "label": _("Setup"),
            "icon": "icon-star",
            "items": [
                {
                    "type": "doctype",
                    "name": "Promo Settings",
                    "description": _("TIMG Promo Settings"),
                    "hide_count": True
                }
            ]
        }
    ]
