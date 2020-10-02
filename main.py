import argparse
from datetime import datetime

from bs4 import BeautifulSoup


class Story:

    __slots__ = ["code", "title"]

    def __init__(self, code, title):
        self.code = code
        self.title = title

    def __str__(self):
        return f"{self.code} - {self.title}"


class Sprint:

    __slots__ = ["goals", "dates", "stories"]

    def __init__(self, goals, dates, stories):
        self.goals = goals
        self.dates = dates
        self.stories = stories

    def __str__(self):
        return f"# {self.dates}\n\n## Sprint Goal\n>{self.goals}\n\n{Table(self.stories)}"


class Table:

    __slots__ = ["stories"]

    def __init__(self, stories=None):
        if stories is None:
            stories = []
        self.stories = stories

    def __str__(self):
        markdown = self.markdown_header()
        for story in self.stories:
            markdown += self.story_as_row(story)
        return markdown

    @staticmethod
    def markdown_header():
        return "| Number | Title | Summary | Demo |\n|--------|-------|---------|------|\n"

    @staticmethod
    def story_as_row(story):
        return f"| {story.code} | {story.title} |  |  |\n"


def main():
    args = parse_args()
    content = get_content(args)
    sprint = parse(content)
    write_sprint(sprint, args.output_file)


def parse_args():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-url", "-u",  help="URL of the sprint report.")
    group.add_argument("-file", "-f", help="Local copy of the sprint report.")
    parser.add_argument("output_file", help="File to append new sprint to.")
    return parser.parse_args()


def write_sprint(sprint, output_file):
    with open(output_file, "a") as file:
        file.write("\n" + str(sprint))


def extract_stories(parsed_html):
    story_rows = [row for row in parsed_html.body.findAll('tr') if row.find("th") is None]
    stories = []
    for story_row in story_rows:
        elements = story_row.findAll("td")
        stories.append(Story(elements[0].text, elements[1].text))
    return stories


def extract_goals(parsed_html):
    return parsed_html.body.find('div', {"class": "ghx-sprint-goal"}).text


def extract_dates(parsed_html):
    start_date_raw = parsed_html.body.find('span', {"title": "Start Date"}).text
    end_date_raw = parsed_html.body.find('span', {"title": "Projected End Date"}).text
    return f"{reformat_date(start_date_raw)} - {reformat_date(end_date_raw)}"


def reformat_date(date_string):
    parsed_date = datetime.strptime(date_string, '%d/%b/%y %I:%M %p')
    return datetime.strftime(parsed_date, "%d %B %Y")


def parse(content):
    parsed_html = BeautifulSoup(content, features="html.parser")
    return Sprint(extract_goals(parsed_html), extract_dates(parsed_html), extract_stories(parsed_html))


def read_file_from_url(url):
    raise NotImplementedError()


def read_local_file(file):
    with open(file, 'r') as file:
        return file.read()


def get_content(args):
    if args.url:
        return read_file_from_url(args.url)
    else:
        return read_local_file(args.file)


if __name__ == '__main__':
    main()
