import chromadb
from sentence_transformers import SentenceTransformer
import os
from django.conf import settings

CHROMA_PATH = os.path.join(settings.BASE_DIR, 'chroma_data')
_client = None
_model = None

def get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=CHROMA_PATH)
    return _client

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    return _model

def get_collection():
    client = get_client()
    return client.get_or_create_collection(name='textbook_knowledge')

def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = ' '.join(words[i:i+chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks

def add_document(document):
    model = get_model()
    collection = get_collection()
    chunks = chunk_text(document.raw_text)
    if not chunks:
        return 0
    embeddings = model.encode(chunks).tolist()
    ids = [f'doc{document.id}_chunk{i}' for i in range(len(chunks))]
    metadatas = [{
        'school_id': str(document.school_id),
        'subject_id': str(document.subject_id),
        'subject_name': document.subject.name,
        'document_id': str(document.id),
        'document_title': document.title,
        'chunk_index': i,
    } for i in range(len(chunks))]
    collection.add(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)
    return len(chunks)

def delete_document(document_id):
    collection = get_collection()
    try:
        collection.delete(where={'document_id': str(document_id)})
    except Exception:
        pass

def search(query, school_id, subject_id=None, n_results=4):
    model = get_model()
    collection = get_collection()
    query_embedding = model.encode([query]).tolist()[0]
    where_filter = {'school_id': str(school_id)}
    if subject_id:
        where_filter = {'$and': [{'school_id': str(school_id)}, {'subject_id': str(subject_id)}]}
    try:
        results = collection.query(query_embeddings=[query_embedding], n_results=n_results, where=where_filter)
        docs = results.get('documents', [[]])[0]
        metas = results.get('metadatas', [[]])[0]
        return [{'text': d, 'meta': m} for d, m in zip(docs, metas)]
    except Exception:
        return []