"""
八字排盤系統 - Web 應用主入口
© 2024-2026 Antigravity. All rights reserved.
Unauthorized copying, modification, or distribution of this code is strictly prohibited.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from api.routes import router
from bazi.db import init_db

app = FastAPI(title="八字算命網頁版")

# 初始化資料庫
init_db()

# 掛載靜態文件目錄
app.mount("/static", StaticFiles(directory="static"), name="static")

# 包含 API 路由
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
