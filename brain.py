import os
import datetime
from dotenv import load_dotenv
from llama_index.core import StorageContext, load_index_from_storage, Settings
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

load_dotenv()

# Настройки те же, что при создании индекса
Settings.embed_model = HuggingFaceEmbedding(model_name="intfloat/multilingual-e5-large")
Settings.llm = Gemini(model="models/gemini-2.5-flash", api_key=os.getenv("GOOGLE_API_KEY"))

def write_to_log(user_question, final_prompt, ai_answer):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = (
        f"{'='*50}\nВРЕМЯ: {timestamp}\n"
        f"ВОПРОС: {user_question}\n\n"
        f"ЧТО ВИДЕЛ ИИ (ПРОМПТ + КОНТЕКСТ):\n{final_prompt}\n\n"
        f"ОТВЕТ ИИ:\n{ai_answer}\n{'='*50}\n\n"
    )
    with open("logs.txt", "a", encoding="utf-8") as f:
        f.write(log_entry)

def get_answer_from_pdf(question):
    # 1. Загружаем индекс из папки storage
    storage_context = StorageContext.from_defaults(persist_dir="./storage")
    index = load_index_from_storage(storage_context)

    # 2. Создаем "движок" запросов
    # similarity_top_k=5 — сколько кусков искать
    query_engine = index.as_query_engine(similarity_top_k=5)

    # 3. Настраиваем промпт (инструкцию для ИИ)
    # LlamaIndex сам подставит контекст в промпт
    custom_prompt = (
        "Ты — высококвалифицированный технический наставник и эксперт по предоставленным учебным материалам.\n"
        "Твоя задача: проанализировать фрагменты учебника и дать точный ответ на вопрос студента.\n\n"
        
        "ПРАВИЛА ОТВЕТА:\n"
        "1. Используй ТОЛЬКО предоставленный ниже текст учебника. Не придумывай ничего от себя.\n"
        "2. Если в тексте есть точное определение или формула, приведи их дословно.\n"
        "3. Если информация в учебнике отсутствует, так и напиши: 'В изученных материалах нет ответа на этот вопрос'.\n"
        "4. Пиши профессионально, но доступно для студента.\n\n"
        
        f"ВОПРОС СТУДЕНТА: {question}"
    )

    response = query_engine.query(custom_prompt)

    # Извлекаем найденный текст для лога
    context_found = "\n".join([node.get_content() for node in response.source_nodes])
    
    # Собираем полный текст промпта, который ушел в Gemini
    full_prompt_for_log = f"ИНСТРУКЦИЯ:\n{custom_prompt}\n\nНАЙДЕННЫЙ КОНТЕКСТ:\n{context_found}"
    
    # Записываем всё в файл
    write_to_log(question, full_prompt_for_log, str(response))

    return str(response)

if __name__ == "__main__":
    q = input("Твой вопрос: ")
    print("-" * 30)
    print(f"ОТВЕТ:\n{get_answer_from_pdf(q)}")