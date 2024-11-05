# Copyright (c) 2022, Peter MAged and contributors
# For license information, please see license.txt

from dataclasses import field
from tokenize import group
from unittest import result
import frappe
from frappe import _, scrub

group_wise_columns = frappe._dict({
    "invoice": ["invoice_or_item", "customer", "status", "warehouse", "item_code", "item_name", "item_group", "brand",
                "qty", "base_rate", "base_amount", "buying_rate", "buying_amount", "gross_profit", "gross_profit_percent"],


    "item_code": ["item_code", "item_name", "item_group", "brand",
                  "qty", "base_rate", "base_amount", "buying_rate", "buying_amount", "gross_profit", "gross_profit_percent"],


    "item_group": ["item_group",
                   "qty", "base_rate", "base_amount", "buying_rate", "buying_amount", "gross_profit", "gross_profit_percent"],



    "warehouse": ["warehouse",
                  "qty", "base_rate", "base_amount", "buying_rate", "buying_amount", "gross_profit", "gross_profit_percent"],

    "brand": ["brand",
              "qty", "base_rate", "base_amount", "buying_rate", "buying_amount", "gross_profit", "gross_profit_percent"],

    "sales_person": ["sales_person",
                     "qty", "base_rate", "base_amount", "buying_rate", "buying_amount", "gross_profit", "gross_profit_percent"],

})


group_map_field = {
    "invoice": "item.name",
    "item_code": "item.item_code",
    "item_group": "item.item_group",
    "warehouse": "item.warehouse",
    "brand": "item.brand",
    "sales_person": "team.sales_person",
}


def execute(filters=None):
    columns, data = [], []
    filters = frappe._dict(filters or {})
    columns = get_columns(filters)
    data = get_data(filters)
    # data = []

    # if filters.group_by == 'Invoice':
    #     get_data_when_grouped_by_invoice(columns, result, filters, group_wise_columns, data)

    # else:
    #     get_data_when_not_grouped_by_invoice(result, filters, group_wise_columns, data)
    return columns, data


def get_columns(filters):
    columns = []
    columns_map = {
        "parent": {
            "fieldname": "parent",
            "label": _("Sales Invoice"),
            "fieldtype": "Link",
            "options": "Sales Invoice",
            "width": 120
        },
        "invoice_or_item": {
            "fieldname": "invoice_or_item",
            "label": _("Sales Invoice"),
            "fieldtype": "Link",
            "options": "Item",
            "width": 120
        },
        "posting_time": {
            "fieldname": "posting_time",
            "label": _("Posting Time"),
            "fieldtype": "Data",
            "width": 120
        },
        "status": {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 120
        },
        "posting_date": {
            "fieldname": "posting_date",
            "label": _("Date"),
            "fieldtype": "Date",
            "width": 120
        },
        "item_code": {
            "fieldname": "item_code",
            "label": _("Item"),
            "fieldtype": "Link",
            "options": "Item",
            "width": 120
        },
        "item_name": {
            "fieldname": "item_name",
            "label": _("Item Name"),
            "fieldtype": "Data",
            "width": 120
        },
        "item_group": {
            "fieldname": "item_group",
            "label": _("Item Group"),
            "fieldtype": "Link",
            "options": "Item Group",
            "width": 120
        },
        "customer": {
            "fieldname": "customer",
            "label": _("Customer"),
            "fieldtype": "Link",
            "options": "Customer",
            "width": 120
        },
        "brand": {
            "fieldname": "brand",
            "label": _("Brand"),
            "fieldtype": "Link",
            "options": "Brand",
            "width": 120
        },
        "description": {
            "fieldname": "description",
            "label": _("Description"),
            "fieldtype": "Data",
            "width": 120
        },
        "warehouse": {
            "fieldname": "warehouse",
            "label": _("Warehouse"),
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 120
        },
        "qty": {
            "fieldname": "qty",
            "label": _("Qty"),
            "fieldtype": "Float",
            "precision": 3,
            "width": 120
        },
        "base_rate": {
            "fieldname": "base_rate",
            "label": _("Rate (Selling)"),
            "fieldtype": "Currency",
            "width": 120
        },
        "base_amount": {
            "fieldname": "base_amount",
            "label": _("Amount (Selling)"),
            "fieldtype": "Currency",
            "width": 120
        },
        "buying_rate": {
            "fieldname": "buying_rate",
            "label": _("Incoming Rate (Costing)"),
            "fieldtype": "Currency",
            "width": 120
        },
        "buying_amount": {
            "fieldname": "buying_amount",
            "label": _("Amount (Costing)"),
            "fieldtype": "Currency",
            "width": 120
        },
        "gross_profit": {
            "fieldname": "gross_profit",
            "label": _("Gross Profit"),
            "fieldtype": "Currency",
            "width": 120
        },
        "gross_profit_percent": {
            "fieldname": "gross_profit_percent",
            "label": _("Gross Profit %"),
            "fieldtype": "Percent",
            "width": 120
        },
        "sales_person": {
            "fieldname": "sales_person",
            "label": _("Sales Person"),
            "fieldtype": "Data",
            "width": 120
        },
    }
    for col in group_wise_columns.get(scrub(filters.group_by)):
        columns.append(columns_map.get(col))
    # columns.append({
    #     "fieldname": "currency",
    #     "label": _("Currency"),
    #     "fieldtype": "Link",
    #     "options": "Currency",
    #     "hidden": 1
    # })
    return columns


def get_data(filters):
    conditions = get_conditions(filters or {})
    inner_group_by = group_map_field.get(scrub(filters.group_by))
    is_sales = (scrub(filters.group_by) == "sales_person")
    sales_inner = " inner join `tabSales Team` team on team.parent = invoice.name " if is_sales else ""
    sales_field = " team.sales_person , " if is_sales else ""
    sql = f"""
    select item.* ,
        (item.base_amount - buying_amount ) as gross_profit,
        ((item.base_amount - buying_amount)  / item.base_amount) * 100  as gross_profit_percent
    from (

                select 
                    {sales_field}
                    invoice.name as invoice_or_item ,
                    invoice.parent,
                    invoice.customer,
                    invoice.status,
                    invoice.posting_date  ,
                    invoice.posting_time  ,
                    item.item_code ,
                    item.item_name ,
                    item.item_group ,
                    item.brand ,
                    item.description ,
                    item.warehouse ,
                    item_row.is_stock_item ,
                    SUM(item.qty) as qty ,
                    AVG(item.base_rate) as base_rate,
                    SUM(item.base_amount) as base_amount,
                    SUM(CASE when item_row.is_stock_item THEN (item.incoming_rate * item.qty) ELSE 0 END) as buying_amount,
                    AVG(CASE when item_row.is_stock_item THEN item.incoming_rate ELSE 0 END) as buying_rate 
                from `tabSales Invoice` invoice 
                inner join `tabSales Invoice Item` item on item.parent = invoice.name 
                inner join `tabItem` item_row on item.item_code = item_row.name 
                {sales_inner}
                where invoice.docstatus = 1
                    {conditions}
                Group By {inner_group_by}

    ) item


	"""
    # frappe.throw(sql)
    result = frappe.db.sql(sql, as_dict=1)
    data = result
    return data


def get_data_when_grouped_by_invoice(columns, gross_profit_data, filters, group_wise_columns, data):
	# column_names = get_column_names()

	# to display item as Item Code: Item Name
	# columns[0] = {
    #         "fieldname": "invoice_or_item",
    #         "label": _("Sales Invoice"),
    #         "fieldtype": "Link",
    #         "options": "Item",
    #         "width": 120
    #     }
	# removing Item Code and Item Name columns
	# del columns[4:6]

	for src in gross_profit_data:
		row = frappe._dict()
		row.indent = src.indent
		row.parent_invoice = src.parent_invoice
		row.currency = filters.currency

		for col in group_wise_columns.get(scrub(filters.group_by)):
			row[col] = src.get(col)

		data.append(row)

def get_data_when_not_grouped_by_invoice(gross_profit_data, filters, group_wise_columns, data):
	for idx, src in enumerate(gross_profit_data.grouped_data):
		row = []
		for col in group_wise_columns.get(scrub(filters.group_by)):
			row.append(src.get(col))

		row.append(filters.currency)
		if idx == len(gross_profit_data.grouped_data)-1:
			row[0] = "Total"

		data.append(row)


def get_conditions(filters):
    from_date, to_date = filters.get('from_date'), filters.get('to_date')

    conditions = ""
    data = filters.get("company")
    if data:
        conditions += f" and invoice.company = '{data}' "

    data = filters.get("sales_invoice")
    if data:
        conditions += f" and invoice.name = '{data}' "

    data = filters.get("from_date")
    if data:
        conditions += f" and invoice.posting_date >= date('{data}') "

    data = filters.get("to_date")
    if data:
        conditions += f" and invoice.posting_date <= date('{data}') "

    return conditions
