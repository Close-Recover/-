import requests
from bs4 import BeautifulSoup
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote

def encode_specialties(specialties):
    """将中文专业名称转为URL编码（GBK格式）"""
    return [quote(spec.encode('gbk')) for spec in specialties]

def fetch_page_data(spec, page, year, base_url, seen):
    """获取单个页面的数据（线程任务）"""
    url = f"https://www.chinakaoyan.com/tiaoji/schoollist.shtml?issearch=1&school=&speciality={spec}&free=&area=&pagenum={page}"
    data_list = []
    
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        response.encoding = 'gbk'
        if response.status_code != 200:
            return data_list

        soup = BeautifulSoup(response.text, 'html.parser')
        for item in soup.find_all('div', class_='info-item font14'):
            try:
                school = item.find('span', class_='school').get_text(strip=True)
                name = item.find('span', class_='name').get_text(strip=True)
                title_span = item.find('span', class_='title')
                title = title_span.get_text(strip=True)
                time_str = item.find('span', class_='time').get_text(strip=True)
                
                if not time_str.startswith(year + '-'):
                    continue
                    
                relative_url = title_span.find('a')['href']
                full_url = base_url + relative_url
                
                unique_id = f"{school}|{title}|{time_str}"
                if unique_id in seen:
                    continue
                seen.add(unique_id)
                
                data_list.append({
                    '标题': title,
                    '学校': school,
                    '门类/专业': name,
                    '招生人数': None,
                    '发布时间': time_str,
                    '链接': full_url
                })
            except Exception as e:
                print(f"Error parsing item: {e}")
        time.sleep(1)  # 避免请求过快被封
    except Exception as e:
        print(f"Request error (spec={spec}, page={page}): {e}")
    
    return data_list

def get_china_kaoyan_data(specialities, year: str, scale, max_workers=5):
    """多线程获取中国考研网调剂数据"""
    base_url = "https://www.chinakaoyan.com"
    seen = set()
    data_list = []
    
    # 如果传入的是中文列表，先编码
    if not all(spec.startswith('%') for spec in specialities):
        specialities = encode_specialties(specialities)
    
    # 创建所有任务 (spec, page) 的组合
    tasks = []
    for spec in specialities:
        for page in range(1, scale):
            tasks.append((spec, page))
    
    # 使用线程池并发执行
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(fetch_page_data, spec, page, year, base_url, seen)
            for spec, page in tasks
        ]
        
        for future in as_completed(futures):
            data_list.extend(future.result())
    
    return data_list