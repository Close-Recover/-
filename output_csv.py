import pandas as pd
def standardize_time(time_str):
    """统一时间格式处理"""
    if not time_str or pd.isna(time_str):
        return None
    
    # 尝试多种常见格式
    formats = [
        '%Y/%m/%d %H:%M',    # 2025/4/2 20:37
        '%Y-%m-%d %H:%M',    # 2025-04-02 20:37
        '%Y/%m/%d',          # 2025/4/2
        '%Y-%m-%d',          # 2025-04-02
        '%m-%d',             # 04-02 (自动补充当前年)
        '%m/%d'              # 4/2 (自动补充当前年)
    ]
    
    for fmt in formats:
        try:
            dt = pd.to_datetime(time_str, format=fmt)
            # 如果是没有年份的格式，补充当前年份
            if fmt in ['%m-%d', '%m/%d']:
                dt = dt.replace(year=pd.Timestamp.now().year)
            return dt
        except:
            continue
    
    return None  # 所有格式尝试失败

def outputCSV(infoList, path):
    """统一输出CSV文件"""
    # 转换数据格式
    formatted_data = []
    for item in infoList:
        # 判断是否为muchong格式
        if isinstance(item, dict) and all(k in item for k in [0,1,2,3,4,'href']):
            formatted = {
                '标题': str(item.get(0, '')).strip(),
                '学校': str(item.get(1, '')).strip(),
                '门类/专业': str(item.get(2, '')).strip(),
                '招生人数': str(item.get(3, '')).strip(),
                '发布时间': str(item.get(4, '')).strip(),
                '链接': str(item.get('href', '')).strip()
            }
        else:
            # chinakaoyan格式
            formatted = {
                '标题': str(item.get('标题', '')).strip(),
                '学校': str(item.get('学校', '')).strip(),
                '门类/专业': str(item.get('门类/专业', '')).strip(),
                '招生人数': str(item.get('招生人数', '')).strip(),
                '发布时间': str(item.get('发布时间', '')).strip(),
                '链接': str(item.get('链接', '')).strip()
            }
        
        # 只保留有效数据
        if formatted['标题'] and formatted['学校']:
            formatted_data.append(formatted)
    
    if not formatted_data:
        print("警告：没有有效数据可保存！")
        return
    
    df = pd.DataFrame(formatted_data)
    print(f"初始数据量: {len(df)}条")
    
    # 统一列顺序并去重
    columns = ['标题', '学校', '门类/专业', '招生人数', '发布时间', '链接']
    df = df[columns].drop_duplicates(subset=['标题', '学校', '发布时间'], keep='first')
    print(f"去重后数据量: {len(df)}条")
    
    # 改进的时间处理
    df['发布时间'] = df['发布时间'].apply(standardize_time)
    df = df.dropna(subset=['发布时间']).sort_values(by='发布时间', ascending=False)
    print(f"有效时间数据量: {len(df)}条")
    
    # 保存前检查
    if len(df) == 0:
        print("警告：时间处理后无有效数据！前5条时间样本:")
        print(formatted_data[:5]['发布时间'])
        return
    
    try:
        df.to_csv(path, index=False, encoding='gbk')
        print(f'成功保存 {len(df)} 条数据至: {path}')
        # print("\n数据样例:")
        # print(df.head(3).to_string())
    except Exception as e:
        print(f'保存失败: {e}')
