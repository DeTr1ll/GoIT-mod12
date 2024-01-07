from collections import UserDict
from datetime import datetime
import pickle

class Field:
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value


class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Name cannot be empty.")
        super().__init__(value)

    @property
    def name(self):
        return self._value

    @name.setter
    def name(self, new_name):
        if not new_name:
            raise ValueError("Name cannot be empty.")
        self._value = new_name

    def lower(self):
        return self._value.lower()


class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        self.validate()

    def validate(self):
        if not (self.value.isdigit() and len(self.value) == 10):
            raise ValueError("Phone number must contain 10 digits.")

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value
        self.validate()

    def __str__(self):
        return self._value


class Birthday(Field):
    def __init__(self, value=None):
        self._value = value
        self.validate()

    def validate(self):
        if self._value and not isinstance(self._value, datetime):
            raise ValueError("Birthday must be a valid datetime object.")

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value
        self.validate()


class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday)

    def add_phone(self, phone_value):
        phone = Phone(phone_value)
        self.phones.append(phone)

    def find_phone(self, phone_value):
        for phone in self.phones:
            if phone.value == phone_value:
                return phone
        return None

    def edit_phone(self, old_phone_value, new_phone_value):
        phone = self.find_phone(old_phone_value)
        if phone:
            phone.value = new_phone_value
        else:
            raise ValueError(f"Phone {old_phone_value} not found.")

    def remove_phone(self, phone_value):
        for phone in self.phones:
            if phone.value == phone_value:
                self.phones.remove(phone)
                return
        raise ValueError(f"Phone {phone_value} not found.")

    def days_to_birthday(self):
        if self.birthday.value:
            today = datetime.today()
            next_birthday = datetime(today.year, self.birthday.value.month, self.birthday.value.day)
            if today > next_birthday:
                next_birthday = datetime(today.year + 1, self.birthday.value.month, self.birthday.value.day)
            days_remaining = (next_birthday - today).days
            return days_remaining
        return None

    def __str__(self):
        phones_str = "; ".join([phone.value for phone in self.phones])
        return f"Contact name: {self.name.value}, phones: {phones_str}, birthday: {self.birthday.value}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def iterator(self, batch_size=5):
        records_list = list(self.data.values())
        for i in range(0, len(records_list), batch_size):
            yield records_list[i:i + batch_size]

    def display_page(self, page_number):
        try:
            page_number = int(page_number)
            if page_number < 1 or page_number > len(self.data):
                raise ValueError("Invalid page number.")
        except ValueError as e:
            print(f"Invalid input: {e}")
            return

        page_size = 5
        start_index = (page_number - 1) * page_size
        end_index = start_index + page_size
        selected_page = list(self.iterator(batch_size=page_size))[page_number - 1]

        print(f"Page {page_number}:")
        for record in selected_page:
            print(record)
            days_remaining = record.days_to_birthday()
            if days_remaining is not None:
                print(f"Days to birthday: {days_remaining}")
    def save_to_file(self, filename='address_book.pkl'):
        with open(filename, 'wb') as file:
            pickle.dump(self.data, file)

    def load_from_file(self, filename='address_book.pkl'):
        try:
            with open(filename, 'rb') as file:
                self.data = pickle.load(file)
        except FileNotFoundError:
            print("File not found. Creating a new address book.")

    def search(self, query):
        results = []
        for record in self.data.values():
            if query.lower() in record.name.lower() or any(query in phone.value for phone in record.phones):
                results.append(record)
        return results


book = AddressBook()
book.load_from_file()


while True:
    cmd_input = input("Enter cmd: ").lower()
    if cmd_input == "close":
        book.save_to_file()
        print("Bye!")
        break
    elif cmd_input == "page":
        page_number_input = input("Enter page: ")
        book.display_page(page_number_input)
    elif cmd_input == "search":
        search_query = input("Enter a name or phone number to search: ")
        search_results = book.search(search_query)
        if search_results:
            print("Search results:")
            for result in search_results:
                print(result)
        else:
            print("No matching results found.")
    else:
        print("Command didn't found.")