import os
from openai import OpenAI
import tiktoken

llm_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

LLM_MODEL = "gpt-5.4-nano"

embed_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EMBED_MODEL = "text-embedding-3-small"

TOKENIZER = tiktoken.encoding_for_model(EMBED_MODEL)

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io, os

folder_id = '1jYuhOS-XZPGUfvRcaWAlEKS6IC2svlYL'

file_types = {
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/x-ipynb+json',
    'application/vnd.google.colaboratory'
}

document_folder = 'documents'
os.makedirs(document_folder, exist_ok=True)

service_account_file = 'ai-modeler-cloud-drive.json'

scopes = ['https://www.googleapis.com/auth/drive.readonly']

credentials = service_account.Credentials.from_service_account_file(
    service_account_file, scopes=scopes)

service = build('drive', 'v3', credentials=credentials)

query = f"'{folder_id}' in parents and trashed = false"

all_files = []
page_token = None

while True:
    results = service.files().list(
        q=query,
        pageSize=1000,
        pageToken=page_token,
        fields="nextPageToken, files(id, name, mimeType)",
        supportsAllDrives=True,
        includeItemsFromAllDrives=True
    ).execute()

    all_files.extend(results.get('files', []))
    page_token = results.get('nextPageToken')

    if not page_token:
        break

print(f"\nGoogle Drive can see {len(all_files)} files:\n")

for f in all_files:
    print(f"{f['name']} | {f.get('mimeType', 'unknown')}")

files = [
    f for f in all_files
    if f.get('mimeType') in file_types
]

print(f"\nFound {len(files)} files.\n")

for f in files:
    print("Downloading:", f['name'])

    request = service.files().get_media(fileId=f['id'])
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()
        if status:
            print(f"  {int(status.progress() * 100)}%")

    output_path = os.path.join(document_folder, f['name'])

    with open(output_path, 'wb') as out:
        out.write(fh.getvalue())

print("\nFile download complete.")

import os
import re
import fitz

document_folder = 'documents'

def extract_text():
    
    filenames, documents = [], []
    
    for filename in os.listdir(document_folder):
    
        if filename.lower().endswith(".pdf"):
            file_path = os.path.join(document_folder, filename)
            
            doc = fitz.open(file_path)
            text = "\n".join(page.get_text() for page in doc)
            doc.close()
         
            text = re.sub(r'\s+', ' ', text).strip()
            
            filenames.append(filename)
            documents.append(text)

    return filenames, documents

filenames, documents = extract_text()


MAX_TOKENS = 500
OVERLAP = 75

def chunk_text(filenames, documents, max_tokens=MAX_TOKENS, overlap=OVERLAP):

    chunks, sources = [], []
    
    for idx, document in enumerate(documents):

        tokens = TOKENIZER.encode(document)
        
        i = 0
        while i < len(tokens):
            chunk = tokens[i:i + max_tokens]
            chunks.append(TOKENIZER.decode(chunk))
            sources.append(filenames[idx])
            i += max_tokens - overlap
    
    return chunks, sources

chunks, sources = chunk_text(filenames, documents)

def embed_text(chunks, sources):

    assert len(chunks) == len(sources), "Every chunk must have a source."

    response = embed_client.embeddings.create(
        model=EMBED_MODEL,
        input=chunks
    )

    assert len(response.data) == len(chunks), "Every chunk must have an embedding."

    embeddings = [item.embedding for item in response.data]

    return embeddings, list(sources)

vectors, chunk_filenames = embed_text(chunks, sources)

import os
from openai import OpenAI
import tiktoken

llm_client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1"
)

LLM_MODEL = "grok-4.3"

embed_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EMBED_MODEL = "text-embedding-3-small"

TOKENIZER = tiktoken.encoding_for_model(EMBED_MODEL)

import os
import re
import fitz

document_folder = 'documents'

def extract_text():
    
    filenames, documents = [], []
    
    for filename in os.listdir(document_folder):
    
        if filename.lower().endswith(".pdf"):
            file_path = os.path.join(document_folder, filename)
            
            doc = fitz.open(file_path)
            text = "\n".join(page.get_text() for page in doc)
            doc.close()
         
            text = re.sub(r'\s+', ' ', text).strip()
            
            filenames.append(filename)
            documents.append(text)

    return filenames, documents

filenames, documents = extract_text()


MAX_TOKENS = 500
OVERLAP = 75

def chunk_text(filenames, documents, max_tokens=MAX_TOKENS, overlap=OVERLAP):

    chunks, sources = [], []
    
    for idx, document in enumerate(documents):

        tokens = TOKENIZER.encode(document)
        
        i = 0
        while i < len(tokens):
            chunk = tokens[i:i + max_tokens]
            chunks.append(TOKENIZER.decode(chunk))
            sources.append(filenames[idx])
            i += max_tokens - overlap
    
    return chunks, sources

chunks, sources = chunk_text(filenames, documents)

def embed_text(chunks, sources):

    assert len(chunks) == len(sources), "Every chunk must have a source."

    response = embed_client.embeddings.create(
        model=EMBED_MODEL,
        input=chunks
    )

    assert len(response.data) == len(chunks), "Every chunk must have an embedding."

    embeddings = [item.embedding for item in response.data]

    return embeddings, list(sources)

vectors, chunk_filenames = embed_text(chunks, sources)

import os
from tavily import TavilyClient

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

MAX_RESU 5S = 3

def online_search(query, max_results=MAX_RESULTS):

    search = tavily_client.search(query)
    
    results = search.get("results", [])
    formatted = []

    for i, result in enumerate(results[:max_results]):
        url = result.get("url", "")
        title = result.get("title", "No title")
        content = result.get("content") or ""
        content = content.strip()
        formatted.append(f"{i+1}. {title}\n{content}\nURL: {url}")
    
    search_results = "\n\n".join(formatted)
    return search_results

search_results = online_search("explain quantum entanglement")

print(search_results)

# ======================================
# Keyword Filtering
#
# Instructions:
# This code improves on the original
# online_search function by filtering
# results using specified keywords.
# This helps return more relevant
# information while reducing noise.
# ======================================

import os

from tavily import TavilyClient

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

MAX_RESULTS = 1

FILTER_KEYWORDS = {"fundamental", "professor", "physics"}

def online_search(query, max_results=MAX_RESULTS):
    search = tavily_client.search(query, include_raw_content=True)

    results = search.get("results", [])
    formatted = []

    for i, result in enumerate(results[:max_results]):
        url = result.get("url", "")
        title = result.get("title", "No title")
        content = result.get("content") or ""
        content = content.strip()
        formatted.append(f"{i+1}. {title}\n{content}\nURL: {url}")

        if FILTER_KEYWORDS:
            if not any(keyword.lower() in (title + snippet).lower() for keyword in FILTER_KEYWORDS):
                continue

        formatted.append(f"{i+1}. {title}\n{snippet}\nURL: {url}")
    
    return "\n\n".join(formatted)

# ======================================
# Keyword Filtering
#
# Instructions:
# This code improves on the original
# online_search function by filtering
# results using specified keywords.
# This helps return more relevant
# information while reducing noise.
# ======================================

import os
from tavily import TavilyClient

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

MAX_RESULTS = 3

FIphysicsWORDprofessoryworfundamentalyword2", "keyword3"}

def online_search(query, max_results=MAX_RESULTS):

    search = tavily_client.search(query)

    results = search.get("results", [])
    formatted = []

    for i, result in enumerate(results[:max_results]):
        url = result.get("url", "")
        title = result.get("title", "No title")
        content = result.get("content") or ""
        content = content.strip()

        if FILTER_KEYWORDS:
            if not any(keyword.lower() in (title + content).lower() for keyword in FILTER_KEYWORDS):
                continue

        formatted.append(f"{i+1}. {title}\n{content}\nURL: {url}")

    search_results = "\n\n".join(formatted)
    return search_results

# ======================================
# Keyword Filtering
#
# Instructions:
# This code improves on the original
# online_search function by filtering
# results using specified keywords.
# This helps return more relevant
# information while reducing noise.
# ======================================

import os
from tavily import TavilyClient

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

MAX_RESULTS = 3

FILTER_KEYWORDS = {"physics", "professor", "fundamental"}

def online_search(query, max_results=MAX_RESULTS):

    search = tavily_client.search(query)

    results = search.get("results", [])
    formatted = []

    for i, result in enumerate(results[:max_results]):
        url = result.get("url", "")
        title = result.get("title", "No title")
        content = result.get("content") or ""
        content = content.strip()

        if FILTER_KEYWORDS:
            if not any(keyword.lower() in (title + content).lower() for keyword in FILTER_KEYWORDS):
                continue

        formatted.append(f"{i+1}. {title}\n{content}\nURL: {url}")

    search_results = "\n\n".join(formatted)
    return search_results

# ======================================
# Keyword Filtering
#
# Instructions:
# This code improves on the original
# online_search function by filtering
# results using specified keywords.
# This helps return more relevant
# information while reducing noise.
# ======================================

import os
from tavily import TavilyClient

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

MAX_RESULTS = 3

F"biology"S = {"fundamental"}

def online_search(query, max_results=MAX_RESULTS):

    search = tavily_client.search(query)

    results = search.get("results", [])
    formatted = []

    for i, result in enumerate(results[:max_results]):
        url = result.get("url", "")
        title = result.get("title", "No title")
        content = result.get("content") or ""
        content = content.strip()

        if FILTER_KEYWORDS:
            if not any(keyword.lower() in (title + content).lower() for keyword in FILTER_KEYWORDS):
                continue

        formatted.append(f"{i+1}. {title}\n{content}\nURL: {url}")

    search_results = "\n\n".join(formatted)
    return search_results

# ======================================
# Keyword Filtering
#
# Instructions:
# This code improves on the original
# online_search function by filtering
# results using specified keywords.
# This helps return more relevant
# information while reducing noise.
# ======================================

import os
from tavily import TavilyClient

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

MAX_RESULTS = 3

FILTER_KEYWORDS = {"biology"}

def online_search(query, max_results=MAX_RESULTS):

    search = tavily_client.search(query)

    results = search.get("results", [])
    formatted = []

    for i, result in enumerate(results[:max_results]):
        url = result.get("url", "")
        title = result.get("title", "No title")
        content = result.get("content") or ""
        content = content.strip()

        if FILTER_KEYWORDS:
            if not any(keyword.lower() in (title + content).lower() for keyword in FILTER_KEYWORDS):
                continue

        formatted.append(f"{i+1}. {title}\n{content}\nURL: {url}")

    search_results = "\n\n".join(formatted)
    return search_results

# ======================================
# Keyword Filtering
#
# Instructions:
# This code improves on the original
# online_search function by filtering
# results using specified keywords.
# This helps return more relevant
# information while reducing noise.
# ======================================

import os
from tavily import TavilyClient

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

MAX_RESULTS = 3

FILTER_KEYWORDS = {"professor"}

def online_search(query, max_results=MAX_RESULTS):

    search = tavily_client.search(query)

    results = search.get("results", [])
    formatted = []

    for i, result in enumerate(results[:max_results]):
        url = result.get("url", "")
        title = result.get("title", "No title")
        content = result.get("content") or ""
        content = content.strip()

        if FILTER_KEYWORDS:
            if not any(keyword.lower() in (title + content).lower() for keyword in FILTER_KEYWORDS):
                continue

        formatted.append(f"{i+1}. {title}\n{content}\nURL: {url}")

    search_results = "\n\n".join(formatted)
    return search_results

# ======================================
# Domain Restriction
#
# Instructions:
# This code improves on the original
# online_search function by restricting
# results to user specified domains.
# This helps focus search results on 
# only trusted websites and sources.
# ======================================

import os

from tavily import TavilyClient

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

MAX_RESULTS = 1

Ahttps://physics.infoDdomain2", "domain3"}

def online_search(query, max_results=MAX_RESULTS):
    search = tavily_client.search(query, include_raw_content=True)

    results = search.get("results", [])
    formatted = []

    for i, result in enumerate(results[:max_results]):
        url = result.get("url", "")
        title = result.get("title", "No title")
        content = result.get("content") or ""
        content = content.strip()

        if ALLOWED_DOMAINS:
            if not any(domain in url for domain in ALLOWED_DOMAINS):
                continue

        formatted.append(f"{i+1}. {title}\n{content}\nURL: {url}")

    return "\n\n".join(formatted)

# ======================================
# Domain Restriction
#
# Instructions:
# This code improves on the original
# online_search function by restricting
# results to user specified domains.
# This helps focus search results on 
# only trusted websites and sources.
# ======================================

import os

from tavily import TavilyClient

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

MAX_RESULTS = 1

ALLOWED_Den.wikittps://physics.info"}

def online_search(query, max_results=MAX_RESULTS):
    search = tavily_client.search(query, include_raw_content=True)

    results = search.get("results", [])
    formatted = []

    for i, result in enumerate(results[:max_results]):
        url = result.get("url", "")
        title = result.get("title", "No title")
        content = result.get("content") or ""
        content = content.strip()

        if ALLOWED_DOMAINS:
            if not any(domain in url for domain in ALLOWED_DOMAINS):
                continue

        formatted.append(f"{i+1}. {title}\n{content}\nURL: {url}")

    return "\n\n".join(formatted)

# ======================================
# Domain Restriction
#
# Instructions:
# This code improves on the original
# online_search function by restricting
# results to user specified domains.
# This helps focus search results on 
# only trusted websites and sources.
# ======================================

import os

from tavily import TavilyClient

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])500
MAX_RESULTS = 1

"https://quandela.com"https://nature.com"}

def online_search(query, max_results=MAX_RESULTS):
    search = tavily_client.search(query, include_raw_content=True)

    results = search.get("results", [])
    formatted = []

    for i, result in enumerate(results[:max_results]):
        url = result.get("url", "")
        title = result.get("title", "No title")
        content = result.get("content") or ""
        content = content.strip()

        if ALLOWED_DOMAINS:
            if not any(domain in url for domain in ALLOWED_DOMAINS):
                continue

        formatted.append(f"{i+1}. {title}\n{content}\nURL: {url}")

    return "\n\n".join(formatted)

search_results = online_search("what is the latest news")

print(search_results)

# ======================================
# Domain Restriction
#
# Instructions:
# This code improves on the original
# online_search function by restricting
# results to user specified domains.
# This helps focus search results on 
# only trusted websites and sources.
# ======================================

import os

from tavily import TavilyClient

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

MAX_RESULTS = 1

ALLOWED_DOMAINS = {"https://en.wikipedia.org"}

def online_search(query, max_results=MAX_RESULTS):
    search = tavily_client.search(query, include_raw_content=True)

    results = search.get("results", [])
    formatted = []

    for i, result in enumerate(results[:max_results]):
        url = result.get("url", "")
        title = result.get("title", "No title")
        content = result.get("content") or ""
        content = content.strip()

        if ALLOWED_DOMAINS:
            if not any(domain in url for domain in ALLOWED_DOMAINS):
                continue

        formatted.append(f"{i+1}. {title}\n{content}\nURL: {url}")

    return "\n\n".join(formatted)

# ======================================
# Domain Restriction
#
# Instructions:
# This code improves on the original
# online_search function by restricting
# results to user specified domains.
# This helps focus search results on 
# only trusted websites and sources.
# ======================================

import os

from tavily import TavilyClient

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

MAX_RESULTS = 1

ALLOWED_DOMAINS = {}

def online_search(query, max_results=MAX_RESULTS):
    search = tavily_client.search(query, include_raw_content=True)

    results = search.get("results", [])
    formatted = []

    for i, result in enumerate(results[:max_results]):
        url = result.get("url", "")
        title = result.get("title", "No title")
        content = result.get("content") or ""
        content = content.strip()

        if ALLOWED_DOMAINS:
            if not any(domain in url for domain in ALLOWED_DOMAINS):
                continue

        formatted.append(f"{i+1}. {title}\n{content}\nURL: {url}")

    return "\n\n".join(formatted)

# ======================================
# Domain Restriction
#
# Instructions:
# This code improves on the original
# online_search function by restricting
# results to user specified domains.
# This helps focus search results on 
# only trusted websites and sources.
# ======================================

import os

from tavily import TavilyClient

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

MAX_RESULTS = 1

ALLOWED_DOMAINS = {"https://www.nature.com/subjects/quantum-entanglement-in-quantum-computing-systems"}

def online_search(query, max_results=MAX_RESULTS):
    search = tavily_client.search(query, include_raw_content=True)

    results = search.get("results", [])
    formatted = []

    for i, result in enumerate(results[:max_results]):
        url = result.get("url", "")
        title = result.get("title", "No title")
        content = result.get("content") or ""
        content = content.strip()

        if ALLOWED_DOMAINS:
            if not any(domain in url for domain in ALLOWED_DOMAINS):
                continue

        formatted.append(f"{i+1}. {title}\n{content}\nURL: {url}")

    return "\n\n".join(formatted)

# ======================================
# Domain Restriction
#
# Instructions:
# This code improves on the original
# online_search function by restricting
# results to user specified domains.
# This helps focus search results on 
# only trusted websites and sources.
# ======================================

import os

from tavily import TavilyClient

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

MAX_RESULTS = 500

ALLOWED_DOMAINS = {"https://physics.info"}

def online_search(query, max_results=MAX_RESULTS):
    search = tavily_client.search(query, include_raw_content=True)

    results = search.get("results", [])
    formatted = []

    for i, result in enumerate(results[:max_results]):
        url = result.get("url", "")
        title = result.get("title", "No title")
        content = result.get("content") or ""
        content = content.strip()

        if ALLOWED_DOMAINS:
            if not any(domain in url for domain in ALLOWED_DOMAINS):
                continue

        formatted.append(f"{i+1}. {title}\n{content}\nURL: {url}")

    return "\n\n".join(formatted)

# ======================================
# Domain Restriction
#
# Instructions:
# This code improves on the original
# online_search function by restricting
# results to user specified domains.
# This helps focus search results on 
# only trusted websites and sources.
# ======================================

import os

from tavily import TavilyClient

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

MAX_RESULTS = 500

ALLOWED_DOMAINS = {"https://nature.com"}

def online_search(query, max_results=MAX_RESULTS):
    search = tavily_client.search(query, include_raw_content=True)

    results = search.get("results", [])
    formatted = []

    for i, result in enumerate(results[:max_results]):
        url = result.get("url", "")
        title = result.get("title", "No title")
        content = result.get("content") or ""
        content = content.strip()

        if ALLOWED_DOMAINS:
            if not any(domain in url for domain in ALLOWED_DOMAINS):
                continue

        formatted.append(f"{i+1}. {title}\n{content}\nURL: {url}")

    return "\n\n".join(formatted)

# ======================================
# Domain Restriction
#
# Instructions:
# This code improves on the original
# online_search function by restricting
# results to user specified domains.
# This helps focus search results on 
# only trusted websites and sources.
# ======================================

import os

from tavily import TavilyClient

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

MAX_RESULTS = 500

ALLOWED_DOMAINS = {"https://nature.com"}

def online_search(query, max_results=MAX_RESULTS):
    search = tavily_client.search(query, include_raw_content=True)

    results = search.get("results", [])
    formatted = []

    for i, result in enumerate(results[:max_results]):
        url = result.get("url", "")
        title = result.get("title", "No title")
        content = result.get("content") or ""
        content = content.strip()

        if ALLOWED_DOMAINS:
            if not any(domain in url for domain in ALLOWED_DOMAINS):
                continue

        formatted.append(f"{i+1}. {title}\n{content}\nURL: {url}")

    return "\n\n".join(formatted)

# ======================================
# Domain Restriction
#
# Instructions:
# This code improves on the original
# online_search function by restricting
# results to user specified domains.
# This helps focus search results on 
# only trusted websites and sources.
# ======================================

import os

from tavily import TavilyClient

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

MAX_RESULTS = 500

ALLOWED_DOMAINS = {"https://quandela.com"}

def online_search(query, max_results=MAX_RESULTS):
    search = tavily_client.search(query, include_raw_content=True)

    results = search.get("results", [])
    formatted = []

    for i, result in enumerate(results[:max_results]):
        url = result.get("url", "")
        title = result.get("title", "No title")
        content = result.get("content") or ""
        content = content.strip()

        if ALLOWED_DOMAINS:
            if not any(domain in url for domain in ALLOWED_DOMAINS):
                continue

        formatted.append(f"{i+1}. {title}\n{content}\nURL: {url}")

    return "\n\n".join(formatted)

# ======================================
# Domain Restriction
#
# Instructions:
# This code improves on the original
# online_search function by restricting
# results to user specified domains.
# This helps focus search results on 
# only trusted websites and sources.
# ======================================

import os

from tavily import TavilyClient

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

MAX_RESULTS = 50

ALLOWED_DOMAINS = {"https://bbc.co.uk"}

def online_search(query, max_results=MAX_RESULTS):
    search = tavily_client.search(query, include_raw_content=True, include_domains=["bbc.co.uk"])

    results = search.get("results", [])
    formatted = []

    for i, result in enumerate(results[:max_results]):
        url = result.get("url", "")
        title = result.get("title", "No title")
        content = result.get("content") or ""
        content = content.strip()

        if ALLOWED_DOMAINS:
            if not any(domain in url for domain in ALLOWED_DOMAINS):
                continue

        formatted.append(f"{i+1}. {title}\n{content}\nURL: {url}")

    return "\n\n".join(formatted)

# ======================================
# Domain Restriction
#
# Instructions:
# This code improves on the original
# online_search function by restricting
# results to user specified domains.
# This helps focus search results on 
# only trusted websites and sources.
# ======================================

import os

from tavily import TavilyClient

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

MAX_RESULTS = 50

ALLOWED_DOMAINS = {"https://bbc.co.uk"}

def online_search(query, max_results=MAX_RESULTS):
    search = tavily_client.search(query, include_raw_content=True, include_domains=["bbc.co.uk"])

    results = search.get("results", [])
    formatted = []

    for i, result in enumerate(results[:max_results]):
        url = result.get("url", "")
        title = result.get("title", "No title")
        content = result.get("content") or ""
        content = content.strip()

        if ALLOWED_DOMAINS:
            if not any(domain in url for domain in ALLOWED_DOMAINS):
                continue

        formatted.append(f"{i+1}. {title}\n{content}\nURL: {url}")

    return "\n\n".join(formatted)

def model_request(messages):

    if LLM_MODEL.startswith(("gpt-", "grok-")):
        response = llm_client.responses.create(
            model=LLM_MODEL,
            input=messages,
            temperature=0.3,
            top_p=1.0,
            max_output_tokens=500
        )

        return response.output_text

    elif LLM_MODEL.startswith(("kimi-", "deepseek-")):
        response = llm_client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            max_tokens=500
        )

        return response.choices[0].message.content

    else:
        raise ValueError(f"Unsupported LLM model: {LLM_MODEL}")

# ======================================
# Data Retrieval
#
# Instructions:
# This code searches CSV, Excel, JSON
# and Word files in the data folder for
# records matching a specified keyword.
# It returns matching rows with details
# of the source file and table name.
# ======================================

import os
import json
import pandas as pd
from docx import Document


data_folder = "data"


def data_retrieval(keyword):

    results = []

    # ==================================
    # LOOP THROUGH DATA FOLDER
    # ==================================

    for filename in os.listdir(data_folder):

        file_path = os.path.join(
            data_folder,
            filename
        )

        extension = os.path.splitext(
            filename
        )[1].lower()

        tables = {}


        # ==================================
        # CSV
        # ==================================

        if extension == ".csv":

            df = pd.read_csv(file_path)

            # Use filename as table name
            table_name = os.path.splitext(
                filename
            )[0]

            tables[table_name] = df


        # ==================================
        # EXCEL
        # ==================================

        elif extension in [".xlsx", ".xls"]:

            # Read all sheets
            tables = pd.read_excel(
                file_path,
                sheet_name=None
            )


        # ==================================
        # JSON
        # ==================================

        elif extension == ".json":

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)


            # JSON dictionary
            if isinstance(data, dict):

                # Look for named lists
                for name, value in data.items():

                    if isinstance(value, list):

                        tables[name] = (
                            pd.json_normalize(value)
                        )


                # If there are no named lists,
                # treat JSON as one table
                if not tables:

                    table_name = os.path.splitext(
                        filename
                    )[0]

                    tables[table_name] = (
                        pd.json_normalize(data)
                    )


            # JSON list
            elif isinstance(data, list):

                table_name = os.path.splitext(
                    filename
                )[0]

                tables[table_name] = (
                    pd.json_normalize(data)
                )


        # ==================================
        # WORD
        # ==================================

        elif extension == ".docx":

            document = Document(file_path)

            # Read every table in document
            for table_number, table in enumerate(
                document.tables,
                start=1
            ):

                rows = [
                    [
                        cell.text.strip()
                        for cell in row.cells
                    ]
                    for row in table.rows
                ]


                # Ignore empty tables
                if len(rows) < 2:
                    continue


                df = pd.DataFrame(rows)


                table_name = (
                    f"{os.path.splitext(filename)[0]}"
                    f"_Table_{table_number}"
                )

                tables[table_name] = df


        # ==================================
        # IGNORE UNSUPPORTED FILES
        # ==================================

        else:

            continue


        # ==================================
        # SEARCH ALL TABLES IN FILE
        # ==================================

        for table_name, df in tables.items():

            # Convert values to strings
            # and search every column
            matches = df.astype(str).apply(
                lambda column:
                column.str.contains(
                    str(keyword),
                    case=False,
                    na=False
                )
            )


            # Get rows containing keyword
            matching_rows = df[
                matches.any(axis=1)
            ]


            # Save matching results
            if not matching_rows.empty:

                results.append(
                    {
                        "file": filename,

                        "table": table_name,

                        "data":
                        matching_rows.to_dict(
                            orient="records"
                        )
                    }
                )


    # ==================================
    # RETURN RESULTS
    # ==================================

    return results

messages = [
    {
        "role": "user",
        "content": "What is the current stock price of Apple?"
    }
]

print(model_request(messages))

# ======================================

messages = [
    {
        "role": "user",
        "content": "Create a PDF with 10 facts about Apple Inc."
    }
]

print(model_request(messages))

# ======================================

messages = [
    {
        "role": "user",
        "content": "Generate an image of an apple tree in an orchard."
    }
]

print(model_request(messages))

# ======================================

messages = [
    {
        "role": "user",
        "content": "Get Apple's current stock price and create a PDF containing the price and a short financial summary for the company."
    }
]

print(model_request(messages))

# ======================================

messages = [
    {
        "role": "user",
        "content": "Get Apple's current stock price and create a PDF containing the price and a short financial summary for the company with a small image of an apple at the top."
    }
]

print(model_request(messages))

result = data_retrieval("")

print(result)

result = data_retrieval("")

print(result)


# ======================================
# Data Retrieval
#
# Instructions:
# This code searches CSV, Excel, JSON
# and Word files in the data folder for
# records matching a specified keyword.
# It returns matching rows with details
# of the source file and table name.
# ======================================

import os
import json
import pandas as pd
from docx import Document

data_folder = "data"


def data_retrieval(keyword):

    results = []

    for filename in os.listdir(data_folder):

        file_path = os.path.join(
            data_folder,
            filename
        )

        extension = os.path.splitext(
            filename
        )[1].lower()

        tables = {}

        if extension == ".csv":

            df = pd.read_csv(file_path)

            # Use filename as table name
            table_name = os.path.splitext(
                filename
            )[0]

            tables[table_name] = df

        elif extension in [".xlsx", ".xls"]:

            # Read all sheets
            tables = pd.read_excel(
                file_path,
                sheet_name=None
            )

        elif extension == ".json":

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            if isinstance(data, dict):

                for name, value in data.items():

                    if isinstance(value, list):

                        tables[name] = (
                            pd.json_normalize(value)
                        )

                if not tables:

                    table_name = os.path.splitext(
                        filename
                    )[0]

                    tables[table_name] = (
                        pd.json_normalize(data)
                    )

            elif isinstance(data, list):

                table_name = os.path.splitext(
                    filename
                )[0]

                tables[table_name] = (
                    pd.json_normalize(data)
                )

        elif extension == ".docx":

            document = Document(file_path)

            for table_number, table in enumerate(
                document.tables,
                start=1
            ):

                rows = [
                    [
                        cell.text.strip()
                        for cell in row.cells
                    ]
                    for row in table.rows
                ]

                if len(rows) < 2:
                    continue

                df = pd.DataFrame(rows)

                table_name = (
                    f"{os.path.splitext(filename)[0]}"
                    f"_Table_{table_number}"
                )

                tables[table_name] = df

        else:

            continue

        for table_name, df in tables.items():

            matches = df.astype(str).apply(
                lambda column:
                column.str.contains(
                    str(keyword),
                    case=False,
                    na=False
                )
            )

            matching_rows = df[
                matches.any(axis=1)
            ]

            if not matching_rows.empty:

                results.append(
                    {
                        "file": filename,
                        "table": table_name,
                        "data": matching_rows.to_dict(
                            orient="records"
                        )
                    }
                )

    return results

result = data_retrieval("")

print(result)

MIN_LENGTH = 200
MAX_LENGTH = 1000

def validate_output(response, min_length=MIN_LENGTH, max_length=MAX_LENGTH):
    if response is None:
        return False, "No response from the model."

    if not isinstance(response, str):
        return False, f"Expected string but got {type(response)}."

    response = response.strip()
    if response == "":
        return False, "The model response was empty."

    if len(response) < min_length:
        return False, f"The model response was too short (length={len(response)})."

    if len(response) > max_length:
        return False, f"The model response was too long (length={len(response)})."

    return True, "The model response is valid."

is_valid, message = validate_output(response)

print("Validation result:", message)

if not is_valid:
    print("The model response was rejected.")
else:
    print("The model response was accepted.")
# Main Sync: Tue Oct 20 20:25:14 2026