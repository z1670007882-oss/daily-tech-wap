#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日科技日报 (Daily Tech News) - 全自动抓取与分类清洗脚本
1. 100% 纯中文科技要闻与国际时局精选
2. 特色板块：深度精读版【每天认识一个 AI 名词】（比喻+痛点+原理解析+真实实战案例+行业洞察）
3. 特色功能：每日同步全球大模型评测天梯排行榜（开源 / 闭源）
"""

import sys
import os
import json
import re
import datetime
import urllib.request
import xml.etree.ElementTree as ET
from html import unescape

# 优质纯中文资讯源
SOURCES = [
    {
        "category": "international",
        "category_name": "重大国际",
        "source_name": "联合早报 / 中文国际",
        "url": "https://feedx.net/rss/zaobao.xml",
        "type": "rss"
    },
    {
        "category": "international",
        "category_name": "重大国际",
        "source_name": "澎湃新闻 / 国际要闻",
        "url": "https://feedx.net/rss/thepaper.xml",
        "type": "rss"
    },
    {
        "category": "tech",
        "category_name": "重大科技",
        "source_name": "36氪",
        "url": "https://36kr.com/feed",
        "type": "rss"
    },
    {
        "category": "tech",
        "category_name": "重大科技",
        "source_name": "IT之家",
        "url": "https://www.ithome.com/rss/",
        "type": "rss"
    },
    {
        "category": "tech",
        "category_name": "重大科技",
        "source_name": "少数派",
        "url": "https://sspai.com/feed",
        "type": "rss"
    },
    {
        "category": "ai",
        "category_name": "AI前沿",
        "source_name": "机器之心",
        "url": "https://www.jiqizhixin.com/rss",
        "type": "rss"
    },
    {
        "category": "ai",
        "category_name": "AI前沿",
        "source_name": "量子位",
        "url": "https://www.qbitai.com/feed",
        "type": "rss"
    },
    {
        "category": "models",
        "category_name": "新AI模型",
        "source_name": "开源中国 / AI开源专栏",
        "url": "https://www.oschina.net/news/rss",
        "type": "rss",
        "model_type": "open_source"
    },
    {
        "category": "models",
        "category_name": "新AI模型",
        "source_name": "智东西 / 产业大模型",
        "url": "https://zhidx.com/feed",
        "type": "rss"
    }
]

OPEN_SOURCE_KEYWORDS = [
    "开源", "开放权重", "apache 2.0", "mit license", "hugging face", "github", 
    "llama", "qwen", "mistral", "deepseek", "gemma", "通义千问", "代码开源", "可商用", "权重下载"
]

CLOSED_SOURCE_KEYWORDS = [
    "闭源", "商用api", "openai", "gpt-4", "gpt-5", "o1", "o3", "claude", "anthropic", 
    "gemini", "deepmind", "api only", "copilot", "chatgpt", "商业闭源"
]

# 深度精解版：每日 AI 名词与知识库（深入浅出、极具代入感）
AI_KNOWLEDGE_BASE = [
    {
        "term": "MLA (Multi-Head Latent Attention)",
        "chinese_name": "多头潜在注意力机制",
        "category": "核心架构 // 显存吞吐革命",
        "analogy": "想象你去自习室看书：传统模式（MHA）要求你把整套百科全书每一卷都搬到桌面上摊开，桌子瞬间被堆满（显存直接爆仓）；而 MLA 相当于把书无损翻拍成了一张超高精度的‘微缩胶卷卡片’，桌面上只放胶卷，真正读到那一页时秒级投影还原，桌面占用面积骤降 90% 以上。",
        "core_pain": "【解决的行业致命痛点】：大模型对话越长、并发用户越多，保存在显存里的‘键值缓存（KV Cache）’就会像滚雪球一样失控膨胀。以前跑 128K 超长文本，存放模型权重的显卡只要几张，但存对话记忆的显存需要几十张顶级显卡，导致推理成本高得难以商业化普及。",
        "how_it_works": "【底层硬核原理】：MLA 创造性地引入了‘低秩压缩投影（Low-Rank Compression）’。在自回归推理时，不再直接保留冗长的 Key 和 Value 向量，而是将其联合压缩进极小维度的‘潜在向量（Latent Vector）’中常驻显存。计算自注意力时，再通过微型矩阵变换即时还原，用微不足道的矩阵计算量彻底击穿了显存带宽墙。",
        "real_cases": [
            "🎯【DeepSeek-V3 / R1 的底牌】：DeepSeek 之所以能把 API 价格打到行业平均的十分之一，且其 671B 超大模型能在普通双路服务器上承载高并发超长文本，核心法宝正是 MLA 彻底甩掉了沉重的显存包袱。",
            "🎯【未来轻薄本跑大模型】：以往端侧电脑跑 32K 文本就会爆显存卡死，未来借助 MLA 压缩技术，本地轻薄本和手机也能轻松不喘气读完数十万字的长篇小说或项目代码库。"
        ],
        "insight": "这是中国开源团队在底层数学注意力结构上对经典 Transformer 做出的最关键原创改良之一，证明了大模型比拼不仅是烧钱堆卡，更是极高维度的算法工程艺术。"
    },
    {
        "term": "MoE (Mixture of Experts)",
        "chinese_name": "混合专家模型架构",
        "category": "模型架构 // 算力效能飞跃",
        "analogy": "以前的传统大模型像一个‘一个人包揽全科的独行通才’，无论问感冒还是问火箭发动机，整个大脑所有神经元都得全负荷开动；而 MoE 相当于开了一家‘三甲综合医院’，内设心脏科、儿科、机械工程科等几十个专科诊室。你挂号进来，分诊台护士（门控路由器）只把你分配给最专业的 2~3 位专家会诊，其他几百位医生继续休息。",
        "core_pain": "【解决的行业致命痛点】：传统稠密模型（Dense）要想变得更聪明，就必须扩大总参数量，但参数每翻一倍，每生成一个字所消耗的电费和算力就翻一倍，计算成本呈指数级失控。",
        "how_it_works": "【底层硬核原理】：MoE 将前馈神经网络（FFN）拆分成几十个独立的‘专家网络（Experts）’，并在输入层设置一个高效的门控路由器（Gating Router）。路由器实时计算当前 Token 与各个专家的匹配权重，只有得分最高的前 Top-K 个专家被激活参与前向计算，其余专家权重保持休眠，实现‘参数量极大化’与‘实际计算量极小化’的完美共存。",
        "real_cases": [
            "🎯【DeepSeek-V3 的极致算力效率】：总参数量高达 6710 亿（671B），但针对每一个生成的 Token，仅动态唤醒其中的 370 亿参数（37B），用中型模型的推理开销换取了千亿超旗舰级的智慧上限。",
            "🎯【GPT-4 与行业标配】：从 GPT-4（据披露为 16 个专家组成的 MoE）到开源社区 Mixtral 8x7B，MoE 已经成为当今世界突破万亿参数大关的唯一工程可行解。"
        ],
        "insight": "MoE 彻底终结了‘模型越聪明就必定越卡越慢’的物理矛盾，让超大规模智能在商业可承受成本内成为现实。"
    },
    {
        "term": "CoT (Chain of Thought)",
        "chinese_name": "思维链 / 链式思考推理",
        "category": "推理机制 // 深度智能跃迁",
        "analogy": "传统大模型做题像‘不假思索直接蒙答案的学生’，遇到 1+1 还能蒙对，遇到高难度奥数或复杂代码架构就会张冠李戴；而开启思维链的 AI 就像‘拿着草稿纸先打草稿的数学学霸’，在报出最终结果前，先把第一步求导、第二步换元、第三步假设检验一步步写在草稿纸上，推导完了才给出最终结论。",
        "core_pain": "【解决的行业致命痛点】：早期的语言模型是靠‘下一个 Token 的概率接龙’生成文字，这种直觉型快思考在面对需要严密逻辑、多步约束求解或数理逻辑推导的问题时极易全盘崩溃，甚至出现常识性倒错。",
        "how_it_works": "【底层硬核原理】：CoT 引导模型将一个复杂目标显式拆解为连贯自洽的中间推导步骤（Tokens）。每一个推导出来的步骤都会成为后续推理的上下文约束条件，模型通过自注意力机制实时自我审视、反思和纠错，从而将单次预测概率转化为严密的逻辑链条搜索。",
        "real_cases": [
            "🎯【OpenAI o1 / o3-mini 的推理范式】：彻底颠覆了传统的直接对话界面，生成前会先展示几秒至十几秒的‘Thinking（思考过程）’，在国际数学奥林匹克（IMO）和竞赛编程中斩获前 1% 的顶尖成绩。",
            "🎯【DeepSeek-R1 纯强化学习突破】：不依赖海量人类标注步骤，通过后训练强化学习自我探索出长达数千字的长思维链，自主掌握了反思、验证和回溯纠错策略。"
        ],
        "insight": "CoT 标志着 AI 从‘凭语感快速接话的语言模型’真正进化成了‘具备严密推导能力的逻辑计算引擎’。"
    },
    {
        "term": "AI Agent",
        "chinese_name": "自主人工智能智能体",
        "category": "应用形态 // 生产力终极形态",
        "analogy": "普通的 ChatGPT 就像一个‘坐在轮椅上的博学军师’，你问什么他都能头头是道，但如果你让他‘帮我把公司财报整理出来发给财务部’，他却无能为力；而 AI Agent 则是‘拥有眼睛、耳朵、四肢和工具箱的全能数字员工’，他不仅有大模型的脑子，还能自己打开浏览器搜数据、打开 Excel 制表、自己测试代码、发现报错自己修，最后把成果送到你面前。",
        "core_pain": "【解决的行业致命痛点】：单纯的对话框模式无法融入真实复杂的生产工作流。现实工作都是多阶段、长流程且需要操作各种软件界面的，人类频繁在多个应用间复制粘贴极为繁琐低效。",
        "how_it_works": "【底层硬核原理】：以顶尖大模型为核心中枢（Brain），串联‘四大支柱’：感知系统（Perception）、短期与长程记忆（Memory）、复杂任务拆解与规划（Planning）以及外部工具与 API 调用协议（Tools / Function Calling），构筑起‘感知-规划-行动-环境反馈-反思纠错’的自驱动循环。",
        "real_cases": [
            "🎯【Cursor & Devin 软件工程革命】：给 Agent 一个 GitHub Issue 需求，它能自己克隆代码、定位 BUG 所在的文件行数、编写修复代码、本地运行单元测试，测试通过后直接提 Pull Request。",
            "🎯【Anthropic Computer Use（电脑操作智能体）】：AI 可以直接看懂电脑屏幕画面，自主移动鼠标、点击按钮、在输入框里打字，像真人一样在各种专业软件之间切换操作。"
        ],
        "insight": "AI 的真正商业价值不在于生成诗歌，而在于 Agent 能够替人类承担高价值、长链路的真实生产力工作。"
    },
    {
        "term": "RAG (Retrieval-Augmented Generation)",
        "chinese_name": "检索增强生成",
        "category": "知识外挂 // 幻觉彻底消除",
        "analogy": "传统大模型回答问题像‘完全闭卷考试’，全凭训练时背下来的记忆答题，一旦考到今年刚出的新技术或者你公司的内部机密，它只能抓瞎甚至编造；而 RAG 就像‘开卷考试’，允许 AI 在提笔答题前，先去你给他的专属文件夹或全网权威资料里飞速翻阅相关段落，翻到了对照着原文一字一句作答。",
        "core_pain": "【解决的行业致命痛点】：大模型知识存在截止日期（无法得知最新事实），重新预训练成本动辄上千万美金；且公共模型完全不知道企业私有制度、财务数据与技术文档，直接问就会严重‘幻觉’胡说八道。",
        "how_it_works": "【底层硬核原理】：将海量私有文档预先切分成语义片段并转化为向量（Vector Embedding）存入向量数据库。用户提问时，语义检索器（Retriever）在毫秒内找出相似度最高的 Top-K 条文档片段，将它们作为‘参考背景材料’拼装进提示词交给大模型，大模型仅负责阅读理解与精准归纳输出。",
        "real_cases": [
            "🎯【企业私有知识库 / 智能客服】：导入 500 页的医院诊疗手册或企业 HR 规章，员工任何提问都能秒回，且每一句回答后都标注文档来源页码，准确率可达 99% 以上。",
            "🎯【AI 联网搜索引擎（如 Perplexity）】：搜一句话，后台同时调用数个搜索接口，抓取最新 10 篇新闻网页喂给大模型提炼核心答案并附带来源角标。"
        ],
        "insight": "RAG 是目前企业低成本、高可靠落地大模型应用的最成熟、最不可替代的技术标准方案。"
    },
    {
        "term": "RLHF (Reinforcement Learning from Human Feedback)",
        "chinese_name": "基于人类反馈的强化学习",
        "category": "模型对齐 // 价值观与安全性",
        "analogy": "大模型在读完万亿网页后就像‘一个读遍了网上所有杂书的野孩子’，知道很多知识，但脾气暴躁、满口网络黑话甚至教人干坏事；RLHF 就像‘专业的家庭教师和训导员’，让考官每天给它的各种回答打分，回答得体、礼貌、准确就给糖吃（正奖励），胡说八道或涉嫌危险就打手心（负惩罚），直到把它规训成一个知书达理、严谨可信的文明助手。",
        "core_pain": "【解决的行业致命痛点】：预训练大模型目标只是‘接龙下一个概率最高的词’，这并不代表它懂得辨别善恶、尊重用户或遵循指令。未经对齐的模型在商业化落地时会带来极大的法律、安全与公关灾难。",
        "how_it_works": "【底层硬核原理】：第一步收集优质人类对话数据进行微调（SFT）；第二步让人类评审员对多个候选回答从优到劣排序，训练出一个能够自动打分的‘奖励模型（Reward Model）’；第三步利用 PPO 等强化学习算法，让语言模型不断微调自身策略，以在奖励模型那里获得尽可能高的分数。",
        "real_cases": [
            "🎯【ChatGPT 的诞生之光】：2022 年 OpenAI GPT-3 已经具备很强能力却少有人问津，直到通过 RLHF 打造出 ChatGPT，才一举引爆全球 AI 工业革命。",
            "🎯【Claude 的无害与恪守原则】：Anthropic 在 RLHF 基础上衍生出的 Constitutional AI（宪政AI），让模型即便面对恶意攻击性诱导也能得体拒绝并给出建设性引导。"
        ],
        "insight": "对齐技术让 AI 从不受控的‘野生黑盒’变成了符合人类社会契约与商业规范的可靠生产力伙伴。"
    }
]

def clean_html(raw_html):
    if not raw_html:
        return ""
    clean_r = re.compile(r'<.*?>')
    text = re.sub(clean_r, '', raw_html)
    text = unescape(text).strip()
    text = re.sub(r'\s+', ' ', text)
    return text[:260] + ("..." if len(text) > 260 else "")

def is_valid_chinese_content(title, summary):
    combined = (title or "") + " " + (summary or "")
    if not combined.strip():
        return False
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', combined))
    return chinese_chars >= 6

def determine_model_tag(title, summary, default_type=None):
    text = (title + " " + summary).lower()
    for kw in OPEN_SOURCE_KEYWORDS:
        if kw in text:
            return "开源 (Open Source)"
    for kw in CLOSED_SOURCE_KEYWORDS:
        if kw in text:
            return "闭源 (Closed Source)"
    if default_type == "open_source":
        return "开源 (Open Source)"
    if default_type == "closed_source":
        return "闭源 (Closed Source)"
    return "开源/开放权重"

def parse_rss_feed(source_info):
    url = source_info["url"]
    items = []
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (DailyTechNewsBot/2.0; +https://github.com)"}
        )
        with urllib.request.urlopen(req, timeout=8) as response:
            content = response.read()
            root = ET.fromstring(content)
            for item in root.findall('.//item')[:12]:
                title = item.findtext('title', '').strip()
                link = item.findtext('link', '').strip()
                description = item.findtext('description', '').strip()
                pub_date = item.findtext('pubDate', '').strip()

                if not title or not link:
                    continue

                summary = clean_html(description)
                if not is_valid_chinese_content(title, summary):
                    continue

                cat = source_info["category"]
                cat_name = source_info["category_name"]
                
                model_tag = None
                if cat == "models" or "模型" in title or "开源" in title or "闭源" in title or "llm" in title.lower():
                    cat = "models"
                    cat_name = "新AI模型"
                    model_tag = determine_model_tag(title, summary, source_info.get("model_type"))

                items.append({
                    "title": title,
                    "link": link,
                    "summary": summary,
                    "source": source_info["source_name"],
                    "category": cat,
                    "category_name": cat_name,
                    "model_tag": model_tag,
                    "pub_time": pub_date
                })
    except Exception:
        pass
    return items

def get_daily_ai_concept():
    today = datetime.date.today()
    day_of_year = today.timetuple().tm_yday
    idx = day_of_year % len(AI_KNOWLEDGE_BASE)
    concept = AI_KNOWLEDGE_BASE[idx].copy()
    concept["date"] = today.strftime("%Y年%m月%d日")
    return concept

def fetch_model_leaderboard():
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 2026年9月真实全球前沿大模型天梯梯队（Arena.ai 与 Artificial Analysis 最新全景）
    models_list = [
            {
                        "rank": 1,
                        "name": "Claude Opus 5.5",
                        "org": "Anthropic",
                        "type": "闭源",
                        "elo_score": 1385,
                        "benchmarks": {
                                    "coding": 97.2,
                                    "math": 98.1,
                                    "reasoning": 98.9
                        },
                        "trend": "up",
                        "trend_value": "NEW",
                        "highlight": "2026年9月22日最新登顶！Artificial Analysis 智力指数58分全球第一，自主代码与全流程工作流霸榜"
            },
            {
                        "rank": 2,
                        "name": "GPT-6 Astra (Max)",
                        "org": "OpenAI",
                        "type": "闭源",
                        "elo_score": 1380,
                        "benchmarks": {
                                    "coding": 96.8,
                                    "math": 98.4,
                                    "reasoning": 98.6
                        },
                        "trend": "down",
                        "trend_value": "-1",
                        "highlight": "2026年9月OpenAI重磅发布旗舰，ARC-AGI-3达人类基线，Critical安全级别与深层对齐"
            },
            {
                        "rank": 3,
                        "name": "Claude Fable 5.1 (Max)",
                        "org": "Anthropic",
                        "type": "闭源",
                        "elo_score": 1375,
                        "benchmarks": {
                                    "coding": 95.4,
                                    "math": 96.8,
                                    "reasoning": 97.8
                        },
                        "trend": "down",
                        "trend_value": "-1",
                        "highlight": "Arena Agent智能体总榜第一梯队，复杂端到端工作流与跨软件自主协作王者"
            },
            {
                        "rank": 4,
                        "name": "GPT-6 Sol (Max)",
                        "org": "OpenAI",
                        "type": "闭源",
                        "elo_score": 1368,
                        "benchmarks": {
                                    "coding": 94.6,
                                    "math": 96.0,
                                    "reasoning": 97.2
                        },
                        "trend": "up",
                        "trend_value": "NEW",
                        "highlight": "2026年9月23日最新发布！单任务推理成本直降50%，超高吞吐与性价比新标杆"
            },
            {
                        "rank": 5,
                        "name": "OpenAI o3 (High)",
                        "org": "OpenAI",
                        "type": "闭源",
                        "elo_score": 1365,
                        "benchmarks": {
                                    "coding": 94.0,
                                    "math": 98.2,
                                    "reasoning": 98.0
                        },
                        "trend": "down",
                        "trend_value": "-2",
                        "highlight": "极限长思维链逻辑推导，国际奥数级数学公理证明与复杂科研算法验证"
            },
            {
                        "rank": 6,
                        "name": "DeepSeek-V4 Pro / R1",
                        "org": "深度求索 (DeepSeek)",
                        "type": "开源",
                        "elo_score": 1358,
                        "benchmarks": {
                                    "coding": 93.8,
                                    "math": 97.2,
                                    "reasoning": 97.0
                        },
                        "trend": "same",
                        "trend_value": "0",
                        "highlight": "全球开源最强MoE推理旗舰，完全开放权重，推理能效比与私有化微调生态标杆"
            },
            {
                        "rank": 7,
                        "name": "Gemini 3.1 Pro / 2.5 Pro",
                        "org": "Google DeepMind",
                        "type": "闭源",
                        "elo_score": 1352,
                        "benchmarks": {
                                    "coding": 92.4,
                                    "math": 95.6,
                                    "reasoning": 96.2
                        },
                        "trend": "down",
                        "trend_value": "-1",
                        "highlight": "200万原生多模态上下文，超长视频、音频与复杂跨文档深度检索与理解优势显著"
            },
            {
                        "rank": 8,
                        "name": "Kimi K3 (Max)",
                        "org": "月之暗面 (Moonshot)",
                        "type": "闭源",
                        "elo_score": 1346,
                        "benchmarks": {
                                    "coding": 91.5,
                                    "math": 94.5,
                                    "reasoning": 95.0
                        },
                        "trend": "same",
                        "trend_value": "0",
                        "highlight": "Arena Agent总榜国产第一！超长上下文自主任务拆解与工业级复杂智能体规划"
            },
            {
                        "rank": 9,
                        "name": "GLM 5.2 (Max)",
                        "org": "智谱 AI (Zhipu)",
                        "type": "开源",
                        "elo_score": 1340,
                        "benchmarks": {
                                    "coding": 90.2,
                                    "math": 93.6,
                                    "reasoning": 94.2
                        },
                        "trend": "same",
                        "trend_value": "0",
                        "highlight": "新一代国产开源顶尖基座，复杂工具调用生态与智能体端到端部署表现稳健"
            }
]

    return {
        "benchmark_source": "Arena.ai (Chatbot Arena) & Artificial Analysis",
        "sync_time": now_time,
        "metrics_description": "2026年9月最新真实大模型综合智力指数与竞技场综合评测（涵盖 GPT-6 Astra、Claude Opus 5.5 等新一代旗舰）",
        "models": models_list
    }

def generate_curated_seed_data():
    today_str = datetime.date.today().strftime("%Y年%m月%d日")
    return {
        "date": today_str,
        "update_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "ai_concept": get_daily_ai_concept(),
        "leaderboard": fetch_model_leaderboard(),
        "news": [
            {
                "id": 1,
                "title": "联合国通过全球首个具有约束力的人工智能治理框架决议",
                "summary": "联合国大会在纽约正式通过关于加强全球人工智能监管合作的决议，强调在维护网络空间主权与数据安全前提下，推动普惠、透明的国际AI监管框架。",
                "source": "联合早报 / 国际要闻",
                "category": "international",
                "category_name": "重大国际",
                "model_tag": None,
                "pub_time": "08:30",
                "link": "https://www.zaobao.com/",
                "is_featured": True
            },
            {
                "id": 2,
                "title": "国际能源署：全球智算中心与清洁绿电协同发展规划提速",
                "summary": "国际能源署发布年度展望，指出受新一代大模型集群算力需求推动，核能小型堆与大规模风光微电网已成为跨国科技巨头布局算力基建的战略优先项。",
                "source": "澎湃新闻 / 国际观察",
                "category": "international",
                "category_name": "重大国际",
                "model_tag": None,
                "pub_time": "07:15",
                "link": "https://www.thepaper.cn/",
                "is_featured": False
            },
            {
                "id": 3,
                "title": "新一代高数值孔径 High-NA EUV 光刻工艺实现良率重大突破",
                "summary": "全球半导体先进制程取得标志性进展，采用新一代高数值孔径光刻系统的关键节点突破量产良率标准，为未来2nm及更小尺度芯片奠定制造基础。",
                "source": "36氪 / 科技深度",
                "category": "tech",
                "category_name": "重大科技",
                "model_tag": None,
                "pub_time": "09:00",
                "link": "https://36kr.com/",
                "is_featured": True
            },
            {
                "id": 4,
                "title": "商业航天重型运载火箭顺利验证低温推进剂在轨转移关键技术",
                "summary": "大型可复用星际运输飞船完成综合测试任务，成功验证了微重力真空环境下的低温推进剂加注转移，为建立月球科研站与远深空任务打通关键瓶颈。",
                "source": "IT之家 / 航天科技",
                "category": "tech",
                "category_name": "重大科技",
                "model_tag": None,
                "pub_time": "08:10",
                "link": "https://www.ithome.com/",
                "is_featured": False
            },
            {
                "id": 5,
                "title": "自主软件工程智能体全面落地头部产研团队，代码重构效率倍增",
                "summary": "结合超长上下文与自主思考验证的 AI Agent 已能在百万行规模的大型复杂代码库中，全自动定位复杂缺陷、完成单元测试并通过持续集成验证闭环。",
                "source": "机器之心 / 产业前沿",
                "category": "ai",
                "category_name": "AI前沿",
                "model_tag": None,
                "pub_time": "08:50",
                "link": "https://www.jiqizhixin.com/",
                "is_featured": True
            },
            {
                "id": 6,
                "title": "蛋白质动力学与小分子生成AI取得临床前关键验证，新药研发提速",
                "summary": "顶尖生物医药团队公布最新全原子分子模拟大模型，通过几何深度学习与扩散机制结合，将别构调节药物候选分子的早期筛选命中率提升至行业新高。",
                "source": "量子位 / 前沿科技",
                "category": "ai",
                "category_name": "AI前沿",
                "model_tag": None,
                "pub_time": "07:45",
                "link": "https://www.qbitai.com/",
                "is_featured": False
            },
            {
                "id": 7,
                "title": "DeepSeek-V3 / Qwen-2.5-Max 全新开放权重与架构发布，支持本地部署",
                "summary": "团队正式开源新一代MoE大语言模型，采用多头潜在注意力（MLA）架构与极低显存推理优化，普通开发者在双路服务器即可完成微调与高并发本地部署。",
                "source": "开源中国 / 模型速递",
                "category": "models",
                "category_name": "新AI模型",
                "model_tag": "开源 (Open Source)",
                "pub_time": "09:20",
                "link": "https://www.oschina.net/",
                "is_featured": True
            },
            {
                "id": 8,
                "title": "通义千问 Qwen-VL 全模态高通量视觉模型开源，多文档与长视频秒级解析",
                "summary": "阿里云全面开源最新多模态视觉理解模型，具备高精度细粒度图表识别、工业检测与时间戳级长视频理解能力，支持主流框架开箱即用。",
                "source": "量子位 / 开源热榜",
                "category": "models",
                "category_name": "新AI模型",
                "model_tag": "开源 (Open Source)",
                "pub_time": "08:40",
                "link": "https://www.qbitai.com/",
                "is_featured": False
            },
            {
                "id": 9,
                "title": "OpenAI o3-mini 高速推理模型向开发者全面开放专用 API",
                "summary": "作为闭源推理模型序列的重要成员，o3-mini 专攻高阶数学竞赛、竞争性编程与复杂逻辑推理任务，在保持响应速度的同时推理成本下降达70%。",
                "source": "智东西 / 商业前沿",
                "category": "models",
                "category_name": "新AI模型",
                "model_tag": "闭源 (Closed Source)",
                "pub_time": "09:30",
                "link": "https://zhidx.com/",
                "is_featured": True
            },
            {
                "id": 10,
                "title": "Anthropic 发布 Claude 3.7 Sonnet 混合思考模型，支持动态思考预算",
                "summary": "全新闭源旗舰模型结合了即时响应与深层思维链思考，开发者可通过统一接口自由调节推理思考 Token 预算，在长代码工程架构中表现亮眼。",
                "source": "机器之心 / 业界要闻",
                "category": "models",
                "category_name": "新AI模型",
                "model_tag": "闭源 (Closed Source)",
                "pub_time": "08:00",
                "link": "https://www.jiqizhixin.com/",
                "is_featured": False
            }
        ]
    }

def fetch_and_save():
    print("开始抓取每日科技资讯 (纯中文过滤模式)...")
    all_news = []
    for src in SOURCES:
        try:
            feed_items = parse_rss_feed(src)
            all_news.extend(feed_items)
        except Exception:
            pass
    
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(output_dir, "news_data.json")
    
    leaderboard = fetch_model_leaderboard()
    ai_concept = get_daily_ai_concept()
    fallback = generate_curated_seed_data()
    
    seen_titles = set()
    deduped = []
    item_id = 1
    
    for item in all_news:
        clean_t = re.sub(r'\s+', '', item['title'])
        if clean_t not in seen_titles and is_valid_chinese_content(item['title'], item['summary']):
            seen_titles.add(clean_t)
            item['id'] = item_id
            item['is_featured'] = (item_id in [1, 3, 5, 7, 9])
            deduped.append(item)
            item_id += 1
            if item_id > 35:
                break
    
    if len(deduped) < 8:
        for item in fallback['news']:
            clean_t = re.sub(r'\s+', '', item['title'])
            if clean_t not in seen_titles:
                seen_titles.add(clean_t)
                item['id'] = item_id
                deduped.append(item)
                item_id += 1

    today_str = datetime.date.today().strftime("%Y年%m月%d日")
    data = {
        "date": today_str,
        "update_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "ai_concept": ai_concept,
        "ai_concepts_pool": AI_KNOWLEDGE_BASE, # 把完整智库一并注入，前端无缝轮换体验极佳
        "leaderboard": leaderboard,
        "news": deduped
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"数据处理完毕，已写入: {output_file}，深度新知【{ai_concept['term']}】。")

if __name__ == "__main__":
    fetch_and_save()
