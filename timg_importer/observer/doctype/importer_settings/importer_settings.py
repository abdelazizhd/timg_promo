# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
import os
import sys
import frappe
from frappe.utils.background_jobs import enqueue
from frappe.utils import cint, cstr
from frappe import throw
import json
import xlrd
from datetime import datetime
import urllib
import re

@frappe.whitelist()
def process_item(sku, price, price_list_name, iva):
    if iva:
        if float(iva) > 0:
            price = float(price) * (1 + abs(float(iva)))
        else:
            price = float(price) / (1 + abs(float(iva)))

    item_price_list = frappe.get_list('Item Price', filters={'item_code': sku, 'price_list': price_list_name}, fields=['name', 'item_code', 'price_list', 'price_list_rate'])

    # Crear asociacion con el price list

    if not item_price_list and price > 0:
        try:
            # create a new document
            item = frappe.get_doc({
                'doctype': 'Item Price',
                'item_code': sku,
                'price_list': price_list_name,
                'price_list_rate': round(price, 2)
            })
            item.insert()
            frappe.db.commit()
        except:
            e = "Error: %s" % sys.exc_info()[0]
            with open('/tmp/error_creating_pricelist_for_' + sku + '.txt', 'w') as outfile:
                outfile.write(e)
    elif price > 0:
        if item_price_list[0] and round(item_price_list[0].price_list_rate, 2) != round(price, 2):
            try:
                item_price = frappe.get_doc('Item Price', item_price_list[0].name)
                item_price.price_list_rate = round(price, 2)
                item_price.save()
            except:
                e = "Error: %s" % sys.exc_info()[0]
                with open('/tmp/error_saving_' + item_price_list[0].name + '.txt', 'w') as outfile:
                    outfile.write(e)
    # elif not item_price_list:
    #     with open('/tmp/no_list.txt', 'a') as outfile:
    #         outfile.write(sku + "\n")
    elif price <= 0:
        with open('/tmp/no_price.txt', 'a') as outfile:
            outfile.write(sku + "\n")


def create_item(item_settings, sheet, i):
    sku_column = item_settings.sku_column
    price_column = item_settings.price_column
    name_column = item_settings.name_column
    description_column = item_settings.description_column
    class_column = item_settings.class_column

    group = item_settings.group
    uom = item_settings.uom

    first_row = sheet.row_values(0)
    sku_idx = False
    price_idx = False
    name_idx = False
    description_idx = False
    class_idx = False

    for idx, column_name in enumerate(first_row):
        if str(column_name) == sku_column:
            sku_idx = idx
        elif str(column_name) == price_column:
            price_idx = idx
        elif str(column_name) == name_column:
            name_idx = idx
        elif str(column_name) == description_column:
            description_idx = idx
        elif class_column and str(column_name) == class_column:
            class_idx = idx

    if sku_idx and price_idx and name_idx and description_idx:
        sku = str(sheet.cell_value(i, sku_idx))
        price = sheet.cell_value(i, price_idx)
        name = str(sheet.cell_value(i, name_idx))
        description = str(sheet.cell_value(i, description_idx))
        iclass = False

        if class_idx:
            iclass = str(sheet.cell_value(i, class_idx))

        is_numeric = unicode(str(str(price).replace(".", "")), 'utf-8').isnumeric()

        if sku and is_numeric and price > 0 and name and uom and group:
            try:
                if sku.endswith('.0'):
                    sku = sku.replace(".0", "")

                dic = {}

                if iclass:
                    dic = {
                        'doctype': 'Item',
                        'item_name': name,
                        'item_code': sku,
                        'name': sku,
                        'description': description,
                        'brand': iclass,
                        'standard_rate': price,
                        'item_group': group,
                        'stock_uom': uom
                    }
                else:
                    dic = {
                        'doctype': 'Item',
                        'item_name': name,
                        'item_code': sku,
                        'name': sku,
                        'description': description,
                        'standard_rate': price,
                        'item_group': group,
                        'stock_uom': uom
                    }

                # create a new document
                item = frappe.get_doc(dic)
                item.insert()
                frappe.db.commit()
                line = "{}: Item {} created! \n".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), sku)
                with open('/tmp/importer_log.txt', 'a') as outfile:
                    outfile.write(str(line))
            except:
                e = "Error: %s" % sys.exc_info()[0]
                with open('/tmp/errorcreatingitem.txt', 'w') as outfile:
                    outfile.write(e)
        else:
            line = "{}: Invalid item values: sku({}) is_numeric({}) and price({}) name({}) \n".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), sku, is_numeric, price, name)
            with open('/tmp/importer_log.txt', 'a') as outfile:
                outfile.write(str(line))
    else:
        line = "{}: Invalid item values \n".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        with open('/tmp/importer_log.txt', 'a') as outfile:
            outfile.write(str(line))


def update_item_status(sku, enabled_str):
    line = "{}: Call update_item_status \n".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    with open('/tmp/importer_log.txt', 'a') as outfile:
        outfile.write(str(line))

    if frappe.db.exists('Item', sku):
        line = "{}: Exists in DB \n".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        with open('/tmp/importer_log.txt', 'a') as outfile:
            outfile.write(str(line))
        try:
            item = frappe.get_doc('Item', sku)

            disabled_strs = ['0', 'false', 'no']
            disabled = enabled_str.lower() in disabled_strs

            line = "{}: Disabled {} \n".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), disabled)
            with open('/tmp/importer_log.txt', 'a') as outfile:
                outfile.write(str(line))

            if item and item.disabled != disabled:
                item.disabled = disabled
                item.save()
        except:
            line = "{}: Error updating item status \n".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            with open('/tmp/importer_log.txt', 'a') as outfile:
                outfile.write(str(line))


def update_item_category(sku, category_id):
    line = "{}: Call update_item_category \n".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    with open('/tmp/importer_log.txt', 'a') as outfile:
        outfile.write(str(line))

    if frappe.db.exists('Item', sku):
        line = "{}: Exists in DB \n".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        with open('/tmp/importer_log.txt', 'a') as outfile:
            outfile.write(str(line))
        try:
            item = frappe.get_doc('Item', sku)

            if item and category_id:
                item.ecommerce_category = category_id
                item.save()
        except:
            line = "{}: Error updating item category \n".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            with open('/tmp/importer_log.txt', 'a') as outfile:
                outfile.write(str(line))


def process_categories(wb):
    with open('/tmp/categories_log.txt', 'w') as outfile:
        outfile.write(str("Starting import process ... \n"))
    categories_settings = frappe.get_single("Importer Categories Settings")
    categories_sheet_name = categories_settings.categories_sheet

    line = "Sheet name: {} \n".format(categories_sheet_name)
    with open('/tmp/categories_log.txt', 'a') as outfile:
        outfile.write(line)

    if categories_sheet_name:
        sheet = wb.sheet_by_name(categories_sheet_name)
        if sheet:
            data = []
            keys = []
            lvl = 0
            i = True

            for v in sheet.row(0):
                key = "l{}_{}".format(lvl, v.value)
                keys.append(key)
                i = not i
                if i:
                    lvl = lvl + 1

            for row_number in range(sheet.nrows):
                if row_number == 0:
                    continue
                row_data = {}
                for col_number, cell in enumerate(sheet.row(row_number)):
                    row_data[keys[col_number]] = str(cell.value).replace(".0", "")
                data.append(row_data)

            if data:
                categories_settings.categories_json = json.dumps({'data': data})
                categories_settings.save()
                with open('/tmp/categories_log.txt', 'a') as outfile:
                    outfile.write(json.dumps({'data': data}))
            else:
                line = "No data was imported: {} \n".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                with open('/tmp/categories_log.txt', 'a') as outfile:
                    outfile.write(line)
        else:
            line = "Sheet not found: {} \n".format(categories_sheet_name)
            with open('/tmp/categories_log.txt', 'a') as outfile:
                outfile.write(line)
    else:
        with open('/tmp/categories_log.txt', 'a') as outfile:
            outfile.write(str("No categorie sheet name"))
    line = "{}: Finish [OK] \n".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    with open('/tmp/categories_log.txt', 'a') as outfile:
        outfile.write(str(line))


def import_from_excel(doc, item_settings):
    url = doc.url
    sku_column = doc.sku_column
    price_column = doc.price_column
    enabled_column = doc.enabled_column
    category_column = doc.category_column
    price_list_name = doc.price_list_name
    iva = doc.iva
    skus_str = doc.skus
    sheets_str = doc.sheets
    skus = False
    sheets = False

    if skus_str:
        skus = skus_str.split(",")
        for i, v in enumerate(skus):
            skus[i] = v.strip()

    if sheets_str:
        sheets = sheets_str.split(",")
        for i, v in enumerate(sheets):
            sheets[i] = v.strip()

    full_path = '/tmp/downloaded_csv.xlsx'

    if os.path.exists(full_path):
        os.remove(full_path)

    urllib.urlretrieve(url, full_path)

    wb = xlrd.open_workbook(full_path)

    if wb:
        with open('/tmp/importer_log.txt', 'w') as outfile:
            outfile.write(str("Starting import process ... \n"))
        sheet_names = wb.sheet_names()
        for sheet_name in sheet_names:
            if (sheets and sheet_name in sheets) or not sheets:
                line = "{}: Starting sheet {} ... \n".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), sheet_name)
                with open('/tmp/importer_log.txt', 'a') as outfile:
                    outfile.write(str(line))
                sheet = wb.sheet_by_name(sheet_name)
                first_row = sheet.row_values(0)
                sku_idx = False
                price_idx = False
                enabled_idx = False
                category_idx = False

                for idx, column_name in enumerate(first_row):
                    if str(column_name) == sku_column:
                        sku_idx = idx
                    elif str(column_name) == price_column:
                        price_idx = idx
                    elif enabled_column and str(column_name) == enabled_column:
                        enabled_idx = idx
                    elif category_column and str(column_name) == category_column:
                        category_idx = idx

                if sku_idx and price_idx:
                    for i in range(sheet.nrows):
                        if i > 0:
                            sku = str(sheet.cell_value(i, sku_idx))
                            price = sheet.cell_value(i, price_idx)

                            if sku.endswith('.0'):
                                sku = sku.replace(".0", "")

                            is_numeric = unicode(str(str(price).replace(".", "")), 'utf-8').isnumeric()

                            if sku and is_numeric and price > 0:
                                if (skus and sku in skus) or not skus:
                                    if not frappe.db.exists('Item', sku):
                                        create_item(item_settings, sheet, i)
                                    process_item(sku, price, price_list_name, iva)
                                    if enabled_idx:
                                        enabled_str = str(sheet.cell_value(i, enabled_idx))
                                        update_item_status(sku, enabled_str)
                                    if category_idx:
                                        category_id = str(sheet.cell_value(i, category_idx))
                                        update_item_category(sku, category_id)
                line = "{}: End sheet {} ... \n".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), sheet_name)
                with open('/tmp/importer_log.txt', 'a') as outfile:
                    outfile.write(str(line))
        process_categories(wb)
        line = "{}: Finish [OK] \n".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        with open('/tmp/importer_log.txt', 'a') as outfile:
            outfile.write(str(line))


def process(doc, method):
    # importer = frappe.get_single("Importer Settings")
    item_settings = frappe.get_single("Importer Item Settings")
    if doc.process:
        url = doc.url

        if url:
            if url.endswith('pub?output=xlsx'):
                enqueue('timg_importer.observer.doctype.importer_settings.importer_settings.import_from_excel',
                        queue='default',
                        timeout=5400,
                        doc=doc,
                        item_settings=item_settings
                        )
                # import_from_excel(doc, item_settings)
                frappe.msgprint('Data processing is running in background.', 'Information')
            else:
                frappe.msgprint('Invalid CSV publication url (' + url + ').', 'Error')
        else:
            frappe.msgprint('CSV publication link must be specified.', 'Warning')


def import_all_from_excel(doc, item_settings):
    url = doc.url
    sku_column = doc.sku_column
    price_column = doc.price_column
    enabled_column = doc.enabled_column
    category_column = doc.category_column
    price_list_name = doc.price_list_name
    iva = doc.iva

    full_path = '/tmp/downloaded_csv.xlsx'

    if os.path.exists(full_path):
        os.remove(full_path)

    urllib.urlretrieve(url, full_path)

    wb = xlrd.open_workbook(full_path)

    if wb:
        with open('/tmp/importer_log.txt', 'w') as outfile:
            outfile.write(str("Starting import process ... \n"))
        sheet_names = wb.sheet_names()
        for sheet_name in sheet_names:
            line = "{}: Starting sheet {} ... \n".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), sheet_name)
            with open('/tmp/importer_log.txt', 'a') as outfile:
                outfile.write(str(line))
            sheet = wb.sheet_by_name(sheet_name)
            first_row = sheet.row_values(0)
            sku_idx = False
            price_idx = False
            enabled_idx = False
            category_idx = False

            for idx, column_name in enumerate(first_row):
                if str(column_name) == sku_column:
                    sku_idx = idx
                elif str(column_name) == price_column:
                    price_idx = idx
                elif enabled_column and str(column_name) == enabled_column:
                    enabled_idx = idx
                elif category_column and str(column_name) == category_column:
                    category_idx = idx

            if sku_idx and price_idx:
                for i in range(sheet.nrows):
                    if i > 0:
                        sku = str(sheet.cell_value(i, sku_idx))
                        price = sheet.cell_value(i, price_idx)

                        if sku.endswith('.0'):
                            sku = sku.replace(".0", "")

                        is_numeric = unicode(str(str(price).replace(".", "")), 'utf-8').isnumeric()

                        if sku and is_numeric and price > 0:
                            if not frappe.db.exists('Item', sku):
                                create_item(item_settings, sheet, i)
                            process_item(sku, price, price_list_name, iva)
                            if enabled_idx:
                                enabled_str = str(sheet.cell_value(i, enabled_idx))
                                update_item_status(sku, enabled_str)
                            if category_idx:
                                category_id = str(sheet.cell_value(i, category_idx))
                                update_item_category(sku, category_id)
            line = "{}: End sheet {} ... \n".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), sheet_name)
            with open('/tmp/importer_log.txt', 'a') as outfile:
                outfile.write(str(line))
        process_categories(wb)
        line = "{}: Finish [OK] \n".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        with open('/tmp/importer_log.txt', 'a') as outfile:
            outfile.write(str(line))


def check():
    full_path = '/tmp/last_csv_update.txt'

    date = False

    if os.path.exists(full_path):
        with open(full_path, 'r') as file:
            date = file.readline()

    if date:
        now = datetime.now()
        updated_date = datetime.strptime(date.strip(), '%d/%m/%Y %H:%M:%S')
        diff = (now - updated_date).total_seconds() / 60

        line = "[Diff]: {} \n".format(diff)
        with open('/tmp/scheduler_log.txt', 'w') as outfile:
            outfile.write(line)

        if diff >= 15:
            os.remove(full_path)

            doc = frappe.get_single("Importer Settings")
            item_settings = frappe.get_single("Importer Item Settings")
            trigger_settings = frappe.get_single("Importer Trigger Settings")

            if trigger_settings.hook_url:
                regex = re.compile(
                    r'^(?:http|ftp)s?://'  # http:// or https://
                    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
                    r'localhost|'  # localhost...
                    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                    r'(?::\d+)?'  # optional port
                    r'(?:/?|[/?]\S+)$', re.IGNORECASE)
                if re.match(regex, trigger_settings.hook_url):
                    req = urllib.request.Request(trigger_settings.hook_url)
                    try:
                        urllib.request.urlopen(req)
                        line = "{}: Called hook {} [OK] \n".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), trigger_settings.hook_url)
                        with open('/tmp/scheduler_log.txt', 'a') as outfile:
                            outfile.write(line)
                    except urllib.error.URLError as e:
                        with open('/tmp/scheduler_log.txt', 'a') as outfile:
                            outfile.write(e.reason)

            if doc.process:
                url = doc.url

                if url:
                    if url.endswith('pub?output=xlsx'):
                        enqueue('timg_importer.observer.doctype.importer_settings.importer_settings.import_all_from_excel',
                                queue='default',
                                timeout=5400,
                                doc=doc,
                                item_settings=item_settings
                                )
                        with open('/tmp/scheduler_log.txt', 'a') as outfile:
                            outfile.write('[QUEUED]: Done')
                    else:
                        with open('/tmp/scheduler_log.txt', 'a') as outfile:
                            outfile.write('Invalid CSV publication url (' + url + ').')
                else:
                    with open('/tmp/scheduler_log.txt', 'a') as outfile:
                        outfile.write('CSV publication link must be specified.')
            else:
                line = "[Error]: Doc disable process \n"
                with open('/tmp/scheduler_log.txt', 'a') as outfile:
                    outfile.write(line)
