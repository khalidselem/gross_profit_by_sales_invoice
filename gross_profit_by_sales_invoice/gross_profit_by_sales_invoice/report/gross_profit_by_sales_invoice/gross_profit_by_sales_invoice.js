// Copyright (c) 2022, Peter Maged and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Gross Profit By Sales Invoice"] = {
  // Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
  // License: GNU General Public License v3. See license.txt

  filters: [
    {
      fieldname: "company",
      label: __("Company"),
      fieldtype: "Link",
      options: "Company",
      reqd: 1,
      default: frappe.defaults.get_user_default("Company"),
    },
    {
      fieldname: "from_date",
      label: __("From Date"),
      fieldtype: "Date",
      default: frappe.defaults.get_user_default("year_start_date"),
    },
    {
      fieldname: "to_date",
      label: __("To Date"),
      fieldtype: "Date",
      default: frappe.defaults.get_user_default("year_end_date"),
    },
    {
      fieldname: "sales_invoice",
      label: __("Sales Invoice"),
      fieldtype: "Link",
      options: "Sales Invoice",
    },
    {
      fieldname: "group_by",
      label: __("Group By"),
      fieldtype: "Select",
      options: "Invoice\nItem Code\nItem Group\nBrand\nWarehouse\nSales Person",
      default: "Invoice",
    },
  ],
  tree: true,
  name_field: "parent",
  parent_field: "parent_invoice",
  initial_depth: 3,
  formatter: function (value, row, column, data, default_formatter) {
    if (
      column.fieldname == "sales_invoice" &&
      column.options == "Item" &&
      data.indent == 0
    ) {
      column._options = "Sales Invoice";
    } else {
      column._options = "Item";
    }
    value = default_formatter(value, row, column, data);

    if (data && (data.indent == 0.0 || row[1].content == "Total")) {
      value = $(`<span>${value}</span>`);
      var $value = $(value).css("font-weight", "bold");
      value = $value.wrap("<p></p>").parent().html();
    }

    return value;
  },
};
