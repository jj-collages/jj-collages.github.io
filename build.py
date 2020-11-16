import logging
import pathlib

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
                "width_in_cm": schema.Or(int, float),
                "height_in_cm": schema.Or(int, float),
                "how_many_printed": int,
                "how_many_sold": int,
                "image_filename": str,
                "price": int,
                schema.Optional("technical_note"): str,
                schema.Optional("description"): str,
            }
        ],
        "exhibitions": [
            {
                "name": str,
                "type": str,
                "year": int,
            }
        ]
    }
)

MARKDOWNER = markdown.Markdown(output_format="html5")


def md_context(template):
    with open(template.filename) as f:
        markdown_content = f.read()
    return {"page_content": MARKDOWNER.convert(markdown_content)}


def render_md(site, template, **kwargs):
    outpath = str(
        pathlib.Path(site.outpath)
        / pathlib.Path(template.filename).with_suffix(".html").parts[-1]
    )
    template = site.get_template("_page.html")
    template.stream(**kwargs).dump(outpath, encoding="utf-8")


def load_data(data_path):
    with open(data_path) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    DATA_SCHEMA.validate(data)
    for i in range(len(data["collages"])):
        data["collages"][i]["slug_name"] = slugify.slugify(
            data["collages"][i]["name"]
        )
    return data


def page_name_context(template):
    return {"page_name": pathlib.Path(template.filename).stem.lower()}


if __name__ == "__main__":
    logging.info("starting website compilation")
    logging.info("loading data")
    data = load_data("data.yml")
    logging.info("compiling templates with staticjinja")
    site = staticjinja.Site.make_site(
        env_globals=data,
        outpath="_build",
        searchpath="templates",
        contexts=[
            (r".*", page_name_context),
            (r".*\.md", md_context),
        ],
        rules=[
            (r".*.md", render_md),
        ],
        mergecontexts=True,
    )
    logging.info("rendering")
    site.render()
