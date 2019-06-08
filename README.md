# Tencent Video API

`pagesize` in the url has a maximum value of 30. You may specify pagesize
greater than than 30, but the database will return at most 30 `list_item`. With `pagesize` less than 30, it will return exactly that many items.



## 豆瓣最佳

在豆瓣最佳的这个`sort`中，一共可以查找到$167\times30=5010$部电影。

A sample `<div>` tag for a film:

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



For each film, we will extract:

- Title (str)
- Link (str)
- Cover image link (str)
- Need vip or not (boolean)
- Score (float)
- Cast names (str)
- Playing amount (str)

## Storage

We save the table as an HTML file with clickable link, so any viewer can enter the viewing page of a film easily. We also serialize the Pandas `DataFram` using `pickle`.

