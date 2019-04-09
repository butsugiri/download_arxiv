# -*- coding: utf-8 -*-
import os

import arxiv
import click
from dateutil.parser import parse
from logzero import logger


@click.command()
@click.argument("urls", type=str, nargs=-1)
@click.option(
    '-o',
    '--out',
    default='.',
    type=click.Path(),
    help='path to save pdf'
)
def main(urls, out):
    for url in urls:
        paper_id = os.path.basename(url)
        paper = arxiv.query(id_list=[paper_id])[0]

        def custom_slugify(obj):
            author_last_name = obj['authors'][0].strip().split(' ')[-1]
            year = parse(obj['published']).year
            title = obj['title'].strip().replace('\n', '')
            logger.info('Download "{}" from "{}"'.format(title, obj['pdf_url']))
            return '[{}+{}] {}'.format(author_last_name, year, title)

        arxiv.download(paper, slugify=custom_slugify, dirpath=out)
