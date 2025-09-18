# server
from typing import Dict, Any, Optional, List

# 推荐算法
from pydantic import BaseModel, Field, model_validator
from diglife.embedding_pool import EmbeddingPool
from diglife.core import MemoryCardManager, BiographyGenerate
from diglife.log import Log
import uuid
import asyncio
from fastapi import FastAPI, HTTPException, Header, status
from fastapi.middleware.cors import CORSMiddleware
from diglife.core import DigitalAvatar

logger = Log.logger

app = FastAPI(
    title="LLM Service",
    description="Provides an OpenAI-compatible API for custom large language models.",
    version="1.0.1",
)

# --- Configure CORS ---
# ! Add this section !
# Define allowed origins. Be specific in production!
# Example: origins = ["http://localhost:3000", "https://your-frontend-domain.com"]
origins = [
    "*",  # Allows all origins (convenient for development, insecure for production)
    # Add the specific origin of your "别的调度" tool/frontend if known
    # e.g., "http://localhost:5173" for a typical Vite frontend dev server
    # e.g., "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Specifies the allowed origins
    allow_credentials=True,  # Allows cookies/authorization headers
    allow_methods=["*"],  # Allows all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers (Content-Type, Authorization, etc.)
)
# --- End CORS Configuration ---

# 这边负责日志, 防止报错的记录方案 并非其他地方绝对不能用,
# try_cache 这边也负责


ep = EmbeddingPool()
MCmanager = MemoryCardManager()
bg = BiographyGenerate()
da = DigitalAvatar()


task_store: Dict[str, Dict[str, Any]] = {}
recommended_biographies_cache: Dict[str, Dict[str, Any]] = {}
recommended_figure_cache: Dict[str, Dict[str, Any]] = {}
recommended_biographies_cache_max_leng = 2
recommended_cache_max_leng = 2


@app.get("/")
async def root():
    """ server run """
    return {"message": "LLM Service is running."}

class LifeTopicScoreRequest(BaseModel):
    S_list: List[int] = Field(..., description="List of scores, each between 1 and 10.")
    K: float = Field(0.8, description="Weighting factor K.")
    total_score: int = Field(0, description="Initial total score.")
    epsilon: float = Field(0.001, description="Epsilon value for calculation.")

    @model_validator(mode="after")
    def validate_s_list(self):
        if not all(1 <= x <= 10 for x in self.S_list):
            raise ValueError(
                "All elements in 'S_list' must be integers between 1 and 10 (inclusive)."
            )
        return self

class ScoreRequest(BaseModel):
    S_list: List[float] = Field(
        ...,
        description="List of string representations of scores, each between 1 and 10.",
    )
    K: float = Field(0.3, description="Coefficient K for score calculation.")
    total_score: int = Field(0, description="Total score to be added.")
    epsilon: float = Field(0.0001, description="Epsilon value for score calculation.")

    @model_validator(mode="after")
    def check_s_list_values(self):
        for s_val in self.S_list:
            try:
                int_s_val = float(s_val)
                if not (1 <= int_s_val <= 100):
                    raise ValueError(
                        "Each element in 'S_list' must be an integer between 1 and 10."
                    )
            except ValueError:
                raise ValueError(
                    "Each element in 'S_list' must be a valid integer string."
                )
        return self

@app.post("/life_topic_score")
async def life_topic_score_server(request: LifeTopicScoreRequest):
    """
    Calculates the life topic score based on the provided parameters.
    S_list elements must be integers between 1 and 10.
    """
    logger.info('running life_topic_score')
    try:
        result = MemoryCardManager.get_score(
            S=request.S_list,
            total_score=request.total_score,
            epsilon=request.epsilon,
            K=request.K,
        )
        return {"message": "Life topic score calculated successfully", 
                "result": int(result)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )

@app.post("/life_aggregate_scheduling_score")
async def life_aggregate_scheduling_score_server(request: ScoreRequest):
    """
    Calculates the life aggregate scheduling score based on the provided parameters.
    S_list: List of scores (as strings, will be converted to integers)
    K: Coefficient K (default 0.8)
    total_score: Total score to add (default 0)
    epsilon: Epsilon value (default 0.001)
    """
    logger.info('running life_aggregate_scheduling_score')
    try:
        result = MemoryCardManager.get_score(
            request.S_list,
            total_score=request.total_score,
            epsilon=request.epsilon,
            K=request.K,
        )
        return {
            "message": "life aggregate scheduling score successfully",
            "result": result,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )


# 记忆合并
class MemoryCardsRequest(BaseModel):
    memory_cards: list[str] = Field(..., description="记忆卡片列表")

class MemoryCardGenerateRequest(BaseModel):
    text: str = Field(..., description="聊天内容或者文本内容")

class MemoryCardResult(BaseModel):
    """
    传记生成结果的数据模型。
    """
    message: str = Field(..., description="优化好的记忆卡片")
    memory_card: str = Field(..., description="优化好的记忆卡片")

class MemoryCardsResult(BaseModel):
    """
    传记生成结果的数据模型。
    """
    message: str = Field(..., description="优化好的记忆卡片")
    memory_cards: list[str] = Field(..., description="优化好的记忆卡片")


@app.post("/memory_card/score")
async def score_from_memory_card_server(request: MemoryCardsRequest):
    """
    记忆卡片质量评分
    接收一个记忆卡片内容字符串，并返回其质量评分。
    """
    logger.info('running memory_card/score')
    results = MCmanager.score_from_memory_card(memory_cards=request.memory_cards)

    return {"message": "memory card score successfully", "result": results}




@app.post("/memory_card/merge",
          response_model=MemoryCardResult)
async def memory_card_merge_server(request: MemoryCardsRequest) -> dict:
    """
    记忆卡片质量评分
    接收一个记忆卡片内容字符串，并返回其质量评分。
    """

    logger.info("running memory_card_merge")
    result = MCmanager.memory_card_merge(memory_cards=request.memory_cards)

    return MemoryCardResult(message = "memory card merge successfully",
                            memory_card = result )


@app.post("/memory_card/polish",
          response_model=MemoryCardsResult,
          summary="记忆卡片发布AI润色")
async def memory_card_polish_server(request: MemoryCardsRequest) -> dict:
    """
    记忆卡片发布AI润色接口。
    接收记忆卡片内容，并返回AI润色后的结果。
    """
    logger.info("running memory_card_polish")
    result = MCmanager.memory_card_polish(memory_cards=request.memory_cards)
    return MemoryCardsResult(message="memory card polish successfully",
                             memory_cards=result)

class MemoryCardGenerageResult(BaseModel):
    message: str
    chapters: list[dict]

@app.post("/memory_card/generate_by_text", response_model=MemoryCardGenerageResult)
async def memory_card_generate_by_text_server(request: MemoryCardGenerateRequest) -> dict:
    """上传文件生成记忆卡片"""
    logger.info("running generate_by_text")
    # 假设 agenerate_memory_card 是一个异步函数，并且已经定义在其他地方
    result = await MCmanager.agenerate_memory_card(
        chat_history_str=request.text, weight=1000
    )
    chapters = result['chapters']
    for i in chapters:
        i.update({"time":"1995年07月--日"})

    return MemoryCardGenerageResult(
        message="memory card generate by text successfully",
        chapters = chapters
    )



@app.post("/memory_card/generate",response_model=MemoryCardGenerageResult)
async def memory_card_generate_server(request: MemoryCardGenerateRequest) -> dict:
    """记忆卡片生成优化
    
        # {
    #   "事件1": {
    #     "事件时间": "1995年07月--日",
    #     "事件名称": "全家海边度假",
    #     "事件内容": "和家人一起去海边玩。"
    #   },
    #   "事件2": {
    #     "事件时间": "11到20岁",
    #     "事件名称": "学习开车",
    #     "事件内容": "开始学习驾驶技术。"
    #   },
    #   "事件3": {
    #     "事件时间": "2020年--月--日",
    #     "事件名称": "儿子出生",
    #     "事件内容": "孩子来到这个世界。"
    #   },
    #   "事件4": {
    #     "事件时间": "21到30岁",
    #     "事件名称": "第一次出国",
    #     "事件内容": "第一次离开国家去旅行。"
    #   }
    # }
    # 
    # 
    """
    logger.info("running memory_card generate")
    # 假设 agenerate_memory_card 是一个异步函数，并且已经定义在其他地方
    result = await MCmanager.agenerate_memory_card(
        chat_history_str=request.text, weight=1000
    )
    chapters = result['chapters']
    for i in chapters:
        i.update({"time":"1995年07月--日"})

    return MemoryCardGenerageResult(
        message="memory card generate successfully",
        chapters = chapters
    )


# 模拟任务存储和状态


class BiographyRequest(BaseModel):
    """
    请求传记生成的数据模型。
    """

    user_name: str = Field(None, description="用户名字")
    vitae: str = Field(None, description="用户简历")
    memory_cards: list[str] = Field(..., description="记忆卡片列表")
    # 可以在这里添加更多用于生成传记的输入字段


class BiographyResult(BaseModel):
    """
    传记生成结果的数据模型。
    """

    task_id: str = Field(..., description="任务的唯一标识符。")
    status: str = Field(...,description="任务的当前状态 (e.g., 'PENDING', 'PROCESSING', 'COMPLETED', 'FAILED').",)
    biography_brief: Optional[str] = Field(None, description="生成的传记简介，仅在状态为 'COMPLETED' 时存在。")
    biography_text: Optional[str] = Field(None, description="生成的传记文本，仅在状态为 'COMPLETED' 时存在。")
    biography_name: Optional[str] = Field(None, description="生成的传记文本中的人名，仅在状态为 'COMPLETED' 时存在。")
    biography_place: Optional[str] = Field(None, description="生成的传记文本中的地名，仅在状态为 'COMPLETED' 时存在。")
    error_message: Optional[str] = Field(None, description="错误信息，仅在状态为 'FAILED' 时存在。")
    progress: float = Field(0.0, ge=0.0, le=1.0, description="任务处理进度，0.0到1.0之间。")

async def _generate_biography(task_id: str, request_data: BiographyRequest):
    """
    模拟一个耗时的传记生成过程。
    在真实场景中，这里会调用LLM或其他复杂的生成逻辑。
    """

    try:
        task_store[task_id]["status"] = "PROCESSING"
        task_store[task_id]["progress"] = 0.1
        logger.info(f"Task {task_id}: Starting generation ")

        # 模拟LLM调用和处理时间

        # 在后台启动异步任务

        # 素材整理
        material = bg.material_generate(
            vitae=request_data.vitae, memory_cards=request_data.memory_cards
        )
        task_store[task_id]["progress"] = 0.2

        # 生成大纲
        outline = bg.outline_generate(material)

        task_store[task_id]["progress"] = 0.3

        # 生成传记简介
        brief = bg.gener_biography_brief(outline)

        task_store[task_id]["progress"] = 0.5

        tasks = []
        for part, chapters in outline.items():
            for chapter in chapters:
                logger.info(
                    f"Creating task for chapter: {chapter.get('chapter_number')} {chapter.get('title')}"
                )
                tasks.append(
                    bg.awrite_chapter(
                        chapter,
                        master=request_data.user_name,
                        material=material,
                        outline=outline,
                    )
                )
        results = await asyncio.gather(*tasks, return_exceptions=False)

        # content = ""
        biography_json = {}
        biography_name = []
        biography_place = []
        for part, chapters in outline.items():
            biography_json[part] = []
            # content += f'# {part}'
            # content += "\n"
            for chapter in chapters:
                chapter_number = chapter.get("chapter_number")
                for x in results:
                    if x.get("chapter_number") == chapter_number:
                        # content += x.get("article")
                        # content += "\n"
                        biography_json[part].append(x.get("article"))
                        biography_name += x.get("chapter_name")
                        biography_place += x.get("chapter_place")

        task_store[task_id]["biography_brief"] = brief
        task_store[task_id]["biography_text"] = biography_json
        task_store[task_id]["biography_name"] = biography_name
        task_store[task_id]["biography_place"] = biography_place
        task_store[task_id]["status"] = "COMPLETED"
        task_store[task_id]["progress"] = 1.0

    except Exception as e:
        task_store[task_id]["status"] = "FAILED"
        task_store[task_id]["error_message"] = str(e)
        task_store[task_id]["progress"] = 1.0
        logger.info(f"Task {task_id}: Generation failed with error: {e}")


@app.post(
    "/generate_biography", response_model=BiographyResult, summary="提交传记生成请求"
)
async def generate_biography(request: BiographyRequest):
    """
    提交一个传记生成请求。

    此接口会立即返回一个任务ID，客户端可以使用此ID查询生成进度和结果。
    实际的生成过程会在后台异步执行。
    """
    task_id = str(uuid.uuid4())
    task_store[task_id] = {
        "task_id": task_id,
        "status": "PENDING",
        "biography_brief": None,
        "biography_text": None,
        "biography_name": None,
        "biography_place": None,
        "error_message": None,
        "progress": 0.0,
        "request_data": request.model_dump(),  # 存储请求数据以备后续使用
    }

    asyncio.create_task(_generate_biography(task_id, request))

    return BiographyResult(task_id=task_id, status="PENDING", progress=0.0)


@app.get(
    "/get_biography_result/{task_id}",
    response_model=BiographyResult,
    summary="查询传记生成结果",
)
async def get_biography_result(task_id: str):
    """
    根据任务ID查询传记生成任务的状态和结果。
    """
    task_info = task_store.get(task_id)
    if not task_info:
        raise HTTPException(
            status_code=404, detail=f"Task with ID '{task_id}' not found."
        )

    return BiographyResult(
        task_id=task_info["task_id"],
        status=task_info["status"],
        biography_brief=task_info.get("biography_brief"),
        biography_text=task_info.get("biography_text"),
        biography_name=task_info.get("biography_name"),
        biography_place=task_info.get("biography_place"),
        error_message=task_info.get("error_message"),
        progress=task_info.get("progress", 0.0),
    )


# 免费版传记优化
@app.post("/generate_biography_free", summary="提交传记生成请求")
async def generate_biography(request: BiographyRequest):
    """
    提交一个传记生成请求。

    此接口会立即返回一个任务ID，客户端可以使用此ID查询生成进度和结果。
    实际的生成过程会在后台异步执行。
    """
    request.user_name
    request.memory_cards
    request.vitae
    result = bg.generate_biography_free(
        user_name=request.user_name,
        memory_cards=request.memory_cards,
        vitae=request.vitae,
    )

    return {"message": "generate_biography_free successfully", "result": result}

# 推荐算法

class UpdateItem(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000, description="要更新的文本内容。")
    id: str = Field(..., min_length=1, max_length=100, description="与文本关联的唯一ID。")
    type: int = Field(..., description="上传的类型")

class QueryItem(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=500, description="user_id")

@app.post(
    "/recommended/update",  # 推荐使用POST请求进行数据更新
    summary="更新或添加文本嵌入",
    description="将给定的文本内容与一个ID关联并更新到Embedding池中。",
    response_description="表示操作是否成功。",
)
def recommended_update(item: UpdateItem):
    """ 记忆卡片是0  传记是1 
    记忆卡片是0 
    记忆卡片上传的是记忆卡片的内容 str
    记忆卡片id
    0

    传记是1 
    上传的是传记简介  str
    传记id  
    1

    数字分身是2
    上传数字分身简介和性格描述  str
    数字分身id
    2
    """
    try:
        if item.type in [0,1,2]:  # 上传的是卡片
            ep.update(text=item.text, id=item.id,type = item.type)
        else:
            logger.error(f"Error updating EmbeddingPool for ID '{item.id}': {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update embedding for ID '{item.id}': {e}",
            )

        return {"status": "success", "message": f"ID '{item.id}' updated successfully."}

    except ValueError as e:  # 假设EmbeddingPool.update可能抛出ValueError
        logger.warning(f"Validation error during update: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating EmbeddingPool for ID '{item.id}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update embedding for ID '{item.id}': {e}",
        )


class DeleteRequest(BaseModel):
    id: str

class DeleteResponse(BaseModel):
    status: str = "success" # 假设返回一个状态表示删除成功

@app.post("/recommended/delete",
          response_model=DeleteResponse,
          description = "delete")
async def delete_server(request:DeleteRequest):

    logger.info('running delete_server')
    
    # TODO 
    result = ep.delete(
        id=request.id
    ) # 包裹的内核函数
 
    ########
    return DeleteResponse(
        status="success",
    )

@app.post(
    "/recommended/search_biographies_and_cards",
    summary="搜索传记和记忆卡片",
    description="搜索传记和记忆卡片",
    response_description="搜索结果列表。",
)
async def recommended_biographies_and_cards(query_item: QueryItem):
    """
    # result = [
    #     {
    #         "id": "1916693308020916225",  # 传记ID
    #         "type": 1,
    #         "order": 0,
    #     },
    #     {
    #         "id": "1962459564012359682",  # 卡片ID
    #         "type": 0,
    #         "order": 1,
    #     },
    #     {
    #         "id": "1916389315373727745",  # 传记ID
    #         "type": 1,
    #         "order": 2,
    #     },
    # ]
    """
    try:
        #TODO 调用id 获得对应的用户简介 query_item.user_id
        user_brief = "我是一个大男孩"
        result = ep.search_bac(query=user_brief)

        if recommended_biographies_cache.get(query_item.user_id):
            clear_result = [
                i
                for i in result
                if i.get("id")
                not in recommended_biographies_cache.get(query_item.user_id)
            ]
        else:
            recommended_biographies_cache[query_item.user_id] = []
            clear_result = result

        recommended_biographies_cache[query_item.user_id] += [
            i.get("id") for i in result
        ]
        recommended_biographies_cache[query_item.user_id] = list(
            set(recommended_biographies_cache[query_item.user_id])
        )
        if (
            len(recommended_biographies_cache[query_item.user_id])
            > recommended_biographies_cache_max_leng
        ):
            recommended_biographies_cache[query_item.user_id] = []

        return {
            "status": "success",
            "result": clear_result,
            "query": query_item.user_id,
        }

    except Exception as e:
        logger.error(
            f"Error searching EmbeddingPool for query '{query_item.user_id}': {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform search: {e}",
        )


@app.post(
    "/recommended/search_figure_person",
    description="搜索数字分身的",
)
async def recommended_figure_person(query_item: QueryItem):
    """
    result = [
        {
            "id": "1905822448827469825",  # 传记ID
            "type": 2,
            "order": 0,
        },
        {
            "id": "1902278304670625793",  # 卡片ID
            "type": 2,
            "order": 1,
        },
        {
            "id": "1905819574433087490",  # 传记ID
            "type": 2,
            "order": 2,
        },
    ]
    """

    try:
        #TODO 调用id 获得对应的用户简介 query_item.user_id
        user_brief = "我是一个大男孩"
        result = ep.search_figure_person(query=user_brief) # 100+

        if recommended_figure_cache.get(query_item.user_id):
            # 不需要创建
            clear_result = [
                i
                for i in result
                if i.get("id") not in recommended_figure_cache.get(query_item.user_id)
            ]
        else:
            recommended_figure_cache[query_item.user_id] = []
            clear_result = result

        recommended_figure_cache[query_item.user_id] += [i.get("id") for i in result]
        recommended_figure_cache[query_item.user_id] = list(
            set(recommended_figure_cache[query_item.user_id])
        )
        if (
            len(recommended_figure_cache[query_item.user_id])
            > recommended_cache_max_leng
        ):
            recommended_figure_cache[query_item.user_id] = []
        return {
            "status": "success",
            "result": clear_result,
            "query": query_item.user_id,
        }

    except Exception as e:
        logger.error(
            f"Error searching EmbeddingPool for query '{query_item.user_id}': {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform search: {e}",
        )


from diglife.core import user_dverview

from diglife.core import user_relationship_extraction

class UserDverviewRequest(BaseModel):
    old_dverview: str
    memory_cards: list[str]

class UserDverviewResponse(BaseModel):
    message: str
    summary: str


@app.post("/user_dverview",response_model=UserDverviewResponse)
async def user_dverview_server(request:UserDverviewRequest):
    """
    None
    """
    logger.info('running user_dverview_server')
    
    result = user_dverview(
        old_dverview=request.old_dverview, memory_cards=request.memory_cards
    ) # 包裹的内核函数
    
    return UserDverviewResponse(
        message="successful",
        summary=result
    )


class UserRelationshipExtractionRequest(BaseModel):
    chat_history: str
    order_relationship: dict

class UserRelationshipExtractionResponse(BaseModel):
    message: str
    output_relation: dict

@app.post("/user_relationship_extraction",response_model=UserRelationshipExtractionResponse)
async def user_relationship_extraction_server(request:UserRelationshipExtractionRequest):
    """
    用户关系提取
    """
    logger.info('running user_relationship_extraction_server')
    
    result = user_relationship_extraction(
        chat_history=request.chat_history, order_relationship=request.order_relationship
    ) 
 
    return UserRelationshipExtractionResponse(
        message="LLM Service is running.", 
        output_relation=result
    )


class BriefResponse(BaseModel):
    message: str
    title: str
    content: str

class digital_avatar_personalityResult(BaseModel):
    """
    传记生成结果的数据模型。
    """
    message: str = Field(..., description="优化好的记忆卡片")
    text: str = Field(..., description="优化好的记忆卡片")


@app.post("/digital_avatar/brief",
          response_model=BriefResponse,
          description = "数字分身介绍")
async def brief_server(request:MemoryCardsRequest):
    logger.info('running brief_server')
    result = da.brief(
        memory_cards=request.memory_cards
    ) 
    return BriefResponse(
        message="successful",
        title=result.get("title"), content=result.get("content")
    )

@app.post("/digital_avatar/personality_extraction",response_model=digital_avatar_personalityResult)
async def digital_avatar_personality_extraction(request:MemoryCardsRequest):
    """数字分身性格提取 """

    logger.info('running digital_avatar_desensitization')
    result = da.personality_extraction(memory_cards=request.memory_cards)
    return digital_avatar_personalityResult(
        message="successful",
        text=result
    )

@app.post("/digital_avatar/desensitization",response_model=MemoryCardsResult)
async def digital_avatar_desensitization(request:MemoryCardsRequest):
    """
    数字分身脱敏
    """
    logger.info('running digital_avatar_desensitization')
    result = da.desensitization(memory_cards=request.memory_cards)
    return MemoryCardsResult(
        message="successful",
        memory_cards=result
    )



if __name__ == "__main__":
    # 这是一个标准的 Python 入口点惯用法
    # 当脚本直接运行时 (__name__ == "__main__")，这里的代码会被执行
    # 当通过 python -m YourPackageName 执行 __main__.py 时，__name__ 也是 "__main__"
    import argparse
    import uvicorn
    from .log import Log

    default = 8007

    parser = argparse.ArgumentParser(
        description="Start a simple HTTP server similar to http.server."
    )
    parser.add_argument(
        "port",
        metavar="PORT",
        type=int,
        nargs="?",  # 端口是可选的
        default=default,
        help=f"Specify alternate port [default: {default}]",
    )
    # 创建一个互斥组用于环境选择
    group = parser.add_mutually_exclusive_group()

    # 添加 --dev 选项
    group.add_argument(
        "--dev",
        action="store_true",  # 当存在 --dev 时，该值为 True
        help="Run in development mode (default).",
    )

    # 添加 --prod 选项
    group.add_argument(
        "--prod",
        action="store_true",  # 当存在 --prod 时，该值为 True
        help="Run in production mode.",
    )
    args = parser.parse_args()

    if args.prod:
        env = "prod"
    else:
        # 如果 --prod 不存在，默认就是 dev
        env = "dev"

    port = args.port
    if env == "dev":
        port += 100
        Log.reset_level("debug", env=env)
        reload = True
        app_import_string = f"{__package__}.server:app"  # <--- 关键修改：传递导入字符串
    elif env == "prod":
        Log.reset_level(
            "info", env=env
        )  # ['debug', 'info', 'warning', 'error', 'critical']
        reload = False
        app_import_string = app
    else:
        reload = False
        app_import_string = app

    # 使用 uvicorn.run() 来启动服务器
    # 参数对应于命令行选项
    uvicorn.run(
        app_import_string, host="0.0.0.0", port=port, reload=reload  # 启用热重载
    )
