import json
from pathlib import Path

from notion_client import Client

# Initialize the Notion client
# example secret token that has been revoked
notion = Client(auth="secret_oD4VbnSak4XwemKXJx81Pr9zbkbdQZZgmReTrwYJPcQ")

# example page ids that have been deleted
test_page = "e929fe44d2574857b67f22be7693ee58"  # the test synced links page
test_page = "9a60b5235e96411a8725d5414a323b92"  # all images import page

page = notion.blocks.retrieve(test_page)
children = notion.blocks.children.list(test_page)

print()

print(json.dumps(children, indent=2))
