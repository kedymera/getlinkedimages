#!/usr/bin/env python3

def prettytitle(titleobj) -> str:
    title = "untitled"
    if titleobj:
        title = titleobj.text.replace(" ", "+").replace("'", "")
    return title

def getfoldername(url: str, title: str) -> str:
    from datetime import datetime
    from urllib.parse import urlparse
    FOLDERNAME = "{year:04}{month:02}{day:02}{hour:02}{minute:02}{second:02}_{host}_{title}"

    dt = datetime.now()
    return FOLDERNAME.format(
        year=dt.year,
        month=dt.month,
        day=dt.day,
        hour=dt.hour,
        minute=dt.minute,
        second=dt.second,
        host=urlparse(url).netloc,
        title=title
    )


def getlinkedimages(url: str, foldername: str|None) -> int:
    from requests import get
    from bs4 import BeautifulSoup as bs
    from os import mkdir, path
    from urllib.parse import urljoin
    from time import perf_counter
    page = get(url)
    soup = bs(page.text, features="lxml")

    if not foldername:
        title = prettytitle(soup.title)
        foldername = getfoldername(url, title)
    mkdir(foldername)

    size = 0
    imgcount = 0
    tstart = perf_counter()
    for link in soup.findAll("a"):
        if not link.has_attr("href") or not link["href"].endswith(".jpg"):
            continue
        imgcount += 1
        imgurl = urljoin(url, link["href"])
        filename = imgurl.rpartition("/")[2]
        print(f"downloading file {filename}")
        imgreq = get(imgurl)
        with open(path.join(foldername, filename), "wb") as f:
            size += f.write(imgreq.content)
    t = perf_counter() - tstart
    msize = size/1024.0/1024
    print(f"downloaded {imgcount} image{'s' if imgcount>1 else ''} "
            +f"totalling {msize:.1f} MiB in {t:.1f} s ({msize/t:.1f} MiB/s)")
    return 0

def main():
    from sys import argv
    if len(argv) < 2:
        return 1

    customfoldername = None
    if len(argv) == 3:
        customfoldername = argv[2]

    return getlinkedimages(argv[1], customfoldername)

if __name__ == "__main__":
    exit(main())
