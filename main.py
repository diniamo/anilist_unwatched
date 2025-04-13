from argparse import ArgumentParser
import requests


def get_title_string(title):
    return title["english"] or title["romaji"] or title["native"]

def hyperlink(text, link):
    return f"\033]8;;{link}\033\\{text}\033]8;;\033\\"


parser = ArgumentParser(
    "anilist_unwatched",
    description="List unwatched sequels and side stories on your AniList profile",
)
parser.add_argument("username")
parser.add_argument("-s", "--side-stories", action="store_true")
args = parser.parse_args()

with open("query.graphql", "r") as file:
    response = requests.post(
        "https://graphql.anilist.co",
        json={"query": file.read(), "variables": {"username": args.username}},
    ).json()

medias = list(
    map(
        lambda e: e["media"],
        response["data"]["MediaListCollection"]["lists"][0]["entries"],
    )
)
ids = set(media["id"] for media in medias)

for media in medias:
    unwatched = []

    relations = media["relations"]
    for edge, node in zip(relations["edges"], relations["nodes"]):
        relation_type = edge["relationType"]

        if relation_type == "SEQUEL" or (args.side_stories and relation_type == "SIDE_STORY"):
            if node["id"] not in ids and node["status"] == "FINISHED":
                unwatched.append(hyperlink(get_title_string(node["title"]), node["siteUrl"]))

    if len(unwatched) > 0:
        print(hyperlink(get_title_string(media["title"]), media["siteUrl"]))
        for i in range(1, len(unwatched) - 1):
            print(f"├ {unwatched[i]}")
        print(f"╰ {unwatched[-1]}", end="\n\n")
