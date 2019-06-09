# 腾讯视频-电影板块小爬虫

做了一些小项目，用的技术和技巧会比较散比较杂，写一个小品文记录一下，帮助熟悉。

需求：经常在[腾讯视频](v.qq.com)上看电影，在影片库里有一个"豆瓣好评"板块。我一般会在这个条目下面挑电影。但是电影很多，又缺乏索引，只能不停地往下来，让js加载更多的条目。然而前面的看完了，每次找新的片就要拉很久。所以用爬虫将"豆瓣好评"里的电影都爬下来整理到一个表中，方便选片。

[Github repo](https://github.com/yangrq1018/vqq-douban-film)

## 依赖

需要如下Python包：

- requests
- bs4 - Beautiful soup
- pandas

就这些，不需要复杂的自动化爬虫架构，简单而且常用的包就够了。

## 爬取影片信息

首先观察[电影频道](https://v.qq.com/channel/movie?listpage=1&channel=movie&sort=18&_all=1)，发现是异步加载的。可以用Firefox（Chrome也行）的inspect中的network这个tab来筛选查看可能的api接口。很快发现接口的URL是这个格式的：

```python
base_url = 'https://v.qq.com/x/bu/pagesheet/list?_all=1&append=1&channel=movie&listpage=2&offset={offset}&pagesize={page_size}&sort={sort}'
```

其中`offset`是请求页开始的位置，`pagesize`是每页请求的数量，`sort`是类型。在这里`sort=21`指我们需要的"豆瓣好评"类型。`pagesize`不能大于30，大于30也只会返回三十个元素，低于30会返回指定数量的元素。

```python
# 让Pandas完整到处过长的URL，后面会需要
pd.set_option('display.max_colwidth', -1)

base_url = 'https://v.qq.com/x/bu/pagesheet/list?_all=1&append=1&channel=movie&listpage=2&offset={offset}&pagesize={page_size}&sort={sort}'

# 豆瓣最佳类型
DOUBAN_BEST_SORT = 21

NUM_PAGE_DOUBAN = 167
```

写一个小小的循环就可以发现，豆瓣好评这个类型总共有167页，每页三十个元素。

我们使用`requests`这个库来请求网页，`get_soup`会请求第`page_idx`页的元素，用`Beautiful soup`来解析`response.content`，生成一个类似`DOM`，可以很方便地查找我们需要的element的对象。我们返回一个`list`。每个电影条目是包含在一个叫list_item的`div`里的，所以写一个函数来帮助我们提取所有的这样的`div`。

```python
def get_soup(page_idx, page_size=30, sort=DOUBAN_BEST_SORT):
    url = base_url.format(offset=page_idx * page_size, 	page_size=page_size, sort=sort)
    res = requests.get(url)
    soup = bs4.BeautifulSoup(res.content.decode('utf-8'), 'lxml')
    return soup

def find_list_items(soup):
    return soup.find_all('div', class_='list_item')
```

我们遍历每一页，返回一个含有所有的被`bs4`过的条目元素的HTML的`list`。

```python
def douban_films():
    rel = []
    for p in range(NUM_PAGE_DOUBAN):
        print('Getting page {}'.format(p))
        soup = get_soup(p)
        rel += find_list_items(soup)
    return rel
```

这是其中的一部电影的HTML代码：

```html
<div __wind="" class="list_item">
<a class="figure" data-float="j3czmhisqin799r" href="https://v.qq.com/x/cover/j3czmhisqin799r.html" tabindex="-1" target="_blank" title="霸王别姬">
<img alt="霸王别姬" class="figure_pic" onerror="picerr(this,'v')" src="//puui.qpic.cn/vcover_vt_pic/0/j3czmhisqin799rt1444885520.jpg/220"/>
<img alt="VIP" class="mark_v" onerror="picerr(this)" src="//i.gtimg.cn/qqlive/images/mark/mark_5.png" srcset="//i.gtimg.cn/qqlive/images/mark/mark_5@2x.png 2x"/>
<div class="figure_caption"></div>
<div class="figure_score">9.6</div>
</a>
<div class="figure_detail figure_detail_two_row">
<a class="figure_title figure_title_two_row bold" href="https://v.qq.com/x/cover/j3czmhisqin799r.html" target="_blank" title="霸王别姬">霸王别姬</a>
<div class="figure_desc" title="主演：张国荣 张丰毅 巩俐 葛优">主演：张国荣 张丰毅 巩俐 葛优</div>
</div>
<div class="figure_count"><svg class="svg_icon svg_icon_play_sm" height="16" viewbox="0 0 16 16" width="16"><use xlink:href="#svg_icon_play_sm"></use></svg>4671万</div>
</div>
```

不难发现，霸王别姬这部电影，名称、播放地址、封面、评分、主演，是否需要会员和播放量都在这个`div`中。在ipython这样的interactive环境中，可以方便地找出怎么用bs来提取他们的方法。我试用的一个技巧是，可以打开一个`spyder.py`文件，在里面编写需要的函数，将ipython的自动重载模组的选项打开，然后就可以在console里debug之后将代码复制到文件里，然后ipython中的函数也会相应的更新。这样的好处是会比在ipython中改动代码方便许多。具体如何打开ipython的自动重载：

```
%load_ext autoreload
%autoreload 2 # Reload all modules every time before executing Python code
%autoreload 0 # Disable automatic reloading
```

这个`parse_films`函数用bs中的两个常用方法提取信息：

- find
- find_all

因为豆瓣的API已经关闭了检索功能，爬虫又会被反爬虫检测到，本来想检索到豆瓣的评分添加上去这个功能就放弃了。

`OrderedDict`可以接受一个由(key, value)组成的list，然后key的顺序会被记住。这个在之后我们导出为pandas DataFrame的时候很有用。

```python
def parse_films(films):
    '''films is a list of `bs4.element.Tag` objects'''
    rel = []
    for i, film in enumerate(films):
        title = film.find('a', class_="figure_title")['title']
        print('Parsing film %d: ' % i, title)
        link = film.find('a', class_="figure")['href']
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
```
## 导出

最后，我们调用写好的函数，在主程序中运行。

被解析好，list of dictionaries格式的对象，可以直接传给DataFrame的constructor。按照评分排序，最高分在前面，然后将播放链接转换成HTML的链接标签，更加美观而且可以直接打开。

>注意，pandas生成的csv文件一直和excel有兼容性问题，在有中文字符的时候会乱码。解决方法是选择utf_8_sig这个encoding，就可以让excel正常解码了。

`Pickle`是一个Python十分强大的serialization库，可以保存Python的对象为文件，再从文件中加载Python的对象。我们将我们的DataFrame保存为`.pkl`。调用`DataFrame`的`to_html`方法保存一个HTML文件，注意要将`escape` 设置为False不然超链接不能被直接打开。

```python
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
```

注意，因为观影链接很长，超过30-40个字符了，所以pandas默认在转换为字符串的时候会裁切过长的部分变成…，这样会导致HTML tag `<a href="XXX">link</a>`不能加载出来，因为后面的 tag 被裁掉了。解决这个问题需要配置Pandas的全局变量`pd.set_option('display.max_colwidth', -1)`.

## 项目管理

代码部分就是这样。那么写完了代码，就要把它归档保存，也便于分析。选择放在Github上。

那么，其实Github是提供了一个命令行工具的（不是`git`，是`git`的一个扩展），叫做`hub`。macOS用户可以这样安装

```python
brew install hub
```

`hub`有许多比`git`更简练的语法，我们这里主要用

```bash
hub create -d "Create repo for our proj" vqq-douban-film
```

来直接从命令行创建repo，是不是很酷！根本不用打开浏览器。然后可能会被提示在Github上登记一个你的SSH公钥（验证权限），如果没有的话用`ssh-keygen`生成一个就好了，在Github的设置里把`.pub`的内容复制进去。

项目目录里，可能会有`__pycache__`和`.DS_Store`这样你不想track的文件。手写一个`.gitignore`又太麻烦，有没有工具呢，肯定有的！Python有一个包

```bash
pip install git-ignore
git-ignore python #	产生一个python的template
# 手动把.DS_Store加进去
```

只用命令行，装逼装到爽。