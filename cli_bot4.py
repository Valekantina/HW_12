from collections import UserDict
from datetime import datetime, date
import time
import pickle


# creating a parent Field clas that will be passed onto Name, Phone and Record classes
# adding functions for self and string representations
class Field:
    def __init__(self, value: str) -> None:
        self.__value = None
        self.value = value

    def __str__(self) -> str:
        return f"{self.value}"

# creating Name class 
class Name(Field):

    # creating setter and value to check if the name is valid
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value: str):
        self.__value = value

# creating Phone class  
class Phone(Field):
# creating setter and value to check if the number is valid and corresponds to the known format
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if len(value) == 10 or len(value) ==9:
            self.__value = value
        else:
            raise ValueError

#creating new class - Birthday
class Birthday(Field):
    def __str__(self):
        if self.value is None:
            return "Unknown birthday"
        else:
            return f"{self.value:%d.%m.%Y}"

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value: str):
        if value is None:
            self.__value = None
        else:
            try:
                self.__value = datetime.strptime(
                    value, "%d.%m.%Y").date()
            except:
                print("Please provide date of birth in a format dd.mm.yyyy")

# creating Record class, where Name is a must, but phone number is optional
class Record:
    def __init__(self, name: Name, telephone=[], birthday: Birthday = None):
        self.name = name
        self.telephone_list = telephone
        self.birthday = birthday

# defining add_phone function within class, that will add a phone number to a phones dictionary
    def add(self, phone):
        self.telephone_list.append(phone)

# definind delete function within class, that will remove the number from phones dictionary
    def delete(self, phone):
        self.telephone_list.remove(phone)

# defining change_phone within class, that takes in old and new numbers and adds them to contact
    def edit(self, old_phone, new_phone):
        self.telephone_list[self.telephone_list.index(old_phone)] = new_phone


# defining the function that will count the days to birthday
    def days_to_bd(self, birthday: Birthday):
        if birthday.value is None:
            return "Birthday has not been set up. I cannot count days to birthday"
        bd = datetime.strptime(str(self.birthday), "%d.%m.%Y")
        today = date.today()
        day_end = date(year=today.year, month=bd.month, day=bd.day)
        if day_end < today:
            day_end = date(year=today.year + 1,
                           month=bd.month, day=bd.day)
        return (day_end - today).days

    def __repr__(self) -> str:
        return f"{self.name.value}: {self.telephone_list}, {self.birthday}"

data_file = "data.bin"

# creating AddressBook class that will take in information from UserDict
class AddressBook(UserDict):
    def add_record(self, rec: Record):
        self.data[rec.name.value] = rec
# adding an iterator to display only 30 records per page
    def iterator(self, num: int = 2):
        page = 1
        counter = 0
        result = "\n"
        for i in self.data:
            result += f"{self.data[i]}\n"
            counter += 1
            if counter >= num:
                yield result
                #defining how the pages will be displayed
                result = " " * 30 + "page " + str(page) + "\n"
                counter = 0
                page += 1
        yield result

# adding function 'save' within Address Book that will save the details to the file "data.bin"
    def save(self):
        with open(data_file, "wb") as df:
            pickle.dump(self.data, df)
# adding function 'load' within Address Book that will restore the data from the file "data.bin"
    def load(self):
        with open(data_file, "rb") as df:
            self.data = pickle.load(df)

# adding genral function load_user that will upload all contacts from the "data.bin" file    
def load_user(address_book, *args):
    address_book.load()
    return f"Your contacts have been loaded"

# creating error wrapper
def input_error(func):
    def wrapper(address_book, *args):
        try:
            return func(address_book, *args)
        except KeyError:
            return "This name does not exist in contacts"
        except IndexError:
            return "Sorry, you have not provided enough arguments."
        except ValueError:
            return "Please provide me with a name and a phone number or name, old number and new number. Please provide the phone in xxxxxxxxx format"
        except TypeError as err:
            return "Sorry, you have provided wrong type of arguments. Error: {err}"
    return wrapper


def hello(*args):
    return "How can I help you?"


def help(*args):
    return "I know these commands: hello, help, add, change, delete, phone, show all, days to bd, birthday, +bday, load, find, good bye, bye, close, exit"


# creating function to add new contacts   
@input_error
def add_new_contact(address_book, *args):
    name = Name(args[0])
    phone = Phone(args[1])
    if name.value in address_book:
        address_book[name.value].add(phone.value)
        return f"A new number has been added to contact {name.value}"
    else:
        if len(args) > 2:
            birthday = Birthday(args[2])
        else:
            birthday = Birthday(None)
        address_book[name.value] = Record(name, [phone.value], birthday)
    return "New contact has been added successfully"

# creating function to change existing contact
@input_error
def change(address_book, *args):
    old_phone, new_phone = args[1], args[2]
    rec = address_book[args[0]]
    rec.edit(old_phone, new_phone)
    return f"Contact was changed successfully"

# creating function to remove the phone number from the record
@input_error
def delete(address_book, *args):
    phone = args[1]
    rec = address_book[args[0]]
    rec.delete(phone)
    if len(rec.telephone_list) == 0:
        address_book.pop(args[0])
    return f"The phone number has been successfully removed!"

# creating function to view phone number of a chosen person from contacts list
@input_error
def phone_number(address_book, *args):
    name = args[0]
    phone = str(address_book[name].telephone_list)
    return f"{name}: {phone.replace('[', '').replace(']', '')}"

# creating function to view name of a chosen person from contacts list by phone number
@input_error
def search_name(address_book, *args):
    phone = args[0]
    for k, v in address_book.items():
        if phone in v.telephone_list:
            return f"This number {phone} is attached to the contact {k}"
        raise ValueError


# creating function to display all entries
@input_error
def show_all(address_book, *args):
    if len(address_book) == 0:
        raise IndexError
    else:
        users = ""
        for key in address_book.iterator():
            users += f"{key}\n"
        return users.replace("[", "").replace("]", "")

# adding function to count days to someones birthday
@input_error
def days_to_birthday(address_book, *args):
    name = args[0]
    if address_book[name].birthday.value is None:
        return "Unknown birthday"
    return f"{address_book[name]} has a birthday in {address_book[name].days_to_bd(address_book[name].birthday)} days"

# adding a function to add a birth date to the existing user
@input_error
def birthday(address_book, *args):
    name = args[0]
    address_book[name].birthday = Birthday(args[1])
    return f"The birthday has been successfully added to the {name}"

def find_info(address_book, *args):
    result= ""
    search = args[0].lower()
    for v in address_book.values():
        v_index = str(v).index(",")
        if search in str(v)[:v_index].lower():
            result += f"{str(v).replace(']','').replace('[','')}\n"
    return result

def command_not_found(*args):
    return "Command not found! Try help or another command!"


# In comparison to cli_bot3 we add "save" feature to the exit function
# this is to ensure, that all the input data is saved upon exiting
def exit(address_book, *args):
    address_book.save() # saving the updated address book
    print(f"Good bye!")
    time.sleep(1.5) # added delay on quit() so the message "Good bye!" is visible
    quit()

COMMANDS = {exit: ["exit", ".", "good bye", "close", "bye"], 
            add_new_contact: ["add"], 
            show_all: ["show all"], 
            change: ["change"],
            hello: ["hi", "hello", "hey"], 
            phone_number: ["phone"],
            search_name: ["name"],
            help: ["help"], 
            delete: ["delete", "remove"],
            days_to_birthday: ["bday", "days to bd"], 
            birthday: ["set bday", "+bday", "birthday"],
            load_user: ["load"], # added load 
            find_info: ["find"],

            }


def parse_command(user_input: str):
    for k, v in COMMANDS.items():
        for i in v:
            if user_input.lower().startswith(i.lower()):
                return k, user_input[len(i):].strip().split()
    else:
        return command_not_found

address_book = AddressBook()

def main():
    while True:
        user_input = input("Input command: ")
        result, data = parse_command(user_input)
        if result:
            print(result(address_book, *data))
        else:
            print (f"Sorry, I do not know this command, please try again. Or type'help' for help")


if __name__ == "__main__":
    main()