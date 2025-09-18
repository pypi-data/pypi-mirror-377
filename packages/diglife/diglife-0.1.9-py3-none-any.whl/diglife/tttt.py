import qdrant_client
from llama_index.vector_stores import QdrantVectorStore
from llama_index.storage.storage_context import StorageContext
from llama_index.indices.vector_store import VectorStoreIndex
from llama_index.schema import Document

# 假设您的 Qdrant 客户端和存储上下文已经配置
# --- 重新创建或获取您的 Qdrant 客户端和 vector_store ---
client = qdrant_client.QdrantClient(
    host="localhost", # 或者您的 Qdrant 服务的地址
    port=6333
)
vector_store = QdrantVectorStore(client=client, collection_name="diglife")
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

# --- 检索您刚刚上传的 Document ---
# 假设您知道您上传的 Document 的一些内容或者 id
# 这里我们尝试通过查询来检索一个 Document
query_text = "记忆卡片" # 使用您Document中的关键词
retriever = index.as_retriever(similarity_top_k=1)
nodes = retriever.retrieve(query_text)

if nodes:
    print(f"检索到的节点数量: {len(nodes)}")
    for node in nodes:
        print(f"原始文本 (node.text): {node.text}")
        print(f"原始元数据 (node.metadata): {node.metadata}")
        # 如果您的 Document 在 metadata 中有额外的 payload
        # print(f"Payload (node.node.metadata.get('payload_key')): {node.node.metadata.get('payload_key')}")
else:
    print("没有找到匹配的节点。")
