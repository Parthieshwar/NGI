# chatbot.py
from langchain_mistralai import ChatMistralAI
import os
import logging
import warnings
import asyncio
from dotenv import load_dotenv
from chatbot.rag import get_vectorstore
from chatbot.prompt import prompt_template
from langchain.schema.runnable import RunnableParallel
from chatbot.memory import ConversationMemory

warnings.filterwarnings("ignore")

memory = ConversationMemory(max_len=10)

# Suppress noisy loggers
logging.basicConfig(level=logging.WARNING)  
for noisy_logger in ["httpx", "faiss"]:
    logging.getLogger(noisy_logger).setLevel(logging.ERROR)

logger = logging.getLogger("chatbot")

# Load environment variables
load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
os.environ["MISTRAL_API_KEY"] = MISTRAL_API_KEY
os.environ["USER_AGENT"] = "Mozilla/5.0"

# Init LLM
# llm = init_chat_model("mistral-small", model_provider="mistralai", temperature=0.1,min_tokens=1000)
llm = ChatMistralAI(
    model_name="mistral-small",
    temperature=0.1,
    max_tokens=5000,
)

# Init retriever
vectorstore = get_vectorstore()
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 5},
)

# Build LCEL chain (retriever -> prompt -> llm)
chain = (
    RunnableParallel(
        context=lambda x: "\n".join([doc.page_content for doc in retriever.get_relevant_documents(x["question"])]),
        question=lambda x: x["question"],
        memory=lambda x: memory.get_memory_text()  # inject last 5 exchanges
    )
    | prompt_template
    | llm
)

# async def chat():
#     print("Chatbot is ready! Type 'exit' to quit.")
#     while True:
#         query = input("\nYou: ")
#         if query.lower() in ["exit", "quit"]:
#             print("Goodbye!")
#             break

#         # Add human message to memory
#         memory.add_human_message(query)

#         # Stream response from chain
#         print("Bot: ", end="", flush=True)
#         response_text = ""
#         try:
#             async for chunk in chain.astream({
#                 "question": query,
#                 "context": "\n".join([doc.page_content for doc in retriever.get_relevant_documents(query)]),
#                 "memory": memory.get_memory_text()  # <-- pass memory here
#             }):
#                 text = chunk.content if hasattr(chunk, "content") else str(chunk)
#                 response_text += text
#                 print(text, end="", flush=True)
#                 await asyncio.sleep(0.02)
#         except Exception as e:
#             print(f"\n[Error generating response: {e}]")
#             continue

#         # Add AI response to memory
#         memory.add_ai_message(response_text)
#         print()