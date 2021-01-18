import logging
import random
import shutil
from pathlib import Path

import markdown
import schema
import slugify
import staticjinja
import yaml

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

DATA_SCHEMA = schema.Schema(
    {
        "collages": [
            {
                "name": str,
                "year": schema.And(int, lambda y: 1900 < y < 2100),
                schema.Optional("width_in_cm"): schema.Or(int, float),
                schema.Optional("height_in_cm"): schema.Or(int, float),
                schema.Optional("how_many_printed", default=8): int,
                schema.Optional("how_many_sold"): int,
                schema.Optional("sold_to"): [
                    schema.And(str, lambda s: len(s) == 2)
                ],
                schema.Optional("image_filename"): str,
                schema.Optional("price"): int,
                schema.Optional("note"): str,
            }
        ],
        "exhibitions": [
            {
                "name": str,
                "type": str,
                "year": int,
            }
        ],
    }
)

MARKDOWNER = markdown.Markdown(output_format="html5")


def md_context(template):
    with open(template.filename) as f:
        markdown_content = f.read()
    return {"page_content": MARKDOWNER.convert(markdown_content)}


def collage_context(template):
    collage_slug_name = Path(template.filename).stem
    return {"collage_slug_name": collage_slug_name}


def render_md(site, template, **kwargs):
    outpath = str(
        Path(site.outpath)
        / Path(template.filename).with_suffix(".html").parts[-1]
    )
    template = site.get_template("_page.html")
    template.stream(**kwargs).dump(outpath, encoding="utf-8")


def render_collage(site, template, **kwargs):
    outpath = str(
        Path(site.outpath)
        / Path(template.filename).with_suffix(".html").parts[-1]
    )
    template = site.get_template("_collage.html")
    template.stream(**kwargs).dump(outpath, encoding="utf-8")


def load_data(data_path):
    with open(data_path) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    DATA_SCHEMA.validate(data)
    for i in range(len(data["collages"])):
        slug_name = slugify.slugify(data["collages"][i]["name"])
        data["collages"][i]["slug_name"] = slug_name
        data["collages"][i]["how_many_printed"] = data["collages"][i].get(
            "how_many_printed",
            8,
        )
        path = Path("static/collages-small/") / f"{slug_name}.jpg"
        if path.is_file():
            data["collages"][i]["image_filename"] = f"{slug_name}.jpg"
        else:
            logging.info("file not found")
            logging.info(str(path))
        if "sold_to" in data["collages"][i]:
            for j in range(len(data["collages"][i]["sold_to"])):
                data["collages"][i]["sold_to"][j] = (
                    data["collages"][i]["sold_to"][j].lower()[0]
                    + data["collages"][i]["sold_to"][j].upper()[1]
                )
    random.shuffle(data["collages"])
    return data


def page_name_context(template):
    return {"page_name": Path(template.filename).stem.lower()}


if __name__ == "__main__":
    logging.info("starting website compilation")
    logging.info("loading data")
    data = load_data("data.yml")
    template_dir = Path("templates")
    build_template_dir = Path("_build_templates")
    if build_template_dir.is_dir():
        shutil.rmtree(build_template_dir)
    shutil.copytree(template_dir, build_template_dir)
    for collage in data["collages"]:
        path = (build_template_dir / collage["slug_name"]).with_suffix(
            ".collage"
        )
        with open(path, "w") as f:
            f.write("")
    logging.info("compiling templates with staticjinja")
    site = staticjinja.Site.make_site(
        env_globals=data,
        outpath="_build",
        searchpath="_build_templates",
        contexts=[
            (r".*", page_name_context),
            (r".*\.md", md_context),
            (r".*\.collage", collage_context),
        ],
        rules=[
            (r".*.md", render_md),
            (r".*\.collage", render_collage),
        ],
        mergecontexts=True,
    )
    logging.info("rendering")
    site.render()
