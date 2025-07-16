import os
import asyncio
import requests
import streamlit as st
from gpt_researcher import GPTResearcher


FAST_LLM = 'netmind:deepseek-ai/DeepSeek-V3-0324'
FAST_TOKEN_LIMIT = 2000

SMART_LLM = 'netmind:deepseek-ai/DeepSeek-R1-0528'
SMART_TOKEN_LIMIT = 4000

STRATEGIC_LLM = 'netmind:deepseek-ai/DeepSeek-V3-0324'
STRATEGIC_TOKEN_LIMIT = 4000

EMBEDDING = 'netmind:nvidia/NV-Embed-v2'

RETRIEVER = 'mcp'

LANGUAGE = 'english'
SIMILARITY_THRESHOLD = 0.42
TEMPERATURE = 0.1

DEEP_RESEARCH_BREADTH = 3
DEEP_RESEARCH_DEPTH = 2
DEEP_RESEARCH_CONCURRENCY = 4

os.environ['FAST_LLM'] = FAST_LLM
os.environ['FAST_TOKEN_LIMIT'] = str(FAST_TOKEN_LIMIT)
os.environ['SMART_LLM'] = SMART_LLM
os.environ['SMART_TOKEN_LIMIT'] = str(SMART_TOKEN_LIMIT)
os.environ['STRATEGIC_LLM'] = STRATEGIC_LLM
os.environ['STRATEGIC_TOKEN_LIMIT'] = str(STRATEGIC_TOKEN_LIMIT)
os.environ['EMBEDDING'] = EMBEDDING

os.environ['LANGUAGE'] = LANGUAGE
os.environ['SIMILARITY_THRESHOLD'] = str(SIMILARITY_THRESHOLD)
os.environ['TEMPERATURE'] = str(TEMPERATURE)
os.environ['RETRIEVER'] = RETRIEVER

os.environ['DEEP_RESEARCH_BREADTH'] = str(DEEP_RESEARCH_BREADTH)
os.environ['DEEP_RESEARCH_DEPTH'] = str(DEEP_RESEARCH_DEPTH)
os.environ['DEEP_RESEARCH_CONCURRENCY'] = str(DEEP_RESEARCH_CONCURRENCY)


st.title("Deep Researcher")


def query_conf():
    headers = {
        'Host': 'stori-rag.example.com',
    }
    res = requests.get(
        'http://netmind-tailscale-prod-apiserver-18faeaadc8f62680.elb.us-east-1.amazonaws.com:31581/config',
        headers=headers
    ).json()
    return res


config = query_conf()
update_time = config['update_time']
stori_start_time = config['stori_start_time']
competitor_start_time = config['competitor_start_time']
st.markdown(
    f"<p style='font-size:14px; font-style:italic;'>Note: Stori data spans from "
    f"{stori_start_time} to {update_time}, competitor data spans from"
    f" {competitor_start_time} to {update_time}.</p>",
    unsafe_allow_html=True
)

if 'question' not in st.session_state:
    st.session_state.question = ""


question = st.text_area(
    "**Input your question:**", placeholder="please input your question...",
    value=st.session_state.question
)

context_placeholder = st.empty()
report_placeholder = st.empty()


async def get_answer(qus):
    researcher = GPTResearcher(
        query=qus,
        mcp_configs=[
            {
                "name": "rag",
                "command": "python",
                "args": ["rag_mcp.py"],
                "env": {}
            }
        ],
        mcp_strategy='deep'
    )
    st.markdown(
        "<span style='color: green; font-weight: bold;'>search context:</span>",
        unsafe_allow_html=True
    )
    context = await researcher.conduct_research()
    st.markdown(context, unsafe_allow_html=True)

    st.markdown(
        "<span style='color: blue; font-weight: bold;'>report:</span>",
        unsafe_allow_html=True
    )
    report = await researcher.write_report()
    st.markdown(report, unsafe_allow_html=True)


if st.button("submit"):
    if question:
        with st.spinner('Loading...'):
            asyncio.run(get_answer(question))
        st.success("Done!")
    else:
        st.warning("please input your question!")
