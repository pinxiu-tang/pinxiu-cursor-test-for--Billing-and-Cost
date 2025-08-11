import pandas as pd
import re
from collections import Counter

# 读取数据
df = pd.read_excel('账单费用疑问咨询工单.xlsx')
print(f"总工单数量: {len(df)}")

# 分析前10个工单
for i in range(min(10, len(df))):
    dialogue = df.iloc[i]['工单对话']
    
    # 提取用户问题
    user_parts = re.findall(r'用户:(.*?)(?=客服:|$)', dialogue, re.DOTALL)
    questions = [part.strip() for part in user_parts if part.strip() and part.strip() not in ['人工服务', '附件']]
    
    # 提取客服回复
    cs_parts = re.findall(r'客服:(.*?)(?=用户:|$)', dialogue, re.DOTALL)
    responses = [part.strip() for part in cs_parts if part.strip()]
    
    if questions:
        print(f"\n=== 工单 {i+1} ===")
        print(f"用户问题: {questions[0][:200]}...")
        
        # 简单的关键词分析
        all_text = ' '.join(questions + responses)
        
        # 判断场景
        if '包年包月' in all_text and ('扣费' in all_text or '费用' in all_text):
            scenario = 'C1.1: 包年包月资源的关联按量费用'
            root_cause = "用户购买了包年包月资源，但未意识到关联的按量计费组件仍在产生费用。"
        elif '免费' in all_text and ('到期' in all_text or '超出' in all_text):
            scenario = 'C1.2: 免费额度规则误解'
            root_cause = "用户误以为服务完全免费，但实际上已超出免费额度或试用期。"
        elif '释放' in all_text and ('忘记' in all_text or '遗漏' in all_text):
            scenario = 'C2.1: 残留/孤立资源计费'
            root_cause = "用户释放了主资源，但遗漏了关联的独立计费资源。"
        elif '停止' in all_text and '未释放' in all_text:
            scenario = 'C2.2: "停止"非"释放"'
            root_cause = "用户仅停止了实例但未释放资源，导致基础资源仍在计费。"
        elif '自动续费' in all_text or '续费' in all_text:
            scenario = 'C2.3: 自动续费未关闭'
            root_cause = "用户未关闭自动续费功能，资源到期后自动续费产生费用。"
        elif '资源包' in all_text and ('不匹配' in all_text or '没扣' in all_text):
            scenario = 'C4.1: 资源包规格不匹配'
            root_cause = "购买的资源包与实际使用的资源规格不匹配，无法抵扣费用。"
        elif '资源包' in all_text and ('用完' in all_text or '过期' in all_text):
            scenario = 'C4.2: 资源包用尽/过期'
            root_cause = "资源包额度已用完或已过期，超出部分转为按量付费。"
        else:
            scenario = 'C5.1: 账号与权限问题'
            root_cause = "需要进一步分析确定具体原因。"
        
        print(f"场景分类: {scenario}")
        print(f"根本原因: {root_cause}")
        print("-" * 80)

print("\n=== 分析完成 ===") 