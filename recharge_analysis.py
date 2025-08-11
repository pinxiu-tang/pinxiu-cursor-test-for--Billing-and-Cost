import pandas as pd
import re
from collections import Counter
import jieba
import jieba.analyse

def extract_user_questions(dialogue):
    """提取用户问题"""
    user_parts = re.findall(r'用户:(.*?)(?=客服:|$)', dialogue, re.DOTALL)
    questions = []
    for part in user_parts:
        if part.strip() and part.strip() not in ['人工服务', '附件']:
            questions.append(part.strip())
    return questions

def extract_customer_service_response(dialogue):
    """提取客服回复"""
    cs_parts = re.findall(r'客服:(.*?)(?=用户:|$)', dialogue, re.DOTALL)
    responses = []
    for part in cs_parts:
        if part.strip():
            responses.append(part.strip())
    return responses

def classify_recharge_scenarios(questions, responses):
    """分类充值汇款场景"""
    all_text = ' '.join(questions + responses)
    
    # 定义充值汇款场景分类
    scenarios = {
        '充值方式咨询': {
            'keywords': ['充值', '付款', '支付', '汇款', '转账', '支付宝', '微信', '银行卡', '网银'],
            'patterns': [r'怎么充值', r'如何付款', r'支付方式', r'汇款方式']
        },
        '充值到账问题': {
            'keywords': ['到账', '未到账', '延迟', '多久', '时间', '确认', '收到'],
            'patterns': [r'充值.*?到账', r'未到账', r'多久.*?到账']
        },
        '充值金额问题': {
            'keywords': ['金额', '钱', '费用', '扣款', '多扣', '少扣', '不对', '错误'],
            'patterns': [r'充值.*?金额', r'扣款.*?不对', r'费用.*?错误']
        },
        '充值失败问题': {
            'keywords': ['失败', '错误', '异常', '无法', '不能', '拒绝', '退回'],
            'patterns': [r'充值.*?失败', r'支付.*?失败', r'汇款.*?失败']
        },
        '充值凭证问题': {
            'keywords': ['凭证', '发票', '收据', '证明', '截图', '记录'],
            'patterns': [r'充值.*?凭证', r'付款.*?证明', r'汇款.*?记录']
        },
        '充值限额问题': {
            'keywords': ['限额', '限制', '上限', '最大', '最小', '额度'],
            'patterns': [r'充值.*?限额', r'支付.*?限制', r'汇款.*?额度']
        },
        '充值安全咨询': {
            'keywords': ['安全', '风险', '诈骗', '被骗', '确认', '验证'],
            'patterns': [r'充值.*?安全', r'支付.*?风险', r'汇款.*?安全']
        },
        '充值退款问题': {
            'keywords': ['退款', '退回', '返还', '取消', '撤销', '退钱'],
            'patterns': [r'充值.*?退款', r'支付.*?退回', r'汇款.*?返还']
        }
    }
    
    # 计算每个场景的匹配分数
    scores = {}
    for scenario, rule in scenarios.items():
        score = 0
        # 关键词匹配
        for keyword in rule['keywords']:
            if keyword in all_text:
                score += 1
        # 模式匹配
        for pattern in rule['patterns']:
            if re.search(pattern, all_text):
                score += 2
        scores[scenario] = score
    
    # 返回得分最高的场景
    if scores:
        best_scenario = max(scores, key=scores.get)
        if scores[best_scenario] > 0:
            return best_scenario
    
    return '其他问题'

def analyze_recharge_tickets():
    """分析充值汇款工单"""
    try:
        df = pd.read_excel('充值汇款咨询工单.xlsx')
        print(f"总工单数量: {len(df)}")
        print("=" * 80)
        
        # 提取用户问题
        user_questions = []
        for idx, row in df.iterrows():
            dialogue = row['工单对话']
            questions = extract_user_questions(dialogue)
            for question in questions:
                user_questions.append(question)
        
        print(f"提取到的用户问题数量: {len(user_questions)}")
        print("=" * 80)
        
        # 分析关键词
        all_text = ' '.join(user_questions)
        keywords = jieba.analyse.extract_tags(all_text, topK=30, withWeight=True)
        print("关键词分析:")
        for word, weight in keywords:
            print(f"  {word}: {weight:.3f}")
        
        print("=" * 80)
        
        # 分类场景
        scenario_results = []
        for idx, row in df.iterrows():
            dialogue = row['工单对话']
            questions = extract_user_questions(dialogue)
            responses = extract_customer_service_response(dialogue)
            
            if questions:
                scenario = classify_recharge_scenarios(questions, responses)
                symptom = questions[0][:100] + "..." if len(questions[0]) > 100 else questions[0]
                
                result = {
                    'ticket_id': idx + 1,
                    'symptom': symptom,
                    'scenario': scenario
                }
                scenario_results.append(result)
                
                if idx < 10:
                    print(f"工单 {idx + 1}:")
                    print(f"症状: {symptom}")
                    print(f"场景: {scenario}")
                    print("-" * 80)
        
        # 统计分类结果
        scenario_stats = Counter([r['scenario'] for r in scenario_results])
        
        print("\n=== 场景分类统计结果 ===")
        for scenario, count in scenario_stats.most_common():
            print(f"  {scenario}: {count}个工单")
        
        return scenario_results, user_questions
        
    except Exception as e:
        print(f"分析过程中出现错误: {e}")
        return [], []

if __name__ == "__main__":
    results, questions = analyze_recharge_tickets() 