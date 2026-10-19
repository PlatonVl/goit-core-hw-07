
from collections import UserDict
from datetime import datetime, date, timedelta


class Field:
    def __init__(self, value):
        self.value = value


class Name(Field):
    def __init__(self, value):
        if not value or not value.strip():
            raise ValueError("Name cannot be empty.")
        super().__init__(value.strip())


class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except (ValueError, TypeError):
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        phone = Phone(phone)
        if self.find_phone(phone.value):
            raise ValueError("This phone number already exists.")
        self.phones.append(phone)

    def remove_phone(self, phone):
        existing_phone = self.find_phone(phone)
        if existing_phone is None:
            raise ValueError("Phone number not found.")
        self.phones.remove(existing_phone)

    def edit_phone(self, old_phone, new_phone):
        existing_phone = self.find_phone(old_phone)
        if existing_phone is None:
            raise ValueError("Old phone number not found.")

        if old_phone != new_phone and self.find_phone(new_phone):
            raise ValueError("This phone number already exists.")

        new_phone = Phone(new_phone)
        existing_phone.value = new_phone.value

    def find_phone(self, phone):
        for item in self.phones:
            if item.value == phone:
                return item
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = ", ".join(phone.value for phone in self.phones)
        birthday = (
            self.birthday.value if self.birthday else "not specified"
        )
        return (
            f"Contact name: {self.name.value}, "
            f"phones: {phones or 'none'}, "
            f"birthday: {birthday}"
        )


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name not in self.data:
            raise KeyError(name)
        del self.data[name]

    def get_upcoming_birthdays(self):
        today = date.today()
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday is None:
                continue

            birthday_date = datetime.strptime(
                record.birthday.value, "%d.%m.%Y"
            ).date()

            try:
                next_birthday = birthday_date.replace(year=today.year)
            except ValueError:
                # For February 29 in a non-leap year.
                next_birthday = date(today.year, 2, 28)

            if next_birthday < today:
                try:
                    next_birthday = birthday_date.replace(
                        year=today.year + 1
                    )
                except ValueError:
                    next_birthday = date(today.year + 1, 2, 28)

            if today <= next_birthday <= today + timedelta(days=6):
                congratulation_date = next_birthday

                if congratulation_date.weekday() == 5:
                    congratulation_date += timedelta(days=2)
                elif congratulation_date.weekday() == 6:
                    congratulation_date += timedelta(days=1)

                upcoming_birthdays.append({
                    "name": record.name.value,
                    "birthday": congratulation_date.strftime("%d.%m.%Y")
                })

        return sorted(
            upcoming_birthdays,
            key=lambda item: datetime.strptime(
                item["birthday"], "%d.%m.%Y"
            )
        )


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as error:
            return str(error)
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Please provide all required arguments."
        except TypeError:
            return "Invalid arguments."
    return inner


def parse_input(user_input):
    parts = user_input.strip().split()
    if not parts:
        return "", []
    command, *args = parts
    return command.lower(), args


@input_error
def add_contact(args, book: AddressBook):
    name, phone = args
    record = book.find(name)

    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    else:
        message = "Contact updated."

    record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)

    if record is None:
        raise KeyError(name)

    record.edit_phone(old_phone, new_phone)
    return "Phone number updated."


@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)

    if record is None:
        raise KeyError(name)

    if not record.phones:
        return f"No phone numbers for {name}."

    return f"{name}: {', '.join(p.value for p in record.phones)}"


@input_error
def show_all(book: AddressBook):
    if not book:
        return "The address book is empty."

    return "\n".join(str(record) for record in book.values())


@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.find(name)

    if record is None:
        raise KeyError(name)

    record.add_birthday(birthday)
    return f"Birthday added for {name}."


@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)

    if record is None:
        raise KeyError(name)

    if record.birthday is None:
        return f"Birthday for {name} is not specified."

    return f"{name}'s birthday: {record.birthday.value}"


@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()

    if not upcoming:
        return "No birthdays in the next 7 days."

    lines = ["Upcoming birthdays:"]
    for item in upcoming:
        lines.append(
            f"{item['name']}: {item['birthday']}"
        )

    return "\n".join(lines)


def hello():
    return "How can I help you?"


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ("close", "exit"):
            print("Good bye!")
            break

        elif command == "hello":
            print(hello())

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        elif not command:
            continue

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
