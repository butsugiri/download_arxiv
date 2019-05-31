# -*- coding: utf-8 -*-
import os
import sys
import time
import urllib
from urllib.request import urlretrieve
from pybtex import database

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


def download_from_arxiv(url, dirpath='./'):
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

    if not paper.get('pdf_url', ''):
        print("Object has no PDF URL.")
        return
    if dirpath[-1] != '/':
        dirpath += '/'

    path = dirpath + custom_slugify(paper) + '.pdf'
    urlretrieve(paper['pdf_url'], path, reporthook=reporthook)
    return path


def download_from_acl(url, dirpath='./'):
    bib_url = url.strip('\n').rstrip('/') + '.bib'
    bib = urllib.request.urlopen(bib_url).read().decode('utf-8')
    bib_database = database.parse_string(bib, bib_format='bibtex')
    author_lastname = bib_database.entries.values()[0].persons['author'][0].last()
    year = bib_database.entries.values()[0].fields['year'].strip()
    title = bib_database.entries.values()[0].fields['title'].strip()
    out_name = '[{}+{}] {}.pdf'.format(author_lastname, year, title)

    path = os.path.join(dirpath, out_name)
    url = bib_database.entries.values()[0].fields['url'].strip()
    logger.info('Download "{}" from "{}"'.format(title, url))
    urlretrieve(url, path, reporthook=reporthook)
    return path


@click.command()
@click.argument('urls', type=str, nargs=-1)
@click.option(
    '-o',
    '--out',
    default=None,
    type=click.Path(),
    help='path to save pdf'
)
def main(urls, out):
    if out is None:
        if 'ARXIV_OUT' in os.environ:
            out = os.environ['ARXIV_OUT']
        else:
            out = '.'
    logger.info('Save PDF(s) to {}'.format(out))

    for url in urls:
        if 'arxiv' in url:
            download_from_arxiv(url, dirpath=out)
        elif 'acl' in url:
            download_from_acl(url, dirpath=out)
        else:
            raise NotImplementedError
