# standard imports
import os
from dotenv import load_dotenv
# file system imports
import glob
from langchain_community.document_loaders import DirectoryLoader, TextLoader
# vector store imports
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
# other imports
from pydantic import BaseModel, Field
from langchain_core.documents import Document
from litellm import completion
from tqdm import tqdm

# load the environment variables
load_dotenv()

# global variables
REFERENCE_BASE_PATH = "twin_reference_base/"
DB_NAME = "twin_db"
EMBEDDING_MODEL = "text-embedding-3-large"
AVERAGE_CHUNK_SIZE = 100
CHUNKING_MODEL = "gpt-4.1-nano"

# define chunk structure
class Chunk(BaseModel):
    headline: str = Field(
        description="A brief heading for this chunk, typically a few words, that is most likely to be surfaced in a query"
    )
    summary: str = Field(
        description="A few sentences summarizing the content of this chunk to answer common questions"
    )
    content: str = Field(
        description="The original text of this chunk from the provided document, exactly as is, not changed in any way"
    )
    def as_result(self, document):
        return Document(
            page_content=self.headline + "\n\n" +self.summary + "\n\n" + self.content,
            metadata=document.metadata
        )

class Chunks(BaseModel):
    chunks: list[Chunk]

# load in the documents
def load_documents(base_path):
    documents = []
    loader = DirectoryLoader(base_path, glob="**/*.md", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
    folder_docs = loader.load() # load the documents
    for doc in folder_docs:
        doc.metadata['type'] = doc.metadata['source'].split('\\')[-2] # get the doc type
        doc.page_content = doc.page_content.strip() # strip the whitespace from the content
        documents.append(doc) # append the document to the list
    print(f"Found {len(documents)} documents")
    return documents

# setup the semantic splitter
def make_prompt(document):
    how_many = (len(document.page_content) // AVERAGE_CHUNK_SIZE) + 1
    return f"""
You take a document and you split the document into overlapping chunks for a KnowledgeBase.

The document is a record of a project that I have worked on or that summarizes my skills and experience.
The document is of type: {document.metadata["type"]}
The document has been retrieved from: {document.metadata["source"]}

A chatbot will use these chunks to answer questions about my projects, skills and experience.
You should divide up the document as you see fit, being sure that the entire document is returned across the chunks - don't leave anything out.
This document should probably be split into at least {how_many} chunks, but you can have more or less as appropriate, ensuring that there are individual chunks to answer specific questions.
There should be overlap between the chunks as appropriate; typically about 25% overlap or about 50 words, so you have the same text in multiple chunks for best retrieval results.

For each chunk, you should provide a headline, a summary, and the original text of the chunk.
Together your chunks should represent the entire document with overlap.

Here is the document:

{document.page_content}

Respond with the chunks.
"""

def make_message(document):
    return [
        {"role": "user", "content": make_prompt(document)},
    ]

# process the documents and create the chunks
def process_document(document):
    message = make_message(document)
    response = completion(model=CHUNKING_MODEL, messages=message, response_format=Chunks)
    reply = response.choices[0].message.content
    doc_as_chunks = Chunks.model_validate_json(reply)
    return [chunk.as_result(document) for chunk in doc_as_chunks.chunks]

def create_chunks(documents):
    chunks = []
    for doc in tqdm(documents):
        chunks.extend(process_document(doc))
    return chunks

# create the vector store
def create_embeddings(chunks):
    # create the embedding model
    emb = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    # delete the collection if it exists
    if os.path.exists(DB_NAME):
        Chroma(persist_directory=DB_NAME, embedding_function=emb).delete_collection()
    # create the vector store
    vectorstore = Chroma.from_documents(
        documents = chunks, 
        embedding=emb, 
        persist_directory=DB_NAME)
    print(f"Vectorstore created with {vectorstore._collection.count()} documents")

# run the script
if __name__ == "__main__":
    documents = load_documents(REFERENCE_BASE_PATH)
    chunks = create_chunks(documents)
    create_embeddings(chunks)
    print("Ingestion complete")