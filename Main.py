import streamlit as st
from OpsLib.core_operations import ProcBase
import os
import pickle
from pathlib import Path

procbase = ProcBase()

def main():
    st.set_page_config(page_title = 'Chat with multiple documents', page_icon = ':books:')
    st.header("Chat with your PDF :books: ")

    pdf_docs = st.file_uploader("Upload your PDF ", type = 'pdf', accept_multiple_files = True)
    if pdf_docs is not None:

        raw_text = procbase.get_PDF_text(pdf_docs = pdf_docs)

        chunks = procbase.create_text_chunks(raw_text, 800, 150)

        filename = ''

        if pdf_docs:
            for uploaded_file in pdf_docs:
                filename = uploaded_file.name
                st.write("Filename: ", filename)

            
            if os.path.exists(f'C:\\Users\\aariz\codes\\LLMS\PDF_Chatting\\Llama\\OpsLib\\Vector_db\\{filename}.pkl'):
                with open(f'C:\\Users\\aariz\\codes\LLMS\\PDF_Chatting\\Llama\OpsLib\\Vector_db\\{filename}.pkl', 'rb') as db:
                    vector_db = pickle.load(db)
                st.write(f"Embeddings loaded from the disk for the file : {filename}")
            else:
                st.write(f"Embedding started for the new file : {filename}")
                vector_db = procbase.vectorStore(chunks, filename)
                st.write(f"Embedding completed for the new file : {filename}")
                print(f"Embedding completed for the new file : {filename}")

        # TAKING USER INPUT
        query = st.text_input("Ask a question about your PDF file : ")
        response = ''
            
        # SIMILAR SEARCH 
        if query:
            similar_search = vector_db.similarity_search(query=query, k=1)
            st.write(similar_search)
            # print(similar_search)
            response = procbase.generate_answer(similar_search, query)
            # print("The response generated : " ,response)
            st.write(response)


if __name__ == "__main__":
    main()


                


                