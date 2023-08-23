import csv
import re
from typing import List, Dict

from faker import Faker


def formatting_phone(number: str):
    pattern = r'^\+7|8?\s?-?\(?(?P<code>\d{3})\)?\s?-?(?P<gr1>\d{3})\s?-?(?P<gr2>\d{2})\s?-?(?P<gr3>\d{2})\s?$'
    return re.sub(pattern, r'8\g<code>\g<gr1>\g<gr2>\g<gr3>', number)


def prepare_sample_data(limit: int) -> List[Dict[str, str]]:
    data = []
    fake = Faker(['ru_RU'])
    while limit:
        try:
            first_name, last_name, patronymic = fake.name().split(' ')
            contact = {
                'last_name': last_name,
                'first_name': first_name,
                'patronymic': patronymic,
                'company': fake.company(),
                'work_phone': formatting_phone(fake.phone_number()),
                'personal_phone': formatting_phone(fake.phone_number())
            }
            data.append(contact)
        except ValueError:
            continue
        limit -= 1
    return data


def write_sample_data(limit: int = 100) -> None:
    with open('sample_data.csv', 'w', newline='') as csvfile:
        fieldnames = ['last_name', 'first_name', 'patronymic', 'company', 'work_phone', 'personal_phone']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        sample_data = prepare_sample_data(limit)
        [writer.writerow(contact) for contact in sample_data]


if __name__ == '__main__':
    write_sample_data()
