# -*- coding: utf-8 -*-
import time
from get_muchong import getPages, parameters, threadingUp
from get_chinakaoyan import get_china_kaoyan_data
from output_csv import outputCSV
from post_service import compare_and_send_email

def main():
    path = './tmp.csv'
    comp_path = './cs_enroll_adjustment_2025-4-2.csv'
    Year: str = '2025'
    
    # 抓取muchong数据
    muchong_data = []
    base_url = 'http://muchong.com/bbs/kaoyan.php?'
    pre_params = ['r1%5B%5D=', 'r2%5B%5D=', 'r3%5B%5D=', 'year=']
    params = parameters(pro_='08', pro_1='0812', year=Year)
    pages, target_url = getPages(base_url, pre_params, *params)
    
    print(f"开始抓取muchong数据，共{pages}页...")
    start_time = time.time()
    threadingUp(10, muchong_data, pages, target_url)  # 10个线程
    
    chinese_specialities = [
        '计算机',
        '软件',
        '物联网',
        '信息',
        '安全'
    ]
    max_page = 5 # 获取数据的范围，一般5页足够获取当年的数据
    scale = max_page + 1
    # 抓取chinakaoyan数据
    print("开始抓取chinakaoyan数据...")

    chinakaoyan_data = get_china_kaoyan_data(chinese_specialities, Year, scale, max_workers=8)
    
    # 合并数据
    all_data = muchong_data + chinakaoyan_data
    print(f"共抓取{len(all_data)}条数据，其中muchong {len(muchong_data)}条，chinakaoyan {len(chinakaoyan_data)}条")
    
    # 输出结果
    outputCSV(all_data, path)
    print(f"总耗时: {time.time()-start_time:.2f}秒")

    # compare_and_send_email(path, comp_path)


if __name__ == "__main__":
    main()