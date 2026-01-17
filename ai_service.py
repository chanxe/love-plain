import requests
import os
import random
from datetime import date, datetime, timedelta
# Import inside functions to avoid circular import

class LoveOneDayService:
    
    @staticmethod
    def collect_daily_data():
        """收集今日播报所需的数据"""
        # Import here to avoid circular import
        from app import app, db, Anniversary, Moment
        today = date.today()
        
        # Use app context to query the database
        with app.app_context():
            # 检查今天是否是纪念日
            # Use extract function to get day and month from the date column
            today_anniversaries = Anniversary.query.filter(
                db.extract('day', Anniversary.date) == today.day,
                db.extract('month', Anniversary.date) == today.month
            ).all()
            
            # 检查往年当天是否有超过3条日常
            historical_moments = []
            for year in range(2020, today.year):  # 假设从2020年开始有数据
                try:
                    historical_date = date(year, today.month, today.day)
                    moments_on_date = Moment.query.filter(
                        db.extract('day', Moment.timestamp) == historical_date.day,
                        db.extract('month', Moment.timestamp) == historical_date.month
                    ).all()
                    
                    if len(moments_on_date) >= 3:
                        historical_moments.extend(moments_on_date)
                except ValueError:
                    # 忽略无效日期（如2月29日）
                    continue
            
            # 获取最近的动态（过去3天内）
            three_days_ago = datetime.now() - timedelta(days=3)
            recent_moments = Moment.query.filter(
                Moment.timestamp >= three_days_ago
            ).order_by(Moment.timestamp.desc()).limit(10).all()
        
        return {
            'today': today,
            'today_anniversaries': today_anniversaries,
            'historical_moments': historical_moments,
            'recent_moments': recent_moments
        }
    
    @staticmethod
    def get_historical_events(month, day):
        """获取历史上今天发生的有趣事件"""
        # 这里可以连接历史事件API或使用预定义的历史事件数据
        # 作为示例，提供一些常见历史事件
        historical_events_map = {
            (1, 1): [
                "1970年 - 第一个Unix纪元时间开始",
                "1999年 - 澳大利亚首都领地成为世界上第一个承认同性婚姻的地区之一"
            ],
            (2, 14): [
                "140岁以上 - 圣瓦伦丁节被宣布为正式节日",
                "1953年 - DNA双螺旋结构被发现"
            ],
            (6, 1): [
                "1910年 - 英国国王乔治五世加冕",
                "1940年 - 法国向德国投降"
            ]
        }
        
        events = historical_events_map.get((month, day), [
            f"在{month}月{day}日，历史上曾发生过许多重要的事件",
            f"{month}月{day}日是特殊的日子，见证了许多历史时刻",
            f"你知道吗？在{month}月{day}日，历史上发生过不少有趣的事情"
        ])
        
        return random.choice(events)
    
    @staticmethod
    def call_bailian_api(prompt, system_prompt=None):
        """调用阿里百炼API"""
        import time
        api_key = os.getenv('BAILIAN_API_KEY')
        # Using the DashScope API endpoint for Qwen models
        endpoint = os.getenv('BAILIAN_ENDPOINT', 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions')
        
        if not api_key:
            raise ValueError("BAILIAN_API_KEY not configured in environment variables")
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "model": os.getenv('BAILIAN_MODEL', 'qwen-max'),
            "messages": [
                {"role": "system", "content": system_prompt or "你是一个浪漫甜蜜的助手，专门为情侣生成纪念日播报。语气要非常温柔、甜蜜，多用emoji，让情侣感受到浓浓的爱意。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": float(os.getenv('BAILIAN_TEMPERATURE', '0.7')),
            "max_tokens": 450,
            "top_p": 0.9
        }
        
        # Retry logic with exponential backoff
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Add timeout for the request
                response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
                
                if response.status_code == 429:  # Rate limited
                    wait_time = (2 ** attempt) + 1  # Exponential backoff
                    print(f"Rate limited, waiting {wait_time}s before retry {attempt + 1}/{max_retries}")
                    time.sleep(wait_time)
                    continue
                elif response.status_code >= 400:
                    print(f"BaiLian API Error {response.status_code}: {response.text}")
                    if attempt == max_retries - 1:  # Last attempt
                        response.raise_for_status()
                    continue
                
                response.raise_for_status()
                result = response.json()
                
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content'].strip()
                    content_length = len(content)
                    
                    if content_length > 350:
                        print(f"Warning: Generated content length ({content_length}) exceeds recommended limit (350)")
                    elif content_length < 150:
                        print(f"Warning: Generated content length ({content_length}) is below recommended minimum (150)")
                    
                    return content
                else:
                    raise Exception(f"Unexpected API response format: {result}")
                    
            except requests.exceptions.Timeout:
                print(f"BaiLian API Request Timeout (attempt {attempt + 1}/{max_retries})")
                if attempt == max_retries - 1:
                    raise
            except requests.exceptions.RequestException as e:
                print(f"BaiLian API Request Error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    raise
            except Exception as e:
                print(f"BaiLian API Error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    raise
            # Wait before retrying
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
    
    @staticmethod
    def generate_love_broadcast(data):
        """生成爱的一天智能播报"""
        today = data['today']
        
        # 判断播报类型
        if data['today_anniversaries']:
            # 纪念日模式
            return LoveOneDayService._generate_anniversary_broadcast(data, today)
        elif data['historical_moments']:
            # 历史日常模式
            return LoveOneDayService._generate_historical_moments_broadcast(data, today)
        else:
            # 历史趣事模式
            return LoveOneDayService._generate_historical_events_broadcast(data, today)
    
    @staticmethod
    def _generate_anniversary_broadcast(data, today):
        """生成纪念日模式播报"""
        ann_titles = [ann.title for ann in data['today_anniversaries']]
        
        prompt = f"""
请以非常甜蜜、浪漫的语气，为情侣生成一份纪念日专属播报。

今天是{today.strftime('%Y年%m月%d日')}，同时也是{'和'.join(ann_titles)}！

请生成一段充满爱意的播报内容，包含：
1. 温馨甜蜜的节日祝贺
2. 对情侣关系的美好祝愿
3. 一些建议如何庆祝这个特殊的日子
4. 表达深深的爱意和关怀

语气要非常浪漫、温暖，让情侣感受到满满的爱意。适当加入一些emoji表达情感。

【重要要求】生成的播报内容必须严格控制在200-300字之间，确保内容完整、逻辑清晰、表达流畅，不要因为字数限制而截断句子或导致语义不完整。
"""
        
        system_prompt = "你是一个浪漫甜蜜的助手，专门为情侣生成纪念日播报。语气要非常温柔、甜蜜，多用emoji，让情侣感受到浓浓的爱意。所有回复必须严格控制在200-300字之间。"
        
        try:
            return LoveOneDayService.call_bailian_api(prompt, system_prompt)
        except Exception as e:
            print(f"BaiLian API Error: {e}")
            return LoveOneDayService._generate_fallback_anniversary_broadcast(data, today)
    
    @staticmethod
    def _generate_historical_moments_broadcast(data, today):
        """生成历史日常模式播报"""
        # 选择一些历史日常内容用于播报
        selected_moments = data['historical_moments'][:5]  # 选择前5条
        moment_summaries = []
        for moment in selected_moments:
            moment_summaries.append(f"{moment.user.name}曾说过：{moment.content[:100]}")
        
        prompt = f"""
请以温馨怀旧的语气，为情侣生成一份回顾往年今日美好时光的播报。

今天是{today.strftime('%Y年%m月%d日')}。

在往年今天的回忆中，你们留下了这些美好瞬间：
{chr(10).join(moment_summaries)}

请生成一段温馨的播报内容，包含：
1. 对过往美好时光的怀念
2. 对现在幸福生活的感恩
3. 对未来的美好憧憬
4. 表达对彼此的深深爱意

语气要温暖怀旧，让情侣回忆起那些珍贵的时刻。适当加入一些emoji表达情感。

【重要要求】生成的播报内容必须严格控制在200-300字之间，确保内容完整、逻辑清晰、表达流畅，不要因为字数限制而截断句子或导致语义不完整。
"""
        
        system_prompt = "你是一个温暖怀旧的助手，专门为情侣回顾往昔美好时光。语气要温馨感人，多用emoji，让情侣感受到时间的美好和爱情的珍贵。所有回复必须严格控制在200-300字之间。"
        
        try:
            return LoveOneDayService.call_bailian_api(prompt, system_prompt)
        except Exception as e:
            print(f"BaiLian API Error: {e}")
            return LoveOneDayService._generate_fallback_historical_broadcast(data, today)
    
    @staticmethod
    def _generate_historical_events_broadcast(data, today):
        """生成历史趣事模式播报"""
        historical_event = LoveOneDayService.get_historical_events(today.month, today.day)
        
        prompt = f"""
请以轻松有趣、活泼可爱的语气，为情侣生成一份有趣的历史知识播报。

今天是{today.strftime('%Y年%m月%d日')}。

在历史上的今天，曾发生过这样的事情：
{historical_event}

请生成一段有趣的播报内容，包含：
1. 用轻松幽默的方式介绍历史事件
2. 结合这个历史事件给情侣一些有趣的互动建议
3. 用活泼的语气鼓励情侣享受今天的美好
4. 加入一些趣味性的事实或小知识

语气要轻松有趣，多用emoji，让播报充满乐趣和正能量。

【重要要求】生成的播报内容必须严格控制在200-300字之间，确保内容完整、逻辑清晰、表达流畅，不要因为字数限制而截断句子或导致语义不完整。
"""
        
        system_prompt = "你是一个有趣活泼的助手，专门为情侣带来轻松愉快的历史知识。语气要活泼有趣，大量使用emoji，让播报充满乐趣。所有回复必须严格控制在200-300字之间。"
        
        try:
            return LoveOneDayService.call_bailian_api(prompt, system_prompt)
        except Exception as e:
            print(f"BaiLian API Error: {e}")
            return LoveOneDayService._generate_fallback_historical_events_broadcast(data, today)
    
    @staticmethod
    def _generate_fallback_anniversary_broadcast(data, today):
        """生成纪念日模式备用播报"""
        ann_titles = [ann.title for ann in data['today_anniversaries']]
        return f"💕 亲爱的，今天是特别的日子！{today.strftime('%Y年%m月%d日')}，同时也是{'和'.join(ann_titles)}！\n\n🎉 在这个美好的日子里，愿你们的爱情如初见般甜蜜，每一天都充满惊喜与感动。记得给彼此一个温暖的拥抱，说一声'我爱你'，让爱意在空气中流淌。可以一起准备一顿浪漫的晚餐，或者重温那些美好的回忆，让这份爱意更加深厚。\n\n💖 祝你们永远幸福快乐，携手走过每一个春夏秋冬，白头偕老，直到永远！愿这份爱意如同璀璨的星辰，永远照亮你们的人生旅途，让每一个平凡的日子都因为彼此的存在而变得闪闪发光。"
    
    @staticmethod
    def _generate_fallback_historical_broadcast(data, today):
        """生成历史日常模式备用播报"""
        return f"✨ 亲爱的，今天是{today.strftime('%Y年%m月%d日')}。\n\n📸 回望过去的今天，你们留下了许多美好的回忆，每一刻都值得珍藏。那些欢声笑语、那些温馨瞬间，都成为了爱情长河中最闪亮的星。翻看旧照片，重温那些美好的时光，心中涌起无限的感动，仿佛一切都发生在昨天。\n\n💝 愿你们继续携手前行，创造更多难忘的瞬间，让爱情在时光中愈发珍贵，直到地老天荒。每一个今天都将成为明天最美好的回忆，珍惜当下，让爱永远延续，让每一天都充满温暖和期待。"
    
    @staticmethod
    def _generate_fallback_historical_events_broadcast(data, today):
        """生成历史趣事模式备用播报"""
        event = LoveOneDayService.get_historical_events(today.month, today.day)
        return f"🗓️ 今天是{today.strftime('%Y年%m月%d日')}。\n\n🔍 历史上今天：{event}\n\n🌟 不妨和伴侣一起探索这个有趣的历史小知识，也许会激发你们的新奇想法。可以一起查阅更多相关资料，或者围绕这个话题展开有趣的讨论。比如，想象一下如果你们生活在那个年代，会有怎样的故事呢？\n\n愿你们的每一天都充满新奇与快乐，一起发现更多有趣的事物，创造属于你们的独特回忆！让历史成为你们爱情的调味剂，为平凡的日子增添一份别样的浪漫色彩，让每一天都充满惊喜和期待。"
    
    @staticmethod
    def text_to_speech(text, output_file='static/reports/love_one_day_report.mp3'):
        """将文本转换为语音"""
        try:
            # 使用 edge-tts 或其他 TTS 服务
            # 这里以 edge-tts 为例
            import edge_tts
            import asyncio
            
            async def _convert_to_speech():
                communicate = edge_tts.Communicate(text, 'zh-CN-XiaoxiaoNeural')
                await communicate.save(output_file)
                return output_file
            
            return asyncio.run(_convert_to_speech())
        except ImportError:
            print("edge-tts not installed, skipping TTS generation")
            return None
        except Exception as e:
            print(f"TTS Error: {e}")
            return None