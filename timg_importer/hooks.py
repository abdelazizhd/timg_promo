# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "timg_importer"
app_title = "Timg Importer"
app_publisher = "Abdelaziz de la Horra Diaz"
app_description = "Import data from CSV file"
app_icon = "octicon octicon-cloud-upload"
app_color = "grey"
app_email = "abdelazizhd@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/timg_importer/css/timg_importer.css"
# app_include_js = "/assets/timg_importer/js/timg_importer.js"

# include js, css files in header of web template
# web_include_css = "/assets/timg_importer/css/timg_importer.css"
# web_include_js = "/assets/timg_importer/js/timg_importer.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "timg_importer.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "timg_importer.install.before_install"
# after_install = "timg_importer.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "timg_importer.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Importer Settings": {
        "on_update": "timg_importer.observer.doctype.importer_settings.importer_settings.process"
    }
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
}

# Scheduled Tasks
# ---------------

scheduler_events = {
    "cron": {
        "*/15 * * * *": [
            "timg_importer.observer.doctype.importer_settings.importer_settings.check"
        ]
    }
# 	"all": [
# 		"timg_importer.tasks.all"
# 	],
# 	"daily": [
# 		"timg_importer.tasks.daily"
# 	],
# 	"hourly": [
# 		"timg_importer.tasks.hourly"
# 	],
# 	"weekly": [
# 		"timg_importer.tasks.weekly"
# 	]
# 	"monthly": [
# 		"timg_importer.tasks.monthly"
# 	]
}

# Testing
# -------

# before_tests = "timg_importer.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "timg_importer.event.get_events"
# }

