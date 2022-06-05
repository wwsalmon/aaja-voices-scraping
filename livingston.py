from pyppeteer import launch
from bs4 import BeautifulSoup
import markdownify
import pandas as pd
from clean import clean


pd.set_option('display.max_columns', None)


async def get_all():
    browser = await launch()
    page = await browser.newPage()

    members = pd.DataFrame(columns=["name", "title", "bio", "board"])

    await page.goto("https://wallacehouse.umich.edu/livingston-awards/judges/", waitUntil="load")
    html = await page.content()

    # bs parse
    soup = BeautifulSoup(html, "html.parser")

    judges = soup.select("div.row.judges div.row.director")

    links = []

    for judge in judges:
        link = judge.select_one("p.name a.link")["href"]
        links.append(link)

    print(links)

    for link in links:
        await page.goto(link)
        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")

        name = clean(soup.select_one("h2.name").text)

        title_raw = clean(str(soup.select_one("p.title")))

        title_split = title_raw.replace("<br>", "<br/>").split("<br/>")
        title = BeautifulSoup(title_split[0], "html.parser").text
        board = BeautifulSoup(title_split[1], "html.parser").text

        bio_raw = soup.select_one("div.content")
        for el in bio_raw.select("p.title, p.bio"): el.decompose()
        bio = markdownify.markdownify(clean(bio_raw.text))

        members.loc[len(members.index)] = {
            "name": name,
            "title": title,
            "board": board,
            "bio": bio,
        }

        print(members.head())

    await browser.close()

    return members
