from argparse import ArgumentParser
import requests


def get_title_string(title):
    return title["english"] or title["romaji"] or title["native"]


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

for media in medias:
    unwatched = []

    relations = media["relations"]

    for edge, node in zip(relations["edges"], relations["nodes"]):
        relation_type = edge["relationType"]

        if relation_type == "SEQUEL" or (args.side_stories and relation_type == "SIDE_STORY"):
            if all(m["id"] != node["id"] for m in medias) and node["status"] == "FINISHED":
                unwatched.append(get_title_string(node["title"]))

    for i, title in enumerate(unwatched):
        if i == 0:
            print(get_title_string(media["title"]))

        if i == len(unwatched) - 1:
            print(f"╰ {title}", end="\n\n")
        else:
            print(f"├ {title}")
