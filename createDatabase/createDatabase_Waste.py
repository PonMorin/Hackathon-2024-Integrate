from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import dotenv_values

config = dotenv_values(".env")
os.environ["OPENAI_API_KEY"] = config["openai_api"]
os.environ["ANTHROPIC_API_KEY"] = config["ANTHROPIC_API_KEY"]

tarPath = "./Doc/WasteDoc" 
def load_document():
    documents = []
    for root, dirs, files in os.walk(tarPath): 
        for file in files:
            full_path = os.path.join(root, file) 
            print (full_path)
            # loader = TextLoader(full_path) 
            # documents = loader.load()
            if (file.endswith('.md')):
                # Prepend the filename to the document content
                file_header = f"--- BEGIN FILE: {file} in {full_path} "
                if(file.endswith(".md")):
                    file_header +="which is md file.---\n"
                else :
                    file_header +="\n"
                # donot forget to append to chromadb
                file_footer = f"\n--- END FILE: {file} ---"
                loader = TextLoader(full_path)
                documents.extend(loader.load())
            elif file.endswith(".pdf"):
                loader = PyPDFLoader(full_path)
                documents.extend(loader.load())
            # loader = PyPDFLoader(full_path) 
            # documents = loader.load() 
        return documents
def split_text(documents):
    text_spliter = RecursiveCharacterTextSplitter(
    chunk_size=900, chunk_overlap=450, length_function=len, add_start_index=True,
    )
    chunks = text_spliter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chuncks.") 
    documents = chunks[0]
    print(documents.page_content)
    print(documents.metadata)
    return chunks

Family_docs = load_document() 
chcks_of_Family = split_text(Family_docs)

dataWaste = "./Data/wasteData"
vectordb = Chroma.from_documents(chcks_of_Family, embedding=OpenAIEmbeddings(), persist_directory=dataWaste)
vectordb.persist()
print(f"Saved {len(chcks_of_Family)} chunks to {dataWaste}.")