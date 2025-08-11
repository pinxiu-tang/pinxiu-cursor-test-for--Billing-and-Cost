import pandas as pd
import re
from collections import Counter
import jieba
import jieba.analyse

def analyze_billing_rules_tickets():
    """分析计费规则咨询工单"""
    # 读取Excel文件
    df = pd.read_excel('计费规则咨询工单.xlsx')
    
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
    
    # 计费规则相关场景分类
    scenarios = {
        '计费方式理解': [],
        '计费周期疑问': [],
        '计费标准咨询': [],
        '计费规则变更': [],
        '计费计算方式': [],
        '计费优惠政策': [],
        '计费异常处理': [],
        '计费文档查询': [],
        '其他': []
    }
    
    # 定义关键词匹配规则
    patterns = {
        '计费方式理解': ['计费方式', '如何计费', '怎么计费', '计费模式', '按量计费', '包年包月', '预付费', '后付费'],
        '计费周期疑问': ['计费周期', '计费时间', '什么时候扣费', '扣费时间', '账单周期', '计费日期'],
        '计费标准咨询': ['计费标准', '收费标准', '价格', '费用标准', '计费规则', '收费规则'],
        '计费规则变更': ['规则变更', '政策变更', '计费调整', '价格调整', '新规则', '变更通知'],
        '计费计算方式': ['计算方式', '如何计算', '计算公式', '计费算法', '费用计算'],
        '计费优惠政策': ['优惠', '折扣', '促销', '活动', '免费额度', '优惠券'],
        '计费异常处理': ['异常', '错误', '问题', '故障', 'bug', '计费错误'],
        '计费文档查询': ['文档', '说明', '帮助', '指南', '手册', 'FAQ']
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
    print("计费规则咨询场景分类统计:")
    for scenario, questions in scenarios.items():
        print(f"  {scenario}: {len(questions)}个问题")
        if len(questions) > 0:
            print(f"    示例问题:")
            for i, q in enumerate(questions[:3]):  # 显示前3个示例
                print(f"      {i+1}. {q[:100]}...")
            print()
    
    print("=" * 50)
    
    # 分析具体产品相关的计费规则问题
    product_keywords = {
        'ECS': ['ECS', '云服务器', '服务器', '实例'],
        'OSS': ['OSS', '对象存储', '存储'],
        'CDN': ['CDN', '内容分发', '加速'],
        'RDS': ['RDS', '数据库', 'MySQL', 'SQL'],
        '快照': ['快照', 'snapshot'],
        '安全中心': ['安全中心', '云安全'],
        '函数计算': ['函数计算', 'FC'],
        '负载均衡': ['负载均衡', 'SLB'],
        '弹性IP': ['弹性IP', 'EIP'],
        '云监控': ['云监控', '监控']
    }
    
    print("产品相关计费规则问题统计:")
    for product, keywords in product_keywords.items():
        count = sum(1 for q in user_questions if any(kw in q for kw in keywords))
        if count > 0:
            print(f"  {product}: {count}个问题")
    
    print("=" * 50)
    
    # 分析用户情绪和紧急程度
    urgency_keywords = {
        '紧急': ['紧急', '急', '马上', '立即', '现在', '今天'],
        '疑问': ['为什么', '怎么', '如何', '什么', '哪里'],
        '投诉': ['投诉', '不满', '不合理', '错误', '问题'],
        '咨询': ['咨询', '了解', '询问', '请问', '麻烦']
    }
    
    print("用户情绪和紧急程度分析:")
    for emotion, keywords in urgency_keywords.items():
        count = sum(1 for q in user_questions if any(kw in q for kw in keywords))
        if count > 0:
            print(f"  {emotion}: {count}个问题")
    
    return scenarios, user_questions, keywords

if __name__ == "__main__":
    scenarios, user_questions, keywords = analyze_billing_rules_tickets() 