from pyppeteer import launch
import asyncio
from bs4 import BeautifulSoup
import csv
import markdownify


async def get_html(year):
    browser = await launch()
    page = await browser.newPage()
    await page.goto("https://www.pulitzer.org/board/" + str(year), waitUntil="load")
    await page.waitForSelector("div.board-member", visible=True)
    html = await page.content()
    await browser.close()
    return html


def get_members(html):
    soup = BeautifulSoup(html, "html.parser")
    members = soup.select("div.board-member")
    members_arr = []

    for member in members:
        description = markdownify.markdownify(getattr(member.select_one("div[ng-bind-html='::member.body.und[0].safe_value | to_trusted']"), "text", None), heading_style="ATX")
        search_string = "joined the Pulitzer Prize Board in "
        join_year = None
        if search_string in description:
            search_string_index = description.index(search_string)
            year_index = search_string_index + len(search_string)
            join_year = description[year_index:year_index + 4]

        member_dict = {
            "name": getattr(member.select_one("span.board-title"), "text", None),
            "title": getattr(member.select_one("span[ng-bind-html='::member.field_job_title.und[0].safe_value']"), "text", None),
            "organization": getattr(member.select_one("span[ng-bind-html='::member.field_employer.und[0].safe_value']"), "text", None),
            "join_year": join_year,
            "description": description,
        }
        members_arr.append(member_dict)

    return members_arr


def to_file(members_arr, filename):
    keys = members_arr[0].keys()
    with open(filename + ".csv", "w", newline="") as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(members_arr)


for i in range(2023 - 1988):
    year = 1988 + i
    print(year)
    to_file(get_members(asyncio.run(get_html(year))), str(year))
