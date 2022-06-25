from __future__ import annotations

import toml


from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from bs4 import BeautifulSoup
from minify_html import minify

app = FastAPI()
app.mount("/assets", StaticFiles(directory="subapps/blog/assets"), name="assets")

templates = Jinja2Templates(directory="subapps/blog/templates")


@app.get("/")
async def index():
    return HTMLResponse(content=Path("subapps/blog/index.html").read_text())


@app.get("/articles/{article_name}", response_class=HTMLResponse)
async def read_article(request: Request, article_name: str):
    context = {
        "request": request,
        **get_context(article_name),
        "size": "{{size}}"  # this trick allows {{size}} to remain un-formatted, because
        # if no "size" is provided in this context dictionary, {{size}} is removed,
        # but we want to keep {{size}} because we'll calculate {{size}} after formatting
    }
    temp = templates.TemplateResponse("article.html", context)

    context["size"] = f"{len(temp.body)/1000:.2f}KB"

    return templates.TemplateResponse("article.html", context)


def get_context(article_name: str) -> dict:
    meta = toml.load(f"subapps/blog/articles/{article_name}/meta.toml")
    content = get_content(article_name)

    context = {
        "author": meta["author"]["name"],
        "description": meta["meta"]["description"],
        "title": meta["meta"]["title"],
        "url": f'https://blog.francisdb.net/articles/{meta["meta"]["url_title"]}',
        "date": meta["meta"]["date"],
        # "style": minify(style, minify_css=True),
        "content": minify(content, minify_css=False, minify_js=False),
    }

    return context


def get_content(article_name: str) -> str:
    article = Path(f"subapps/blog/articles/{article_name}/article.html")
    soup = BeautifulSoup(article.read_text(), features="html.parser")
    # style = soup.find("style")
    article = soup.find("article")
    return article.decode_contents()
