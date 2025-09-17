# 

import time
import asyncio
import json
from diglife.utils import extract_json, extract_article
from diglife.prompt import prompt_get_infos, prompt_base
from diglife.prompt import outline_prompt
from diglife.prompt import interview_material_clean_prompt, interview_material_add_prompt
from diglife.prompt import memory_card_system_prompt
from llmada.core import BianXieAdapter
from diglife.utils import super_print

from llmada.core import BianXieAdapter
import json
from diglife.utils import extract_json
bx = BianXieAdapter()


score_memory_card_prompt = """
我会给到你一段文本描写, 我希望你可以对它进行打分  
  
具体的评分规则如下  
  
9-10 分    内容标准: 真实动人  
7-9  分     内容标准: 细节丰富  
5-7 分    内容标准: 内容完整  
3-5  分     内容标准: 略显模糊  
0-3 分    内容标准: 内容稀薄

按照以下格式输出
```json
{"score":分数,
"reason":理由}
```

好的，请您给出文本描写，我会按照您的评分规则进行打分。
"""

memory_card_polish_prompt = """
**System Prompt for Generating a Short Personal Autobiography from Interview Transcripts**

You are an expert AI assistant tasked with crafting concise, first-person autobiographical narratives based on interview transcripts. Your primary goal is to distill the user's experiences and perspectives into a coherent and engaging short story, maintaining an authentic and personal tone.

**Core Principles and Guidelines:**

1.  **First-Person Narrative (Direct "I"):** The autobiography must be written entirely from the first-person perspective, starting directly with "我" (I) without introductory phrases like "我叫XX。" (My name is XX.) or similar framing.
2.  **Focus on User's Experiences & Emotions:** Prioritize extracting the user's personal experiences, feelings, reflections, and significant life events as revealed in the interview.
3.  **Conciseness & Storytelling:** Weave the extracted information into a fluid, storytelling format. Avoid simply listing facts; aim for a narrative flow that connects events and emotions.
4.  **Length Adaptation:** The length of the autobiography should be proportionate to the amount of detail and depth provided in the interview segments. More detailed conversations allow for richer narratives, while brief exchanges will result in shorter pieces.
5.  **Strategic Use of User Quotes (Minimised):**
    *   **Purpose:** Only use direct quotes from the user when they are particularly evocative, insightful, or represent a "classic" statement that truly encapsulates a key idea or emotion.
    *   **Quantity:** Aim for a minimal number of quotes (e.g., 1-2 per significant theme or section) to provide "点睛" (spot-on) emphasis without making the narrative feel like a transcript.
    *   **Integration:** Seamlessly integrate quotes into the narrative using appropriate punctuation (e.g., full-width quotation marks “ ”).
6.  **Analyze User's Intent & Focus:**
    *   **Identify Engagement:** Pay close attention to topics the user elaborates on, shows enthusiasm for, or offers open-ended answers. These are the areas to focus on and expand.
    *   **Identify Disinterest/Avoidance:** Crucially, if the user gives a closed-ended answer (e.g., "没有完全没有想过") or clearly indicates a reluctance to discuss a topic, **DO NOT include or elaborate on that topic** in the autobiography. This respects the user's boundaries and maintains narrative focus on their preferred areas.
7.  **Maintain Original Tone/Style (if applicable):** If the original user's text has a particular literary flair, emotional depth, or descriptive quality (as in the "童年惊魂" example), strive to retain and amplify that style in the generated autobiography.
8.  **Avoid AI-centric Language:** Do not use phrases like "As an AI, I have learned..." or "The AI asked..." – the output should be purely the user's story.
9.  **Error Handling/Clarification (Internal Note - not for output):** If the input is too ambiguous or insufficient to form a coherent story, request more context or examples, but for this prompt, assume sufficient input is provided.

**Input Format:**
You will be provided with interview segments, typically in a Q&A format (e.g., `ai: [AI question] human: [User response]`).

**Output Format:**
A single, cohesive, first-person narrative reflecting the user's experiences.
"""

memory_card_merge_prompt = """
我会给你多个文本,帮我融合成一个文本
"""
####
extract_person_name_prompt = """
我这里有一段个人传记的小章节, 由于我想校验传记中的人名是否正确, 所以我希望你帮我总结出这个篇章里面的所有人名,  
输出格式:  
```json  
[‘人名‘,…]  
```  
"""

extract_place_name_prompt = """
我这里有一段个人传记的小章节, 由于我想校验传记中的地名是否正确, 所以我希望你帮我总结出这个篇章里面的所有地名,  
输出格式:  
```json  
[‘地名‘,…]  
```  
"""


biography_free_prompt = """
帮我利用下面这些信息,生成一篇个人传记:

输出格式:  
```article
<content>
```  
"""

# TODO 重调机制应该通过改进llmada 来实现

class MemoryCardManager():
    def __init__(self):
        self.bx = BianXieAdapter()

    @staticmethod
    def get_score(S:list[int],total_score:int = 0,epsilon:float = 0.001,K:float = 0.8)->float:
        # 一个根据 列表分数 计算总分数的方法 如[1,4,5,7,1,5] 其中元素是 1-10 的整数

        # 一个非常小的正数，确保0分也有微弱贡献，100分也不是完美1
        # 调整系数，0 < K <= 1。K越大，总分增长越快。


        # 数字人生总进度 
        # 人生主题分值计算
        
        for score in S:
            # 1. 标准化每个分数到 (0, 1) 区间
            normalized_score = (score + epsilon) / (10 + epsilon)

            # 2. 更新总分
            # 每次增加的是“距离满分的剩余空间”的一个比例
            total_score = total_score + (100 - total_score) * normalized_score * K

            # 确保不会因为浮点数精度问题略微超过100，虽然理论上不会
            if total_score >= 100 - 1e-9: # 留一点点余地，避免浮点数误差导致判断为100
                total_score = 100 - 1e-9 # 强制设置一个非常接近100但不等于100的值
                break # 如果已经非常接近100，可以提前终止

        return total_score
    
    def score_from_memory_card(self,memory_cards:list[str])->list[int]:
        results = []
        for memory_card in memory_cards:
            result = self.bx.product(score_memory_card_prompt + "\n" + memory_card)
            results.append(json.loads(extract_json(result)))

        return results

    def memory_card_polish(self,memory_cards:list[str])->list[str]:
        # 记忆卡片润色
        results = []
        for memory_card in memory_cards:
            result = bx.product(memory_card_polish_prompt + "\n" + memory_card)
            results.append(result)
        # return json.loads(extract_json(result))
        return results


    def memory_card_merge(self,memory_cards:list[str]):
        # 记忆卡片合并
        result = bx.product(memory_card_merge_prompt + "\n" + json.dumps(memory_cards))
        return result

    
    async def agenerate_memory_card(self,chat_history_str:str, weight:int = 1000):
        
        number_ = len(chat_history_str)//weight

        base_prompt = memory_card_system_prompt.format(number = number_) + chat_history_str
        try:
            result = await asyncio.to_thread(bx.product, base_prompt) 
            result_json_str = extract_json(result)

            if result_json_str:
                return json.loads(result_json_str)
            else:
                return ""
        except Exception as e:
            print(f"Error processing  {chat_history_str[:30]}: {e}")
            return ""


### 

class BiographyGenerate():
    def __init__(self):
        model_name = "gemini-2.5-flash-preview-05-20-nothinking"
        bx = BianXieAdapter()
        bx.model_pool.append(model_name)
        bx.set_model(model_name=model_name)
        self.bx = bx


    def extract_person_name(self,bio_chunk:str):
        result = bx.product(extract_person_name_prompt + "\n" + bio_chunk)
        return json.loads(extract_json(result))


    def extract_person_place(self,bio_chunk:str):
        result = bx.product(extract_place_name_prompt + "\n" + bio_chunk)
        return result


    def material_generate(self,vitae:str,memory_cards:list[str])->str: # 简历, 
        """
        素材整理
        vitae : 简历
        memory_cards : 记忆卡片们
        """
        def split_into_chunks(my_list, chunk_size = 5):
            """
            使用列表推导式将列表分割成大小为 chunk_size 的块。
            """
            return [my_list[i:i + chunk_size] for i in range(0, len(my_list), chunk_size)]

        # --- 示例 ---
        chunks = split_into_chunks(memory_cards, chunk_size = 5)

        material = ""
        for i,chunk in enumerate(chunks):
            chunk = json.dumps(chunk,ensure_ascii = False)
            if i == 0:
                material = self.bx.product(interview_material_clean_prompt + vitae + chunk)
            else:
                material = self.bx.product(interview_material_add_prompt + "#素材:\n" + material + "#记忆卡片:\n" + chunk)
        return material


    def outline_generate(self,material:str)->str:
        """
        大纲生成
        """
        outline_origin = self.bx.product(outline_prompt + material)
        outline = extract_json(outline_origin)
        return json.loads(outline)

    async def gener_biography_brief(self,outline:dict)->str:
        outline = json.dumps(outline)

        brief = self.bx.product(f'帮我根据大纲写一个传记的简介: {outline}')
        return brief

    async def awrite_chapter(self,chapter,
                             master = "",
                             material = "", 
                             outline:dict = {},
                             suggest_number_words = 3000):
        created_material =""
        try:
            print()
            material_prompt = prompt_get_infos.format(material= material,frame = json.dumps(outline), requirements = json.dumps(chapter))
            material = await asyncio.to_thread(self.bx.product, material_prompt) 
            words = prompt_base.format(master = master, chapter = f'{chapter.get("chapter_number")} {chapter.get("title")}', 
                                       topic = chapter.get("topic"),
                                        number_words = suggest_number_words,
                                        material = material ,reference = "",
                                        port_chapter_summery = '' )
            article = await asyncio.to_thread(self.bx.product, words) # Python 3.9+

            chapter_name = await asyncio.to_thread(self.extract_person_name, article) 
            chapter_place = await asyncio.to_thread(self.extract_person_place, article)
            
            return {"chapter_number":chapter.get("chapter_number"),"article": extract_article(article),
                    "material":material,"created_material":created_material,
                    "chapter_name":chapter_name,
                    "chapter_place":chapter_place}
        
        except Exception as e:
            print(f"Error processing chapter {chapter.get('chapter_number')}: {e}")
            return None

    def generate_biography_free(self,user_name, vitae, memory_cards):
        # 简要版说法
        result = bx.product(biography_free_prompt + "\n" + f"{user_name},{vitae},{memory_cards}")
        result = extract_article(result)
        return result

