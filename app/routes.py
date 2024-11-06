from flask import Blueprint, jsonify, request, render_template, send_file
from app.crawler import SheetCrawler
import requests
import io
from PIL import Image
import img2pdf

main = Blueprint('main', __name__)
crawler = SheetCrawler()

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/api/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': '请输入搜索关键词'}), 400
    
    results = crawler.search_sheets(query)
    return jsonify({'results': results})

@main.route('/api/download/<path:url>')
def download(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://www.tan8.com'
        }
        
        if not url.startswith('http'):
            url = 'http:' + url
            
        print(f"正在下载: {url}")
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"下载失败，状态码: {response.status_code}")
            return jsonify({'error': '下载失败'}), 400
            
        content_type = response.headers.get('Content-Type', '')
        if 'image' not in content_type.lower():
            print(f"非图片内容: {content_type}")
            return jsonify({'error': '下载失败：非图片内容'}), 400
            
        filename = url.split('/')[-1]
        if not filename.lower().endswith(('.jpg', '.png', '.jpeg')):
            filename = 'sheet.jpg'
            
        print(f"下载文件名: {filename}")
            
        return response.content, 200, {
            'Content-Type': response.headers.get('Content-Type', 'image/jpeg'),
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Length': str(len(response.content))
        }
    except requests.Timeout:
        print("下载超时")
        return jsonify({'error': '下载超时，请重试'}), 408
    except requests.RequestException as e:
        print(f"请求错误: {str(e)}")
        return jsonify({'error': '网络错误，请重试'}), 500
    except Exception as e:
        print(f"下载错误: {str(e)}")
        return jsonify({'error': '下载失败，请重试'}), 400

@main.route('/api/download_pdf/<path:detail_url>')
def download_pdf(detail_url):
    try:
        pdf_url = crawler.get_pdf_url(detail_url)
        if not pdf_url:
            return jsonify({'error': '获取PDF失败'}), 400
            
        # 下载PDF
        response = requests.get(pdf_url, headers=crawler.headers, timeout=15)
        
        if response.status_code != 200:
            return jsonify({'error': '下载PDF失败'}), 400
            
        # 从URL中提取文件名
        filename = pdf_url.split('/')[-1]
        
        return response.content, 200, {
            'Content-Type': 'application/pdf',
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Length': str(len(response.content))
        }
        
    except Exception as e:
        print(f"下载PDF失败: {str(e)}")
        return jsonify({'error': '下载失败'}), 500