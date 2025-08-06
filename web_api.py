# config log at first
import logging

from custom_prompt import Report_Custom_Prompt

logging.basicConfig(format='[%(asctime)s]-[%(name)s]-[%(levelname)s] : %(message)s')
logging.basicConfig(level=logging.DEBUG)

import os
import asyncio
import requests
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from gpt_researcher import GPTResearcher

# Copy all environment configurations from web.py
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
os.environ['NETMIND_API_KEY'] = "098ba1186ed849bca1180a75383075b7"
os.environ['MCP_CHOOSE_TH'] = "6"

app = FastAPI()

def query_conf():
    headers = {
        'Host': 'stori-rag.example.com',
    }
    res = requests.get(
        'http://netmind-tailscale-prod-apiserver-18faeaadc8f62680.elb.us-east-1.amazonaws.com:31581/config',
        headers=headers
    ).json()
    return res

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            # Receive query from client
            data = await websocket.receive_text()
            query_data = json.loads(data)
            query = query_data.get("query", "")
            
            if not query:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Query is required"
                }))
                continue
            
            # Send processing start message
            await websocket.send_text(json.dumps({
                "type": "status",
                "message": "Starting research process..."
            }))
            
            try:
                # Initialize researcher
                researcher = GPTResearcher(
                    query=query,
                    mcp_configs=[
                        {
                            "name": "rag",
                            "command": "python",
                            "args": ["rag_mcp.py"],
                            "env": {}
                        }
                    ],
                    mcp_strategy='deep',
                    custom_websocket=websocket,
                )
                
                # Send context search message
                await websocket.send_text(json.dumps({
                    "type": "status",
                    "message": "Searching context..."
                }))
                
                # Conduct research
                await researcher.conduct_research()
                retrival_result_list = researcher.research_conductor.mcp_retrival_results
                
                # Send context results
                for result in retrival_result_list:
                    await websocket.send_text(json.dumps({
                        "type": "retrival_result",
                        "content": result
                    }))
                
                # Send report generation message
                await websocket.send_text(json.dumps({
                    "type": "status",
                    "message": "Generating report..."
                }))
                
                # Generate report
                report = await researcher.write_report(custom_prompt=Report_Custom_Prompt)
                
                # Send final report
                await websocket.send_text(json.dumps({
                    "type": "report",
                    "content": report
                }))
                
                # Send completion message
                await websocket.send_text(json.dumps({
                    "type": "status",
                    "message": "Research completed successfully!"
                }))
                
            except Exception as e:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": f"Error during research: {str(e)}"
                }))
                
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {str(e)}")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    """Return the index.html file"""
    with open("index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 