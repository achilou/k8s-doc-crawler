import os
from typing import Dict

import aiofiles

class WalDict:
    path: str
    data: dict

    def __init__(self, path: str, data: Dict[str, str]):
        self.path = path
        self.data = data

    @classmethod
    async def from_file(cls, path: str):
        data = {}
        if os.path.exists(path):
            async with aiofiles.open(path, 'r') as f:
                lines = await f.readlines()
            for line in lines:
                key, value = line.strip().split('\t')
                data[key] = value
        return cls(path, data)
    
    def is_empty(self):
        return not bool(self.data)
    
    async def set(self, key: str, value: str):
        self.data[key] = value
        async with aiofiles.open(self.path, 'a') as f:
            await f.write(f'{key}\t{value}\n')
    
    def get(self, key: str):
        return self.data.get(key)

    def items(self):
        return self.data.items()
    
    def keys(self):
        return self.data.keys()

