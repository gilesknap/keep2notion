import re
from datetime import datetime
from pathlib import Path
from shutil import move

from notion_client import Client
from ruamel.yaml import YAML

# retrieve the secrets from the secrets.yaml file
config_file = Path(__file__).parent / "config.yaml"
config_txt = config_file.read_text()
config = YAML().load(config_txt)

# Initialize the Notion client
notion = Client(auth=config.get("integration_token"))


# Function to create a new page in the Notion database
def create_page(title, tags, children, date_created, colour=""):
    notion.pages.create(
        parent={"type": "database_id", "database_id": config.get("database_id")},
        properties={
            "Name": {"title": [{"text": {"content": title}}]},
            "Tags": {"multi_select": [{"name": tag} for tag in tags]},
            "Date": {
                "date": {
                    "start": str(datetime.fromtimestamp(date_created)),
                    "end": None,
                    "time_zone": None,
                }
            },
            "Colour": {
                "rich_text": [
                    {
                        "text": {"content": colour},
                        "annotations": {
                            "color": colour_conversion(colour),
                        },
                    }
                ]
            },
        },
        children=children,
    )


def colour_conversion(colour):
    if colour == "":
        return "default"
    if colour == "Teal":
        colour = "blue"
    return f"{colour.lower()}_background"


def extract_tags(contents):
    tags = re.findall(r"Keep\/(?:Label)\/(.*)", contents)
    return tags


def extract_colour(contents):
    tags = re.findall(r"Keep\/(?:Color)\/(.*)", contents)
    return tags


def remove_header(contents):
    contents = re.sub(r"---\n[\s\S]*?(---)\n*", "", contents)
    contents = re.sub(r"\n?!\[\[(.*?)\]\]", "", contents)
    return contents


def make_children(title, contents, assets):
    children = []
    for line in contents.split("\n"):
        children.append(
            {
                "object": "block",
                "paragraph": {
                    "rich_text": [
                        {
                            "text": {
                                "content": line,
                            },
                        }
                    ],
                    "color": "default",
                },
            },
        )

    for asset in assets:
        if asset.endswith(".3gp"):
            typ = "video"
        else:
            typ = "image"
        children.append(
            {
                "object": "block",
                "type": typ,
                typ: {
                    "type": "external",
                    "external": {
                        "url": config.get("images_url") + asset,
                    },
                },
            }
        )
    return children


def extract_assets(contents):
    assets = re.findall(r"!\[\[(.*?)\]\]", contents)
    return assets


directory = Path(config.get("source_folder"))
move_f = config.get("move_folder")
if move_f:
    move_folder = Path(move_f)
    move_folder.mkdir(exist_ok=True)
else:
    move_folder = None

# Iterate over all Markdown files in the directory and create pages
for i, filename in enumerate(directory.glob("*.md")):
    print(f"Importing {i}: {filename}...")
    title = filename.stem
    contents = filename.read_text()
    tags = extract_tags(contents)
    colours = extract_colour(contents)
    colour = colours[0] if colours else ""
    assets = extract_assets(contents)
    children = make_children(title, remove_header(contents), assets)
    file_date = filename.stat().st_mtime
    create_page(title, tags, children, file_date, colour)
    if move_folder:
        move(filename, move_folder)


print("Markdown files have been imported into the Notion database.")
