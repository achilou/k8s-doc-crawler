# K8s文档爬虫

基于httpx、beautifulsoup4和AsyncIO的K8s文档爬虫。爬取内容包括目录和文档，支持：

- 断连重试
- 并发请求
- 本地缓存
- AsyncGenerator输出数据

## python版本

python3.10+

## 安装

```
pip3 install -r requirements.txt
```

## 使用

```shell
python3 crawler.py
```

## 说明

```python
# 获取目录
menu = await aget_menu()

# 打印目录树
for item in menu:
    print_menu_tree(item)

# 获取所有文档， 存储到data/html目录下,再次调用可以从本地直接加载
res = await aget_docs(menu)

```