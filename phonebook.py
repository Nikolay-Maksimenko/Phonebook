import csv
import math
import re
from dataclasses import dataclass
from typing import Dict, List, Any, Union, Optional
from copy import deepcopy


PAGE_SIZE = 10
DATA_PATH = 'sample_data.csv'
PATTERN = r'^\+7|8?\s?-?\(?(?P<code>\d{3})\)?\s?-?(?P<gr1>\d{3})\s?-?(?P<gr2>\d{2})\s?-?(?P<gr3>\d{2})\s?$'


@dataclass
class Contact:
    last_name: str
    first_name: str
    patronymic: str
    company: str
    work_phone: str
    personal_phone: str

    def __str__(self):
        return ' '.join(self.to_dict.values())

    @property
    def to_dict(self) -> Dict:
        """
        Сreates a dictionary from class attributes.
        """
        return {
            'last_name': self.last_name.strip().title(),
            'first_name': self.first_name.strip().title(),
            'patronymic': self.patronymic.strip().title(),
            'company': self.company.strip().title(),
            'work_phone': self.work_phone,
            'personal_phone': self.personal_phone
        }


class Pagination:
    def __init__(self, data: List[Any], page_size: int = PAGE_SIZE):
        self.data = data
        self.total_count = len(data)
        self.page_size = page_size
        self.pages_count = math.ceil(self.total_count / self.page_size)

    def paginated_data(self, cur_page: int = 1) -> Dict[str, Union[str, int]]:
        """
        Selects data for a given page.
        """
        if cur_page > self.pages_count:
            print('There is no page with this number')
            cur_page = self.pages_count
        end_pos = cur_page * self.page_size
        start_pos = end_pos - self.page_size
        items = self.data[start_pos: end_pos]
        return {
            'items': items,
            'page': cur_page,
            'pages_count': self.pages_count,
            'total_count': len(self.data),
        }


class Phonebook:

    def __init__(self, path=DATA_PATH):
        self.path = path
        self._init_data(path=self.path)

    def _init_data(self, path: str):
        with open(path, 'r') as f:
            reader = csv.DictReader(f.readlines())
            data = [Contact(**row) for row in reader]
            self.data = data

    def write(self, contacts, mode: str):
        """
        Writes contact data to a csv file.
        """
        if not isinstance(contacts, list):
            contacts = [contacts]
        with open(self.path, mode) as f:
            writer = csv.DictWriter(f, fieldnames=Contact.__annotations__.keys())
            if mode == 'w':
                writer.writeheader()
            [writer.writerow(contact.to_dict) for contact in contacts]

    @staticmethod
    def _get_paginated_data(data: List[Contact], page: int = 1):
        pagination = Pagination(data=data)
        return pagination.paginated_data(page)

    def _get_paginated_response(self, data, page):
        data = self._get_paginated_data(data=data, page=page)
        items = data['items']
        print(
            f'Contacts total: {data["total_count"]}, '
            f'Page {data["page"]}/{data["pages_count"]}\n'
        )
        print(*items, sep='\n')

    @staticmethod
    def _validate_phone(phone_number: str):
        search_result = re.search(PATTERN, phone_number)
        if search_result is None:
            print('Incorrect phone number')
        if search_result is not None:
            phone = re.sub(PATTERN, r'8\g<code>\g<gr1>\g<gr2>\g<gr3>', phone_number)
            return phone

    def _unique_contact_validate(self, contact: List):
        data = self.data
        if contact not in data:
            return True

    @staticmethod
    def _request_contact_params() -> Dict:
        while True:
            command = input(
                'Input a contact params string or "q" for exit command\n'
                'Params string must be key/value pairs divided by space like this: first_name=John last_name=Doe\n'
                f'Available fields: {Contact.__annotations__}\n'
            )

            if command == 'q':
                break

            try:
                pairs = command.split(' ')
                search_params = {}
                for pair in pairs:
                    key, value = pair.split('=')
                    search_params[key] = value
                if 'work_phone' in list(search_params.keys()):
                    search_params['work_phone'] = Phonebook._validate_phone(search_params['work_phone'])
                    if search_params['work_phone'] is None:
                        continue
                if 'personal_phone' in list(search_params.keys()):
                    search_params['personal_phone'] = Phonebook._validate_phone(search_params['personal_phone'])
                    if search_params['personal_phone'] is None:
                        continue

            except Exception:
                print('Invalid params string')
                continue
            return search_params

    def _search_contacts(self) -> Optional[List[Contact]]:
        search_params = self._request_contact_params()
        if not search_params:
            return

        data = []
        for contact in self.data:
            if list(search_params.values()) == [getattr(contact, field_name) for field_name in search_params.keys()]:
                data.append(contact)
        return data

    def _list(self, data):
        self._get_paginated_response(data=data, page=1)
        while True:
            command = input('For page navigation input page number or "q" for exit command ')
            if command == 'q':
                break

            try:
                command = int(command)
            except ValueError:
                print('Input integer or "q" for exit command')
                continue

            if command < 1:
                print('Page number must be a positive integer')
                continue

            self._get_paginated_response(data=data, page=command)

    def list_command(self):
        """
        Shows contact data with paginated navigation.
        """
        self._list(data=self.data)

    def search_command(self):
        """
        Searches for contacts by the given parameters.
        """
        searched_data = self._search_contacts()
        if not searched_data:
            return
        self._list(data=searched_data)

    def add_command(self):
        """
        Creates a new contact in the phonebook.
        """
        params = self._request_contact_params()
        if not params:
            return

        required_params = Contact.__annotations__.keys()
        while params and (params.keys() != required_params):
            print(
                f'You have to fill all required parameters to continue\n'
                f'{required_params=}\n'
                f'Enter "q" for exit command'
            )
            params = self._request_contact_params()

        new_contact = Contact(**params)
        if self._unique_contact_validate(new_contact):
            self.data.append(new_contact)
            self.write(contacts=new_contact, mode='a')
            print(f'New contact was created\n{new_contact}')
            return new_contact
        else:
            print('Such a contact already exists')
            return

    def edit_command(self):
        """
        Modifies an existing contact based on user input.
        """
        contact_to_edit = deepcopy(self._search_contacts())
        print(contact_to_edit)
        while contact_to_edit and len(contact_to_edit) > 1:
            print('Input more specific contact data')
            contact_to_edit = deepcopy(self._search_contacts())
        if contact_to_edit:
            contact_idx = self.data.index(contact_to_edit[0])
            print('Input parameters to update')
            params_to_update = self._request_contact_params()
            if params_to_update:
                for field_name, value in params_to_update.items():
                    setattr(contact_to_edit[0], field_name, value)

                if not self._unique_contact_validate(contact_to_edit[0]):
                    print('Such a contact already exists')
                    return
                self.data[contact_idx] = contact_to_edit[0]
                self.write(self.data, 'w')
                print(f'Contact updated\n{self.data[contact_idx]}')

    def run(self):
        """"""
        commands = {
            'l': self.list_command,
            's': self.search_command,
            'a': self.add_command,
            'e': self.edit_command,
        }
        while True:
            command = input('Input command: ')
            if command == 'q':
                break
            if method := commands.get(command):
                method()
