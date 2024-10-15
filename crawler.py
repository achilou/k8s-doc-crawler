import httpx
import os
import json
from typing import List, Dict, Iterable, Optional, AsyncGenerator
import asyncio

from bs4 import BeautifulSoup, PageElement
from pydantic import BaseModel
from tqdm.asyncio import tqdm_asyncio
import aiofiles

from logger import get_logger
from utils import atimeit, aretry
from wal import WalDict


logger = get_logger(__name__)

DOC_URL_PREFIX = 'https://kubernetes.io'



class MenuItem(BaseModel):
    name: str
    href: str
    children: Optional[List['MenuItem']] = None


# li
def get_menu_item(html: Iterable[PageElement]) -> List[MenuItem]:
    res = []
    for li in html:
        # elem : li
        menu_item = {}
        children = None
        for elem in li.children:
            if elem.name == 'label':
                menu_item["name"] = elem.a.span.string
                menu_item["href"] = elem.a.get('href')
            elif elem.name == 'ul' and elem.has_attr('class'):
                if children is None:
                    children = get_menu_item(elem.children)
                else:
                    logger.warn("multiple ul found for menu item", menu_item.name)
        try:
            menu_item = MenuItem.model_validate({**menu_item, "children": children})
            res.append(menu_item)
        except Exception as e:
            logger.error(f"invalid menu item {menu_item}: {e}")
    return res

@aretry(max_retries=3)
async def arequest_html(url: str) -> BeautifulSoup:
    # logger.info(f"Requesting {url}")
    
    async with httpx.AsyncClient(follow_redirects=True) as client:  # 使用异步 HTTP 客户端
        response = await client.get(url)  # 发送异步请求
        response.raise_for_status()  # 检查请求是否成功
    
    return BeautifulSoup(response.content, 'html.parser')


@atimeit
async def aget_menu(menu_file_path: str = 'data/menu.json') -> List[MenuItem]:
    if os.path.exists(menu_file_path):
        async with aiofiles.open(menu_file_path, 'r') as f:
            content = await f.read()
        data = json.loads(content)
        return [MenuItem(**d) for d in data]
    else:
        url = f"{DOC_URL_PREFIX}/zh-cn/docs/home"
        soup = await arequest_html(url)
        nav =soup.find("ul", class_='ul-1')
        res = get_menu_item(nav)
        content = json.dumps([m.model_dump() for m in res], ensure_ascii=False,indent=4)
        async with open(menu_file_path, 'w') as f:
            await f.write(content)
        return res


async def doc_dataset(urls: List[str]) -> AsyncGenerator[Dict[str, str], None]:
    """从本地加载所有文档，递归 """
    for url in urls:
        async with aiofiles.open(f"data/html/{url.replace(r'/',  r'-')}.html", 'r') as f:
            content = await f.read()
        yield {'url': url, 'html': content}

@atimeit
async def aget_docs(menu: List[MenuItem]) -> AsyncGenerator[Dict[str, str], None]:
    """获取所有文档"""
    doc_url = await WalDict.from_file('data/wal/doc_log.log')
    if doc_url.is_empty():
        async def dfs(menu: List[MenuItem]):
            for item in menu:
                await doc_url.set(f"{DOC_URL_PREFIX}{item.href}", False)
                if item.children:
                    await dfs(item.children)
        await dfs(menu)

    logger.info(f"Get {len(doc_url.items())} urls...")
    semaphore = asyncio.Semaphore(10)  # 限制并发量
        
    async def _process(url: str):
        async with semaphore:
            html = await arequest_html(url)
        html = html.prettify()

        # 写入文件
        async with aiofiles.open(f"data/html/{url.replace(r'/',r'-')}.html", 'w') as f:
            await f.write(html)

        # 记录已处理的文档
        await doc_url.set(url, str(True))

    tasks =[_process(url) for url, is_processed in doc_url.items() if not is_processed]
    logger.info(f"Processing {len(tasks)} tasks...")
    await tqdm_asyncio.gather(*tasks)
    return doc_dataset(doc_url.keys())



def print_menu_tree(menu_item: MenuItem, indent: str = ''):
    """递归打印菜单的树状结构"""
    # 打印当前菜单项的名称和链接
    print(f"{indent}├── {menu_item.name} ({menu_item.href})")

    # 如果有子菜单，则递归处理
    if menu_item.children:
        for index, child in enumerate(menu_item.children):
            # 判断是否是最后一个子菜单，用于选择连接符号
            if index == len(menu_item.children) - 1:
                print_menu_tree(child, indent + "    ")  # 最后一个子菜单，使用空格缩进
            else:
                print_menu_tree(child, indent + "│   ")  # 不是最后一个，继续使用竖线



if __name__ == '__main__':
    async def main():
        # 获取目录
        menu = await aget_menu()
        # 打印目录树
        for item in menu:
            print_menu_tree(item)
        # 获取所有文档， 存储到data/html目录下,再次调用可以从本地加载
        res = await aget_docs(menu)
        # print(await anext(res))
    asyncio.run(main())