from fastapi import FastAPI
from subapps.blog.app import app as blog_app

app = FastAPI()

app.mount("/blog", blog_app, name="blog")
