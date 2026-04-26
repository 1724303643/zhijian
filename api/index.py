#!/usr/bin/env python3
"""
Vercel Serverless Function - 智剪API
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import uuid
import base64

app = FastAPI(title="智剪API", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ClipRequest(BaseModel):
    video_data: str  # Base64编码的视频数据
    start_time: float = 0
    end_time: Optional[float] = None
    ai_mode: str = "custom"


@app.get("/")
async def root():
    return {
        "name": "智剪 - AI智能视频剪辑API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/api/health")
async def health():
    return {"status": "healthy", "service": "智剪API"}


@app.post("/api/process")
async def process_video(request: ClipRequest):
    """
    处理视频剪辑请求（前端模式）
    由于Vercel Serverless限制，此接口作为信息展示
    实际剪辑由前端FFmpeg WASM完成
    """
    return {
        "success": True,
        "message": "前端已集成FFmpeg WASM，可在浏览器中完成视频剪辑",
        "ai_mode": request.ai_mode,
        "start_time": request.start_time,
        "end_time": request.end_time
    }


@app.post("/api/upload")
async def upload_info():
    """上传接口信息"""
    return {
        "success": True,
        "message": "请使用前端直接上传视频文件",
        "method": "前端FFmpeg WASM处理"
    }
