# -*- coding: utf-8 -*-

"""
@Project : skos_api 
@File    : __init__.py.py
@Date    : 2025/9/17 13:48:40
@Author  : luke
@Desc    : 
"""
import requests


class SkosApiBox:
    def __init__(self, base_url, auth):
        self.base_url = base_url
        self.auth = auth
        self.headers = {
            "Authorization": f"Bearer {self.auth}"
        }
        self.timeout = 15

    def health(self):
        """健康监测"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/health",
                headers=self.headers, timeout=15
            )
            res_json = response.json()
            if res_json["success"] is True:
                return True, res_json
            else:
                return False, res_json
        except Exception as e:
            return False, str(e)

    def upload_file(self, file_path, tags=None):
        """上传到skos"""
        with open(file_path, 'rb') as f:
            files = {
                'file': f,

            }
            data = {'tags': tags}
            response = requests.post(
                f"{self.base_url}/api/v1/files/upload",
                headers=self.headers, files=files, timeout=self.timeout, data=data
            )
            # print(response.text)
            res_json = response.json()
            if 'data' in res_json:
                if 'download_url' in res_json['data']:
                    res_json['data']['download_url'] = f"{self.base_url}{res_json['data']['download_url']}"
                if 'preview_url' in res_json['data']:
                    res_json['data']['preview_url'] = f"{self.base_url}{res_json['data']['preview_url']}"
            return res_json

    def search_file(self, file_name=None, upload_date=None,
                    include_tags=None, exclude_tags=None, offset=0, limit=1000):
        params = {
            'filename': file_name,
            'upload_date': upload_date,
            'include_tags': include_tags,
            'exclude_tags': exclude_tags,
            'offset': offset,
            'limit': limit
        }
        response = requests.get(
            f"{self.base_url}/api/v1/files", params=params,
            headers=self.headers, timeout=self.timeout
        )
        res_json = response.json()
        if 'data' in res_json:
            res_data = res_json['data']
            if 'items' in res_data:
                res_items = res_data['items']
                for row in res_items:
                    if 'download_url' in row:
                        row['download_url'] = f"{self.base_url}{row['download_url']}"
                    if 'preview_url' in row:
                        row['preview_url'] = f"{self.base_url}{row['preview_url']}"
        return res_json

    def search_file_by_tag(self, tags, offset=0, limit=1000):
        """通过标签查找文件"""
        params = {
            'tags': tags,
            'offset': offset,
            'limit': limit
        }
        response = requests.get(
            f"{self.base_url}/api/v1/files/search", params=params,
            headers=self.headers, timeout=self.timeout
        )
        res_json = response.json()
        if 'data' in res_json:
            res_data = res_json['data']
            if 'items' in res_data:
                res_items = res_data['items']
                for row in res_items:
                    if 'download_url' in row:
                        row['download_url'] = f"{self.base_url}{row['download_url']}"
                    if 'preview_url' in row:
                        row['preview_url'] = f"{self.base_url}{row['preview_url']}"
        return res_json

    def delete_file(self, file_id):
        """通过file_id删除文件"""
        response = requests.delete(
            f"{self.base_url}/api/v1/files/{file_id}",
            headers=self.headers, timeout=self.timeout
        )
        res_json = response.json()
        return res_json

    def file_add_tags(self, file_id, tags):
        """通过file_id添加标签"""
        json_data = {'tag_name': tags}
        response = requests.post(
            f"{self.base_url}/api/v1/files/{file_id}/tags", json=json_data,
            headers=self.headers, timeout=self.timeout
        )
        res_json = response.json()
        return res_json

    def file_delete_tags(self, file_id, tags):
        """通过file_id删除标签"""
        params = {'tags': tags}
        response = requests.delete(
            f"{self.base_url}/api/v1/files/{file_id}/tags",
            headers=self.headers, timeout=self.timeout, params=params
        )
        res_json = response.json()
        return res_json

    def tags_list(self, tag_name=None, offset=0, limit=1000):
        """查找标签信息"""
        params = {'search': tag_name, 'skip': offset, 'limit': limit}
        response = requests.get(
            f"{self.base_url}/api/v1/tags",
            headers=self.headers, timeout=self.timeout, params=params
        )
        return response.json()
