import os
import requests
import pymongo

from pyquery import PyQuery as pq


class Movie():
    db = pymongo.MongoClient()['Douban']

    def __init__(self):
        self.name = ''
        self.other = ''
        self.score = 0
        self.quote = ''
        self.cover_url = ''
        self.ranking = 0


def get(url, filename):
    folder = 'cached'
    if not os.path.exists(folder):
        os.makedirs(folder)

    path = os.path.join(folder, filename)
    if os.path.exists(path):
        with open(path, 'rb') as f:
            s = f.read()
            return s
    else:
        # 发送网络请求并建立页面缓存
        r = requests.get(url)
        with open(path, 'wb') as f:
            f.write(r.content)
            return r.content


def movie_from_div(div):
    e = pq(div)
    m = Movie()
    m.name = e('.title').text()
    m.other = e('.other').text()
    m.score = e('.rating_num').text()
    m.quote = e('.inq').text()
    m.cover_url = e('img').attr('src')
    m.ranking = e('.pic').find('em').text()
    data = m.__dict__
    print('dict', data)
    m.db.movie.save(data)
    return m


def save_cover(movies):
    for m in movies:
        filename = '{}.webp'.format(m.ranking)
        get(m.cover_url, filename)


def movies_from_url(url):
    # https://movie.douban.com/top250?start=100
    filename = '{}.html'.format(url.split('=', 1)[-1])
    page = get(url, filename)
    e = pq(page)
    items = e('.item')
    movies = [movie_from_div(i) for i in items]
    save_cover(movies)
    return movies


def main():
    for i in range(0, 250, 25):
        url = 'https://movie.douban.com/top250?start={}'.format(i)
        movies_from_url(url)


if __name__ == '__main__':
    main()
