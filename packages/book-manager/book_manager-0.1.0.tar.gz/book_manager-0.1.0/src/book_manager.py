"""Book manager application."""

import sqlite3
import time

import inquirer

from src.assignment22.task1.src.database_utils import (
    create_database,
    delete_book,
    get_data,
    insert_data,
    mark_read,
)


def main() -> None:
    """Manages main loop."""
    print("\nWelcome to book manager\n")
    create_database()
    while True:
        mode = prompt_modes()
        if mode == "Quit":
            break
        else:
            modes[mode]()


def _add_book() -> None:
    """Insert book to database."""
    name = input("Enter name of the book: ")
    author = input("Enter author of the book: ")
    try:
        insert_data(name, author)
        print(f"\n{name} has been added.\n")
    except sqlite3.IntegrityError:
        print("\nBook already exists.\n")


def _remove_book() -> None:
    """Delete book from database."""
    name = input("Enter name of the book: ")
    status = delete_book(name)
    if status == 0:
        print("\nNo book found.\n")
    else:
        print(f"\n{name} has been deleted.\n")


def _display_books() -> None:
    """Get books from database."""
    books = get_data()
    if not books:
        print("No books to show.\n")
    for book in books:
        if book["read"]:
            read = "READ"
        else:
            read = "NOT READ"
        print(f"{book['name']} by {book['author']} - {read}\n")


def _read_book() -> None:
    """Mark a book read."""
    name = input("Enter name of the book: ")
    status = mark_read(name)
    if status == 0:
        print("\nNo book found.\n")
    else:
        print(f"\n{name} has been marked as read.\n")


def prompt_modes() -> str:
    """Get mode from the user."""
    questions = [
        inquirer.List(
            "choice",
            message="What do you want to do?",
            choices=list(modes.keys()) + ["Quit"],
        )
    ]
    if callable(inquirer.prompt):
        answer = inquirer.prompt(questions)
        if isinstance(answer, dict):
            return answer["choice"]
        else:
            return "Quit"
    else:
        raise RuntimeError


modes = {
    "Insert Book": _add_book,
    "Delete Book": _remove_book,
    "List Books": _display_books,
    "Mark a book read": _read_book,
}


if __name__ == "__main__":
    try:
        main()
        print("Closing the application!!")
    except KeyboardInterrupt:
        pass
    except (Exception, BaseException) as error:
        print(f"{error.__class__.__name__}: {error}")
    time.sleep(0.5)
