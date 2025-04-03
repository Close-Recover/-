import os
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import filecmp

def compare_and_send_email(path, comp_path, recipient='xxx@qq.com'):
    """
    比较两个CSV文件，处理差异并发送邮件
    
    参数:
        path: 新生成的临时文件路径
        comp_path: 要比较的基准文件路径
        recipient: 收件人邮箱
    """
    # 获取当前时间（精确到分钟）
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M")
    
    # 初始化邮件信息
    msg = MIMEMultipart()
    msg['From'] = 'xxx@qq.com'  # 替换为你的发件邮箱
    msg['To'] = recipient
    msg['Subject'] = '调剂信息汇总'
    
    # 检查文件是否存在
    if not os.path.exists(path):
        print(f"错误：临时文件 {path} 不存在")
        return
        
    # 基准文件不存在的情况（首次运行）
    if not os.path.exists(comp_path):
        new_filename = f'./cs_enroll_adjustment_{current_time}.csv'
        os.rename(path, new_filename)
        convert_to_excel(new_filename)
        
        msg.attach(MIMEText(f"拉取时间：{current_time}\n首次生成数据文件，具体内容见于附件", 'plain'))
        attach_file(msg, new_filename.replace('.csv', '.xlsx'))
        send_email(msg)
        return
    
    # 比较文件内容
    if is_file_content_same(path, comp_path):
        msg.attach(MIMEText(f"拉取时间：{current_time}\n当前数据无更新", 'plain'))
    else:
        # 生成带时间戳的新文件名
        new_filename = f'./cs_enroll_adjustment_{current_time}.csv'
        
        # 文件重命名
        os.rename(path, new_filename)
        
        # 转换为Excel
        excel_path = convert_to_excel(new_filename)
        
        # 准备邮件内容
        msg.attach(MIMEText(f"拉取时间：{current_time}\n当前数据有更新，新版本见于附件", 'plain'))
        attach_file(msg, excel_path)
    
    # 发送邮件
    send_email(msg)

def is_file_content_same(file1, file2):
    """比较两个CSV文件内容是否相同（忽略行尾和空行差异）"""
    try:
        # 使用pandas比较内容（更可靠）
        df1 = pd.read_csv(file1, encoding='gbk')
        df2 = pd.read_csv(file2, encoding='gbk')
        return df1.equals(df2)
    except:
        # 回退到文件比较
        return filecmp.cmp(file1, file2, shallow=False)

def convert_to_excel(csv_path):
    """将CSV转换为Excel文件"""
    excel_path = csv_path.replace('.csv', '.xlsx')
    try:
        df = pd.read_csv(csv_path, encoding='gbk')
        df.to_excel(excel_path, index=False, engine='openpyxl')
        print(f"已生成Excel文件: {excel_path}")
        return excel_path
    except Exception as e:
        print(f"Excel转换失败: {e}")
        return None

def attach_file(msg, filepath):
    """添加附件到邮件"""
    if not os.path.exists(filepath):
        print(f"附件文件不存在: {filepath}")
        return
        
    with open(filepath, 'rb') as f:
        part = MIMEApplication(f.read())
        part.add_header('Content-Disposition', 'attachment', 
                       filename=os.path.basename(filepath))
        msg.attach(part)

def send_email(msg):
    """发送邮件"""
    try:
        # 配置SMTP服务器（以QQ邮箱为例）
        smtp_server = 'smtp.qq.com'
        port = 465
        username = 'xxx@qq.com'  # 替换为你的邮箱
        password = 'xxxx'  # 替换为邮箱授权码
        
        # 创建安全连接
        server = smtplib.SMTP_SSL(smtp_server, port)
        server.login(username, password)
        
        # 发送邮件
        server.send_message(msg)
        server.quit()
        print("邮件发送成功")
    except Exception as e:
        print(f"邮件发送失败: {e}")