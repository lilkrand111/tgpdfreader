import os
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.readers.file import PDFReader # Импортируем нормальный загрузчик
from llama_index.core.node_parser import SentenceSplitter

# 1. Настройки поиска (используем мощную русскую модель)
Settings.embed_model = HuggingFaceEmbedding(model_name="intfloat/multilingual-e5-large")
Settings.node_parser = SentenceSplitter(chunk_size=800, chunk_overlap=100)

def create_index():
    # 2. Явно указываем, как читать PDF
    loader = PDFReader()
    
    documents = []
    folder = "./books"
    
    print("Начинаю чтение PDF файлов...")
    for file in os.listdir(folder):
        if file.endswith(".pdf"):
            file_path = os.path.join(folder, file)
            # Читаем именно страницы текста
            docs = loader.load_data(file=file_path)
            documents.extend(docs)

    if not documents:
        print("Ошибка: Текст не извлечен!")
        return

    # 3. ПРОВЕРКА: Теперь здесь должен быть нормальный русский текст!
    print("\n--- ПРОВЕРКА ТЕКСТА (ТЕПЕРЬ ТУТ ДОЛЖНЫ БЫТЬ БУКВЫ) ---")
    print(documents[0].text[:500]) 
    print("------------------------------------------------------\n")

    # 4. Создаем индекс
    index = VectorStoreIndex.from_documents(documents, show_progress=True)
    
    # 5. Сохраняем
    index.storage_context.persist(persist_dir="./storage")
    print("База знаний успешно создана!")

if __name__ == "__main__":
    create_index()