#!/usr/bin/env python3

import os
from os.path import isfile, join
from typing import Dict, Any, List, Tuple
import yaml
import uuid
import json

# import re

ROOT = os.path.dirname(os.path.realpath(__file__))
POSTS_DIRECTORY = f"{ROOT}/content/posts"
IGNORE_POSTS = ["search.md"]


class Document:
    def __init__(self, title: str, date, content: str):
        self.id = str(uuid.uuid4())
        self.title = title
        self.date = str(date)
        self.content = content

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "date": self.date,
            "content": self.content,
        }


def cleanup_markdown_and_symbols(content: str) -> str:
    return content


def extract_content_and_frontmatter(file_path: str) -> Tuple[Dict[str, Any], str]:
    content: str = ""
    frontmatter: Dict[str, Any] = {}

    with open(file_path, "r") as reader:
        foo = reader.read().split("---")
        raw_frontmatter = foo[1]
        raw_content = " ".join(foo[2:])
        frontmatter = yaml.safe_load(raw_frontmatter)
        content = cleanup_markdown_and_symbols(raw_content)

    return (frontmatter, content)


posts: List[str] = [
    f for f in os.listdir(POSTS_DIRECTORY) if isfile(join(POSTS_DIRECTORY, f))
]
index: List[Dict[str, Any]] = []

for f in posts:
    print(f"Found {f}")
    (frontmatter, content) = extract_content_and_frontmatter(f"{POSTS_DIRECTORY}/{f}")

    if ("draft" in frontmatter) and frontmatter.get("draft"):
        print("-- This is a draft. Ignoring...")
    elif f in IGNORE_POSTS:
        print("-- This is an ignored post. Ignoring...")
    else:
        index.append(
            Document(
                frontmatter.get("title"), frontmatter.get("date"), content
            ).to_dict()
        )

with open(f"{ROOT}/static/index.json", "w") as writer:
    writer.write(json.dumps(index))
