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