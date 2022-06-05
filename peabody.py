from pyppeteer import launch
from bs4 import BeautifulSoup
import markdownify
import pandas as pd
from clean import clean


def get_dir_dict(director, coast):
    return {
            "name": clean(director.select_one("p.director__name").text),
            "title": clean(director.select_one("p.director__title").text),
            "coast": coast,
            "board": "directors",
            "description": None,
        }


def get_juror_dict(juror, board):
    return {
            "name": clean(juror.select_one("p.juror__name").text),
            "title": None,
            "coast": None,
            "board": board,
            "description": markdownify.markdownify(clean(juror.select_one("div.juror__bio").text))
    }


async def get_all():
    browser = await launch()
    page = await browser.newPage()

    members = pd.DataFrame(columns=["name", "title", "coast", "board", "description"])

    await page.goto("https://peabodyawards.com/our-story", waitUntil="load")
    html = await page.content()

    # bs parse
    soup = BeautifulSoup(html, "html.parser")

    west_coast_dirs = soup.select("div#tab-west-coast li.director")
    east_coast_dirs = soup.select("div#tab-east-coast li.director")

    for director in west_coast_dirs:
        members.loc[len(members.index)] = get_dir_dict(director, "west")

    for director in east_coast_dirs:
        members.loc[len(members.index)] = get_dir_dict(director, "east")

    jurors = soup.select("div#board-of-jurors li.juror")

    for juror in jurors:
        members.loc[len(members.index)] = get_juror_dict(juror, "jurors")

    interactives = soup.select("div#interactive-board li.juror")

    for juror in interactives:
        members.loc[len(members.index)] = get_juror_dict(juror, "interactives")

    await browser.close()

    return members
