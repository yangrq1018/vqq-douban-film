import requests
import bs4
from collections import OrderedDict
from pandas import DataFrame
import pandas as pd


# Prevent Pandas from folding long urls
pd.set_option('display.max_colwidth', -1)

base_url = 'https://v.qq.com/x/bu/pagesheet/list?_all=1&append=1&channel\
=movie&listpage=2&offset={offset}&pagesize={page_size}&sort={sort}'

# 豆瓣最佳
DOUBAN_BEST_SORT = 21

NUM_PAGE_DOUBAN = 167

def get_soup(page_idx, page_size=30, sort=DOUBAN_BEST_SORT):
    url = base_url.format(offset=page_idx * page_size, page_size=page_size,
                        sort=sort)
    res = requests.get(url)
    soup = bs4.BeautifulSoup(res.content.decode('utf-8'), 'lxml')
    return soup

def find_list_items(soup):
    return soup.find_all('div', class_='list_item')

def douban_films():
    rel = []
    for p in range(NUM_PAGE_DOUBAN):
        print('Getting page {}'.format(p))
        soup = get_soup(p)
        rel += find_list_items(soup)
    return rel

def parse_films(films):
    '''films is a list of `bs4.element.Tag` objects'''
    rel = []
    for i, film in enumerate(films):
        title = film.find('a', class_="figure_title")['title']
        print('Parsing film %d: ' % i, title)
        link = film.find('a', class_="figure")['href']
        # remove "preceding \\" to find the accessible URL
        img_link = film.find('img', class_="figure_pic")['src']

        # test if need VIP
        need_vip = bool(film.find('img', class_="mark_v"))
        score = getattr(film.find('div', class_='figure_score'), 'text', None)
        if score: score = float(score)
        cast = film.find('div', class_="figure_desc")
        if cast:
            cast = cast.get('title', None)
        play_amt = film.find('div', class_="figure_count").get_text()

        # db_score, db_link = search_douban(title)
        # Store key orders
        dict_item = OrderedDict([
            ('title', title),
            ('vqq_score', score),
            # ('db_score', db_score),
            ('need_vip', need_vip),
            ('cast', cast),
            ('play_amt', play_amt),
            ('vqq_play_link', link),
            # ('db_discuss_link', db_link),
            ('img_link', img_link),
        ])

        rel.append(dict_item)

    return rel

def search_douban(film_name):
    res = requests.get('https://www.douban.com/search?q={}'.format(film_name))
    soup = bs4.BeautifulSoup(res.content, 'lxml')
    score = getattr(soup.find('div', class_="result").find('span', class_="rating_nums"), 'text', None)
    if score: score = float(score)
    douban_link = soup.find('div', class_="result").find('a').get('href', None)
    return score, douban_link

if __name__ == '__main__':
    df = DataFrame(parse_films(douban_films()))
    # Sorted by score
    df.sort_values(by="vqq_score", inplace=True, ascending=False)
    # Format links
    df['vqq_play_link'] = df['vqq_play_link'].apply(lambda x: '<a href="{0}">Film link</a>'.format(x))
    df['img_link'] = df['img_link'].apply(lambda x: '<img src="{0}">'.format(x))

    # Chinese characters in Excel must be encoded with _sig
    df.to_csv('vqq_douban_films.csv', index=False, encoding='utf_8_sig')
    # Pickle
    df.to_pickle('vqq_douban_films.pkl')
    # HTML, render hyperlink
    df.to_html('vqq_douban_films.html', escape=False)
