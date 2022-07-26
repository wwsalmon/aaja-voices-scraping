from pyppeteer import launch
from bs4 import BeautifulSoup
import markdownify
import pandas as pd


pd.set_option('display.max_columns', None)


async def get_all():
    browser = await launch()
    page = await browser.newPage()

    members = pd.DataFrame(columns=["name", "title", "organization", "board_years", "join_year", "description"])

    start_year = 1917

    for i in range(2023 - start_year):
        year = start_year + i
        print(year)

        # load html
        await page.goto("https://www.pulitzer.org/board/" + str(year), waitUntil="load")
        await page.waitForSelector("div.board-member", visible=True)
        html = await page.content()

        # bs parse
        soup = BeautifulSoup(html, "html.parser")
        member_divs = soup.select("div.board-member")

        # add/update array
        for member_div in member_divs:
            description = markdownify.markdownify(getattr(member_div.select_one("div[ng-bind-html='::member.body.und[0].safe_value | to_trusted']"), "text", None), heading_style="ATX")
            search_string = "joined the Pulitzer Prize Board in "
            join_year = None
            if search_string in description:
                search_string_index = description.index(search_string)
                year_index = search_string_index + len(search_string)
                join_year = description[year_index:year_index + 4]

            name = getattr(member_div.select_one("span.board-title"), "text", None)
            title = getattr(member_div.select_one("span[ng-bind-html='::member.field_job_title.und[0].safe_value']"), "text", None)
            organization = getattr(member_div.select_one("span[ng-bind-html='::member.field_employer.und[0].safe_value']"), "text", None)

            match_indices = members.index[members["name"] == name].tolist()

            if len(match_indices):
                match_index = match_indices[0]
                members.loc[match_index, "board_years"].append(year)
                members.loc[match_index, "title"] = title
                members.loc[match_index, "organization"] = organization
                members.loc[match_index, "description"] = description
                members.loc[match_index, "join_year"] = join_year
            else:
                members.loc[len(members.index)] = {
                    "name": name,
                    "board_years": [year],
                    "title": title,
                    "organization": organization,
                    "description": description,
                    "join_year": join_year
                }

    await browser.close()

    return members
