import gspread
import logging


gp = gspread.service_account(filename='services/hrfactor.json')

#Open Google spreadsheet
gsheet = gp.open('HRFactor')


# select worksheet
contact = gsheet.worksheet("Контактные данные")
friends = gsheet.worksheet("Рекомендации")


# добавить значения
def append_contact(list_contact: list, sheet: str):
    logging.info(f'append_contact')
    if sheet == 'contact':
        contact.append_row(list_contact)
    else:
        friends.append_row(list_contact)

