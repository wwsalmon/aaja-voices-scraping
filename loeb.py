from pyppeteer import launch
from bs4 import BeautifulSoup
import pandas as pd
from clean import clean


pd.set_option('display.max_columns', None)


async def get_all():
    browser = await launch()
    page = await browser.newPage()

    members = pd.DataFrame(columns=["name", "title"])

    await page.goto("https://www.anderson.ucla.edu/news-and-events/signature-events/gerald-loeb-awards/final-judges", waitUntil="load")
    html = await page.content()

    # bs parse
    soup = BeautifulSoup(html, "html.parser")

    judges = soup.select("div.block--bio-card")

    for judge in judges:
        members.loc[len(members.index)] = {
            "name": clean(judge.select_one("div.profile-name").text),
            "title": clean(judge.select_one("div.bio-card__field-text").text),
        }

    await browser.close()

    return members
