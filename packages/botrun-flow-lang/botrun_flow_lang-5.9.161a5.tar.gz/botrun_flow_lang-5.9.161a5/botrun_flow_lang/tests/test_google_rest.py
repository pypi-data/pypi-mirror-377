import asyncio
import os
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# 載入 .env 檔案中的環境變數
load_dotenv()

# 從環境變數讀取您的 API 金鑰
api_key = os.getenv("SUBSIDY_GEMINI_API_KEY")
if not api_key:
    raise ValueError("請設定 SUBSIDY_GEMINI_API_KEY 環境變數")

# 您的 Nginx 代理端點
api_endpoint = "trend-vision.botrun.ai"


async def main():
    print("Configuring google.generativeai globally for REST transport...")
    try:
        # === 核心修改：使用全域設定 ===
        # 這樣可以確保所有 client 都使用 REST 和您的自訂端點
        genai.configure(
            api_key=api_key,
            transport="rest",
            client_options={"api_endpoint": api_endpoint}
        )

        # 現在，正常建立 ChatGoogleGenerativeAI 物件，不需要再傳 transport 或 client_options
        model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0
        )

        print("Invoking model...")
        response = await model.ainvoke([HumanMessage(content="你好")])
        print("Successfully received response:")
        print(response.content)

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())