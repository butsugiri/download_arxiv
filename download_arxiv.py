# -*- coding: utf-8 -*-
import os
import sys
import time
from urllib.request import urlretrieve

import arxiv
import click
from dateutil.parser import parse
from logzero import logger


def reporthook(count, block_size, total_size):
    global start_time
    if count == 0:
        start_time = time.time()
        return
    duration = time.time() - start_time
    progress_size = int(count * block_size)
    speed = int(progress_size / (1024 * duration))
    percent = int(count * block_size * 100 / total_size)
    sys.stdout.write(
        "\r{}%, {} KB, {} KB/s, {:.1f} seconds passed".format(min(percent, 100), progress_size / 1024, speed, duration))
    sys.stdout.flush()


def download(obj, slugify, dirpath='./'):
    if not obj.get('pdf_url', ''):
        print("Object has no PDF URL.")
        return
    if dirpath[-1] != '/':
        dirpath += '/'
    path = dirpath + slugify(obj) + '.pdf'
    urlretrieve(obj['pdf_url'], path, reporthook=reporthook)
    return path


@click.command()
@click.argument('urls', type=str, nargs=-1)
@click.option(
    '-o',
    '--out',
    default='.',
    type=click.Path(),
    help='path to save pdf'
)
def main(urls, out):
    for url in urls:
        if url.endswith('.pdf'):
            paper_id = os.path.splitext(os.path.basename(url))[0]
        else:
            paper_id = os.path.basename(url)
        paper = arxiv.query(id_list=[paper_id])[0]

        def custom_slugify(obj):
            author_last_name = obj['authors'][0].strip().split(' ')[-1]
            year = parse(obj['published']).year
            title = obj['title'].strip().replace('\n', '')
            logger.info('Download "{}" from "{}"'.format(title, obj['pdf_url']))
            return '[{}+{}] {}'.format(author_last_name, year, title)

        download(paper, slugify=custom_slugify, dirpath=out)
