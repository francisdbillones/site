from __future__ import annotations

import toml

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from bs4 import BeautifulSoup

app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("/")
async def index():
    return HTMLResponse(content=Path("index.html").read_text())


@app.get("/articles/{article_name}", response_class=HTMLResponse)
async def read_article(request: Request, article_name: str):
    context = {"request": request, **get_context(article_name)}
    return templates.TemplateResponse("article.html", context)


def get_context(article_name: str) -> dict:
    meta = toml.load(f"./articles/{article_name}/meta.toml")
    style, content = get_content(article_name)

    context = {
        "author": meta["author"]["name"],
        "description": meta["meta"]["description"],
        "title": meta["meta"]["title"],
        "url": f'https://blog.francisdb.net/articles/{meta["meta"]["url_title"]}',
        "date": meta["meta"]["date"],
        "style": style,
        "content": content,
    }

    return context


def get_content(article_name: str) -> str:
    article = Path(f"./articles/{article_name}/article.html")
    # breakpoint()
    soup = BeautifulSoup(article.read_text(), features="html.parser")
    style = soup.find("style")
    article = soup.find("article")
    return style.decode_contents(), article.decode_contents()
