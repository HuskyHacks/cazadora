from colorama import Fore, Style


def print_logo():
    title = "Cazadora"
    subtitle = "Triage Script for Sussy M365 OAuth Apps"
    author_info = "Matt Kiely | Principal Security Researcher | Huntress"

    border_length = 60

    title_line = title.center(border_length)
    subtitle_line = subtitle.center(border_length)
    author_line = author_info.center(border_length)
    border = "=" * border_length

    print(Fore.CYAN + f"""
{border}
{title_line}
{subtitle_line}

{author_line}
{border}
""" + Fore.RESET)
