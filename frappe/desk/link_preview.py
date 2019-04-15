import frappe
from frappe.model import no_value_fields
import json

@frappe.whitelist()
def get_preview_data(doctype, docname, fields):
	fields = json.loads(fields)
	preview_fields = [field['name'] for field in fields if field['type'] not in no_value_fields]
	if 'title' not in fields and frappe.get_meta(doctype).has_field('title'):
		preview_fields.append('title')
	if 'name' not in fields:
		preview_fields.append('name')
	if frappe.get_meta(doctype).has_field('image'):
		preview_fields.append('image')

	preview_data = frappe.cache().hget('preview_data', (doctype, docname))
	if preview_data == None:
		preview_data = frappe.get_all(doctype, filters={
			'name': docname
		}, fields=preview_fields, limit=1)
		if preview_data:
			preview_data = preview_data[0]

			preview_data = {k: v for k, v in preview_data.items() if v is not None}
			for k,v in preview_data.items():
				if frappe.get_meta(doctype).has_field(k):
					preview_data[k] = frappe.format(v,frappe.get_meta(doctype).get_field(k).fieldtype)

		frappe.cache().hset('preview_data', (doctype, docname), preview_data)
	if not preview_data:
		return None
	return preview_data

def clear_preview_cache(doc, method):
	frappe.cache().delete_value('preview_data', (doc.get('doctype', doc.get('name'))))
