from datetime import datetime
import random
from typing import List, Dict

import pytz

from connection_pool import get_connection
from database import database
from models.option import Option
from models.poll import Poll
from utils import from_list_to_dict_option


MENU_PROMPT = """-- Menu --

1) Create new poll
2) List open polls
3) Vote on a poll
4) Show poll votes
5) Select a random winner from a poll option
6) Exit

Enter your choice: """
NEW_OPTION_PROMPT = "Enter new option text (or leave empty to stop adding options): "


def prompt_create_poll():
    title = input("Enter poll title: ")
    owner = input("Enter poll owner: ")
    poll = Poll(title, owner)
    poll.save()

    while (new_option := input(NEW_OPTION_PROMPT)):
        poll.add_option(new_option)


def list_open_polls():
    for poll in Poll.all():
        print(f"{poll.id}: {poll.title} (created by {poll.owner})")


def prompt_vote_poll():
    poll_id = int(input("Enter poll would you like to vote on: "))
    poll = Poll.get(poll_id)
    if poll:
        options = from_list_to_dict_option(poll.options)
        _print_poll_options(options)

        option_num = input("Enter option you'd like to vote for: ")
        option_id = options.get(option_num).id
        username = input("Enter the username you'd like to vote as: ")

        Option.get(option_id).vote(username)
    else:
        print("Haven't polls yet.")


def _print_poll_options(options: Dict[str, Option]):
    for key, option in options.items():
        print(f"{key}: {option.text}")


def _print_votes_for_options(options: List[Option]):
    for option in options:
        print(f"-- {option.text} --")
        for vote in option.votes:
            naive_datetime = datetime.utcfromtimestamp(vote[2])
            utc_date = pytz.utc.localize(naive_datetime)
            local_date = utc_date.astimezone(pytz.timezone("Europe/Moscow")).strftime("%Y-%m-%d %H:%M")
            print(f"\t- {vote[0]} on {local_date}")


def show_poll_votes():
    poll_id = int(input("Enter poll you would like to see votes for: "))
    poll = Poll.get(poll_id)
    options = poll.options
    votes_per_option = [len(option.votes) for option in options]
    total_votes = sum(votes_per_option)

    try:
        for option, votes in zip(options, votes_per_option):
            percentage = votes / total_votes * 100
            print(f"{option.text} for {votes} ({percentage:.2f}% of total)")
    except ZeroDivisionError:
        print("No votes yet cast for this poll.")

    vote_log = input("Would you like to see the vote log? (y/N) ")

    if vote_log == "y":
        _print_votes_for_options(options)


def randomize_poll_winner():
    poll_id = int(input("Enter poll you'd like to pick a winner for: "))
    poll = Poll.get(poll_id)
    options = from_list_to_dict_option(poll.options)
    _print_poll_options(options)

    option_num = input("Enter which is the winning option, we'll pick a random winner from voters: ")
    option_id = options.get(option_num).id
    votes = Option.get(option_id).votes
    if votes:
        winner = random.choice(votes)
        print(f"The randomly selected winner is {winner[0]}.")
    else:
        print("No one voted for this option.")


MENU_OPTIONS = {
    "1": prompt_create_poll,
    "2": list_open_polls,
    "3": prompt_vote_poll,
    "4": show_poll_votes,
    "5": randomize_poll_winner
}


def menu():
    with get_connection() as connection:
        database.create_tables(connection)

    while (selection := input(MENU_PROMPT)) != "6":
        try:
            MENU_OPTIONS[selection]()
        except KeyError:
            print("Invalid input selected. Please try again.")


if __name__ == "__main__":
    menu()
