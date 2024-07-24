from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import RetrievalQA
from langchain.document_loaders import DirectoryLoader
from langchain.vectorstores import FAISS
from langchain.llms import GPT4All
from transformers import AutoTokenizer, AutoModelForCausalLM
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.llms import CTransformers
from PyPDF2 import PdfReader
import os
import pickle

class ProcBase:
    def get_PDF_text(self,pdf_docs):
        '''
        Function is responsible for extracting text from PDF files 

        ARGS    : pdf_docs (PDF files)
        RETUNR  : text from the pdf
        '''
        text = ''
        for pdf in pdf_docs:
            pdf_reader = PdfReader(pdf)        # CREATING A PDF READER FOR EACH PAGE 
            for page in pdf_reader.pages:      # LOOPING THROUGH EACH PAGE IN THE PDF
                text += page.extract_text()    # EXTRACTING THE CONTENT OF EACH PAGE AND APPENDING IT TO THE TEXT VARIABEL
        return text
    
    def create_text_chunks(self, raw_text, chunk_size, chunk_overlap):
        '''
        Function is responsible for converting raw_text into chunks

        ARGS    : raw_text 
        RETURN  : chunks from raw text
        '''
        text_splitter = RecursiveCharacterTextSplitter(chunk_size         = chunk_size,
                                                chunk_overlap             = chunk_overlap,
                                                length_function           = len)
        
        chunk = text_splitter.split_text(text = raw_text)

        return chunk

    def vectorStore(self,text_chunks,file_name):
        '''
        Function is responsible for converting the chunks into vectors and storing them into a chroma db

        ARGS    : text_chunks
        return  : A vector store for the embeddings
        '''

        instructor_embeddings = HuggingFaceInstructEmbeddings(model_name      = 'all-mpnet-base-v2',
                                                                model_kwargs  = {'device' : 'cpu'})

        print(f"Embedding has started for the new file : {file_name}")
        vector_db = FAISS.from_texts(text_chunks,
                                        instructor_embeddings,
                                        )
        with open(f'C:\\Users\\aariz\\codes\LLMS\\PDF_Chatting\\Llama\OpsLib\\Vector_db\\{file_name}.pkl', 'wb') as new_db:
            pickle.dump(vector_db, new_db)

        return vector_db
    
    def generate_answer(self,similar_search,query):
        '''
        ARGS    : similar search from the vector DB with respect to the query, query 
        return  : Response generated by the LLM
        '''
        model_path = "C:\\Users\\aariz\\codes\\LLMS\\LLM_model\\llama-2-7b-chat.ggmlv3.q8_0.bin"

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"No LLM found at the file location : {model_path}")

        llmodel = CTransformers(model = model_path,
                                model_type = 'llama',
                                max_tokens = 512,
                                temperature = 0.7)
        
        print("------------------")
        conv_chain = load_qa_chain(llmodel, chain_type='stuff')
        print("------------------")
        print(conv_chain.run(input_documents = similar_search, question = query))
        print("------------------")
        return conv_chain.run(input_documents = similar_search, question = query)