import pandas as pd
import re
from collections import Counter
import jieba
import jieba.analyse

def analyze_tickets():
    # 读取Excel文件
    df = pd.read_excel('账单费用疑问咨询工单.xlsx')
    
    print(f"总工单数量: {len(df)}")
    print("=" * 50)
    
    # 提取用户问题
    user_questions = []
    for idx, row in df.iterrows():
        dialogue = row['工单对话']
        # 提取用户的问题部分
        user_parts = re.findall(r'用户:(.*?)(?=客服:|$)', dialogue, re.DOTALL)
        for part in user_parts:
            if part.strip() and part.strip() != '人工服务' and part.strip() != '附件':
                user_questions.append(part.strip())
    
    print(f"提取到的用户问题数量: {len(user_questions)}")
    print("=" * 50)
    
    # 分析关键词
    all_text = ' '.join(user_questions)
    
    # 使用jieba提取关键词
    keywords = jieba.analyse.extract_tags(all_text, topK=50, withWeight=True)
    print("关键词分析:")
    for word, weight in keywords:
        print(f"  {word}: {weight:.3f}")
    
    print("=" * 50)
    
    # 分类常见场景
    scenarios = {
        '费用明细查询': [],
        '小额费用疑问': [],
        '包年包月仍扣费': [],
        '资源包不生效': [],
        '欠费问题': [],
        '计费方式疑问': [],
        '产品费用疑问': [],
        '其他': []
    }
    
    # 定义关键词匹配规则
    patterns = {
        '费用明细查询': ['费用明细', '扣款明细', '账单明细', '消费明细', '费用记录', '扣款记录'],
        '小额费用疑问': ['0.1元', '0.1', '几分钱', '几毛钱', '小额', '零钱', '几分', '几毛'],
        '包年包月仍扣费': ['包年包月', '包年', '包月', '年付', '月付', '预付费', '为什么还扣费'],
        '资源包不生效': ['资源包', '流量包', '抵扣包', '优惠包', '不生效', '没扣资源包'],
        '欠费问题': ['欠费', '欠款', '余额不足', '账户余额', '充值', '续费'],
        '计费方式疑问': ['计费', '扣费', '收费', '计费方式', '按量', '按需'],
        '产品费用疑问': ['ECS', 'OSS', 'CDN', 'RDS', '云服务器', '对象存储', '负载均衡', '数据库']
    }
    
    for question in user_questions:
        matched = False
        for scenario, keywords in patterns.items():
            if any(keyword in question for keyword in keywords):
                scenarios[scenario].append(question)
                matched = True
                break
        if not matched:
            scenarios['其他'].append(question)
    
    # 输出分析结果
    print("场景分类统计:")
    for scenario, questions in scenarios.items():
        print(f"  {scenario}: {len(questions)}个问题")
        if len(questions) > 0:
            print(f"    示例问题:")
            for i, q in enumerate(questions[:3]):  # 显示前3个示例
                print(f"      {i+1}. {q[:100]}...")
            print()
    
    print("=" * 50)
    
    # 分析具体产品相关的问题
    product_keywords = {
        'ECS': ['ECS', '云服务器', '服务器', '实例'],
        'OSS': ['OSS', '对象存储', '存储'],
        'CDN': ['CDN', '内容分发', '加速'],
        'RDS': ['RDS', '数据库', 'MySQL', 'SQL'],
        '快照': ['快照', 'snapshot'],
        '安全中心': ['安全中心', '云安全'],
        '函数计算': ['函数计算', 'FC'],
        '负载均衡': ['负载均衡', 'SLB']
    }
    
    print("产品相关费用问题统计:")
    for product, keywords in product_keywords.items():
        count = sum(1 for q in user_questions if any(kw in q for kw in keywords))
        if count > 0:
            print(f"  {product}: {count}个问题")
    
    return scenarios, user_questions

if __name__ == "__main__":
    scenarios, user_questions = analyze_tickets() 