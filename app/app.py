import os
import streamlit as st
import langchain

from dotenv import load_dotenv
load_dotenv()

from urllib.error import URLError
from qna.llm import make_qna_chain, get_cache


@st.cache_resource
def startup_qna_backend():
    return make_qna_chain()

@st.cache_resource
def fetch_llm_cache():
    return get_cache()


try:
    qna_chain = startup_qna_backend()
    langchain.llm_cache = fetch_llm_cache()

    default_question = ""
    default_answer = ""

    if 'question' not in st.session_state:
        st.session_state['question'] = default_question
    if 'response' not in st.session_state:
        st.session_state['response'] = {
            "choices" :[{
                "text" : default_answer
            }]
        }

    st.image(os.path.join('app/assets','RedisOpenAI.png'))

    col1, col2 = st.columns([4,2])
    with col1:
        st.write("# Q&A Application")
    # with col2:
    #     with st.expander("Settings"):
    #         st.tokens_response = st.slider("Tokens response length", 100, 500, 400)
    #         st.temperature = st.slider("Temperature", 0.0, 1.0, 0.1)


    question = st.text_input("*Ask thoughtful questions about the **cities' ranks***", default_question)

    if question != '':
        if question != st.session_state['question']:
            st.session_state['question'] = question
            with st.spinner("OpenAI and Redis are working to answer your question..."):
                result = qna_chain({"query": question})
                st.session_state['context'], st.session_state['response'] = result['source_documents'], result['result']
            st.write("### Response")
            st.write(f"{st.session_state['response']}")
            with st.expander("Show Q&A Context Documents"):
                if st.session_state['context']:
                    docs = "\n".join([doc.page_content for doc in st.session_state['context']])
                    st.text(docs)

    st.markdown("____")
    st.markdown("")
    st.write("## How does it work?")
    st.write("""
        The Q&A app exposes a dataset of wikipedia articles hosted by [OpenAI](https://openai.com/) (about the 2020 Summer Olympics). Ask questions like
        *"Which country won the most medals at the 2020 olympics?"* or *"Who won the men's high jump event?"*, and get answers!

        Everything is powered by OpenAI's embedding and generation APIs and [Redis](https://redis.com/redis-enterprise-cloud/overview/) as a vector database.

        There are 3 main steps:

        1. OpenAI's embedding service converts the input question into a query vector (embedding).
        2. Redis' vector search identifies relevant wiki articles in order to create a prompt.
        3. OpenAI's generative model answers the question given the prompt+context.

        See the reference architecture diagram below for more context.
    """)

    st.image(os.path.join('app/assets', 'RedisOpenAI-QnA-Architecture.drawio.png'))



except URLError as e:
    st.error(
        """
        **This demo requires internet access.**
        Connection error: %s
        """
        % e.reason
    )
