# -*- coding: utf-8 -*-
import os

import arxiv
import click
from dateutil.parser import parse


@click.command()
@click.argument("url", type=str)
@click.option(
    '-o',
    '--out',
    default='.',
    help='path to save pdf'
)
def main(url, out):
    paper_id = os.path.basename(url)
    paper = arxiv.query(id_list=[paper_id])[0]

    def custom_slugify(obj):
        author_last_name = obj['authors'][0].strip().split(' ')[-1]
        year = parse(obj['published']).year
        title = obj['title'].strip().replace('\n', '')
        return '[{}+{}] {}'.format(author_last_name, year, title)

    arxiv.download(paper, slugify=custom_slugify, dirpath=out)
