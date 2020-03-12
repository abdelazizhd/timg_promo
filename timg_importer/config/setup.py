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
                    "name": "Importer Settings",
                    "description": _("TIMG Importer Settings"),
                    "hide_count": True
                },
                {
                    "type": "doctype",
                    "name": "Importer Item Settings",
                    "description": _("TIMG Importer Item Settings"),
                    "hide_count": True
                },
                {
                    "type": "doctype",
                    "name": "Importer Trigger Settings",
                    "description": _("TIMG Importer Trigger Settings"),
                    "hide_count": True
                },
                {
                    "type": "doctype",
                    "name": "Importer Categories Settings",
                    "description": _("TIMG Importer Categories Settings"),
                    "hide_count": True
                }
            ]
        }
    ]
