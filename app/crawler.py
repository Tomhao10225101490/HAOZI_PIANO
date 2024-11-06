import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import time
import random
import re
import json

class SheetCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://www.tan8.com'
        }
        self.base_url = "https://www.tan8.com"
        
    def search_sheets(self, query: str) -> List[Dict]:
        """
        搜索钢琴乐谱
        """
        try:
            url = f"{self.base_url}/search-1-1-0.php?keyword={requests.utils.quote(query)}"
            print(f"搜索URL: {url}")
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                print(f"请求失败: {response.status_code}")
                return []
            
            print(f"页面内容长度: {len(response.text)}")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # 查找所有乐谱项
            sheet_items = soup.select('.yuepuClassify_list_0422 li')
            print(f"找到 {len(sheet_items)} 个乐谱项")
            
            for item in sheet_items:
                try:
                    # 提取标题和链接
                    title_elem = item.select_one('.title_color')
                    if not title_elem:
                        continue
                        
                    # 移除序号和VIP标记
                    title = title_elem.text.strip()
                    title = title.split('.', 1)[-1].strip()
                    title = title.split('[')[0].strip()
                    
                    # 获取详情页链接
                    link_elem = item.find_parent('a')
                    if not link_elem:
                        continue
                    detail_url = self.base_url + link_elem.get('href', '')
                    
                    # 提取预览图
                    img_elem = item.select_one('.img img')
                    if not img_elem:
                        continue
                        
                    preview_url = img_elem.get('src', '')
                    if not preview_url.startswith('http'):
                        if preview_url.startswith('//'):
                            preview_url = 'https:' + preview_url
                        elif preview_url.startswith('/'):
                            preview_url = self.base_url + preview_url
                        else:
                            preview_url = f"{self.base_url}/{preview_url}"
                    
                    # 提取作者信息
                    composer = "未知"
                    composer_elem = item.select_one('.brief_color span')
                    if composer_elem:
                        composer = composer_elem.text.strip()
                    
                    # 使用预览图作为下载图片
                    download_url = preview_url
                    
                    # 获取乐谱图片
                    detail_response = requests.get(detail_url, headers=self.headers, timeout=10)
                    detail_response.encoding = 'utf-8'
                    
                    if detail_response.status_code != 200:
                        print(f"获取详情失败: {detail_response.status_code}")
                        continue
                    
                    detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
                    script_tags = detail_soup.find_all('script')

                    # 存储所有页面的URL
                    sheet_urls = []

                    # 首先尝试获取五线谱
                    for script in script_tags:
                        script_text = script.string
                        if script_text and 'yuepuArrXian' in script_text:
                            try:
                                xian_urls = re.findall(r'yuepuArrXian = \[(.*?)\];', script_text, re.S)[0]
                                xian_data = json.loads(f"[{xian_urls}]")
                                if xian_data and xian_data[0].get('img'):
                                    sheet_urls = xian_data[0]['img']
                                    # 确保所有URL都是完整的
                                    sheet_urls = ['https:' + url if not url.startswith('http') else url for url in sheet_urls]
                                    break
                            except Exception as e:
                                print(f"解析五线谱URL失败: {str(e)}")
                                continue

                    # 如果没有找到五线谱，尝试获取简谱
                    if not sheet_urls:
                        for script in script_tags:
                            script_text = script.string
                            if script_text and 'yuepuArrJian' in script_text:
                                try:
                                    jian_urls = re.findall(r'yuepuArrJian = \[(.*?)\];', script_text, re.S)[0]
                                    jian_data = json.loads(f"[{jian_urls}]")
                                    if jian_data and jian_data[0].get('img'):
                                        sheet_urls = jian_data[0]['img']
                                        # 确保所有URL都是完整的
                                        sheet_urls = ['https:' + url if not url.startswith('http') else url for url in sheet_urls]
                                        break
                                except Exception as e:
                                    print(f"解析简谱URL失败: {str(e)}")
                                    continue

                    # 使用第一页作为预览，所有页面URL存储在download_urls中
                    download_url = sheet_urls[0] if sheet_urls else preview_url
                    download_urls = sheet_urls if sheet_urls else [preview_url]

                    results.append({
                        'title': title,
                        'composer': composer,
                        'preview_url': preview_url,
                        'download_url': download_url,
                        'download_urls': download_urls,  # 添加所有页面的URL
                        'detail_url': detail_url,
                        'page_count': len(download_urls)  # 添加页面总数
                    })
                    
                    print(f"添加结果: {title}")
                    time.sleep(random.uniform(0.2, 0.5))
                    
                except Exception as e:
                    print(f"解析乐谱项时出错: {str(e)}")
                    continue
                    
                if len(results) >= 10:
                    break
            
            print(f"总共找到 {len(results)} 个结果")
            return results
            
        except Exception as e:
            print(f"爬虫错误: {str(e)}")
            return []

    def get_sheet_detail(self, url: str) -> Dict:
        """
        获取乐谱详情
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                return None
                
            soup = BeautifulSoup(response.text, 'html.parser')
            img_elem = soup.select_one('.showpianoScore img')
            
            if img_elem:
                img_url = img_elem.get('src', '')
                if not img_url.startswith('http'):
                    img_url = self.base_url + img_url
                return {'download_url': img_url}
            
            return None
            
        except Exception as e:
            print(f"获取详情错误: {str(e)}")
            return None