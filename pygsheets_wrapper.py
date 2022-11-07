import pygsheets as pygs


def get_sheet(sheet_id, sheet_name):
    google_client = pygs.authorize(client_secret='credentials.json')
    spreadsheet = google_client.open_by_key(sheet_id)
    return spreadsheet.worksheet_by_title(sheet_name)


def get_sheet_data(sheet_id, sheet_name):
    sheet = get_sheet(sheet_id, sheet_name)
    return sheet.get_as_df()


def copy_sheet(template_id, title, folder_id, set_values=None, sheet_name=None):
    google_client = pygs.authorize(client_secret='credentials.json')
    template = google_client.open_by_key(template_id)
    spreadsheet = google_client.create(title=title, template=template, folder=folder_id)
    # populate values if provided
    if set_values:
        if sheet_name:
            sheet = spreadsheet.worksheet_by_title(sheet_name)
        else:
            sheet = spreadsheet[0]
        update_sheet_values(set_values, sheet)
    # finally return copied sheet's id
    return spreadsheet.id


def update_sheet_values(set_values, sheet=None, sheet_id=None, sheet_name=None):
    ranges = list(set_values.keys())
    # pygsheet require the values to be a list of list, i.e., matrix
    values = [val if type(val) is list else [[val]] for val in set_values.values()]
    # edit sheet with set_values
    if not sheet:
        sheet = get_sheet(sheet_id, sheet_name)
    sheet.update_values_batch(ranges, values)
