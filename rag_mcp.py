from mcp.server.fastmcp import FastMCP
from typing import Literal
import httpx

mcp = FastMCP("rag")


async def get_company_data(query: str, company: str, platform: str, language: str = "English") -> str:
    url = f"http://netmind-tailscale-prod-apiserver-18faeaadc8f62680.elb.us-east-1.amazonaws.com:31581/query"
    headers = {
        'host': 'stori-rag.example.com'
    }
    data = {
        "query": query,
        "company": company,
        "platform": platform,
        "mode": "mix",
        "language": language,
        "stream": False
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data, timeout=2 * 60, headers=headers)
        if response.status_code != 200:
            raise httpx.HTTPStatusError(
                f"Request failed with status code {response.status_code}",
                request=response.request, response=response
            )
        return response.text


@mcp.tool()
async def query_stori(
        query: str,
        platform: Literal["Google Play", "App Store", "Facebook", "Instagram", "LinkedIn", "TikTok", "X"],
        language: Literal["English", "Español", "简体中文"] = "English"
) -> str:
    """
    A question-answering tool for querying user-generated content about Stori across multiple social and app platforms using a Retrieval-Augmented Generation (RAG) system.

    This tool allows users to ask natural language questions about the company "Stori", and retrieves answers based on user comments and feedback collected from various public online platforms, including:
    - Google Play app reviews
    - Apple App Store app reviews
    - Facebook post comments
    - Instagram post comments
    - LinkedIn post comments
    - TikTok post comments
    - X (formerly Twitter) post comments

    The tool supports multilingual answers, and will return the answer in the specified language (English, Español, or 简体中文). The response is generated using a RAG-based pipeline that retrieves relevant comments and synthesizes an informative, fluent answer.

    """
    company = "Stori"
    return await get_company_data(query, company, platform, language)


@mcp.tool()
async def query_nubank(
        query: str,
        platform: Literal["Google Play", "App Store", "Facebook"],
        language: Literal["English", "Español", "简体中文"] = "English",
) -> str:
    """
    A question-answering tool for querying public user feedback about Nubank using a Retrieval-Augmented Generation (RAG) system.

    This tool allows users to ask questions about the digital bank "Nubank", and returns synthesized answers based on real user reviews and comments from the following platforms:
    - Google Play app reviews
    - Apple App Store app reviews
    - Facebook post comments

    The system retrieves relevant data and uses a RAG pipeline to generate a concise, accurate answer. It supports multilingual responses in English, Spanish, or Simplified Chinese.

    """
    company = "Nubank"
    return await get_company_data(query, company, platform, language)
    pass


# klar = 'Klar'
@mcp.tool()
async def query_klar(
        query: str,
        platform: Literal["Google Play", "App Store", "Facebook"],
        language: Literal["English", "Español", "简体中文"] = "English",
) -> str:
    """
    A question-answering tool for retrieving user feedback about Klar from public sources using a Retrieval-Augmented Generation (RAG) system.

    This tool enables users to ask natural language questions about the financial company "Klar", and get informative answers based on real user-generated content collected from the following platforms:
    - Google Play app reviews
    - Apple App Store app reviews
    - Facebook post comments

    The tool supports multilingual output in English, Spanish, and Simplified Chinese. It retrieves the most relevant user comments from the specified platform and synthesizes a coherent answer using RAG techniques.

    """
    company = "Klar"
    return await get_company_data(query, company, platform, language)


@mcp.tool()
async def query_didi_finanzas(
        query: str,
        platform: Literal["Google Play", "App Store", "Facebook"],
        language: Literal["English", "Español", "简体中文"] = "English",
) -> str:
    """
    A question-answering tool for retrieving user feedback about DiDi Finanzas using a Retrieval-Augmented Generation (RAG) system.

    This tool allows users to ask natural language questions about the financial services of DiDi (DiDi Finanzas) and returns informative, multilingual answers based on real user-generated content collected from:
    - Google Play app reviews
    - Apple App Store app reviews
    - Facebook post comments

    Using RAG techniques, the system retrieves relevant feedback from the selected platform and synthesizes a natural, context-aware answer.

    """
    company = "DiDi Finanzas"
    return await get_company_data(query, company, platform, language)


if __name__ == "__main__":
    mcp.run(transport='stdio')

