"""
智剪 - AI智能视频剪辑后端服务
基于 FastAPI + FFmpeg
"""
import os
import uuid
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

# 临时文件存储目录
TEMP_DIR = Path("./temp_files")
OUTPUT_DIR = Path("./output")
TEMP_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# 任务存储
tasks = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    print("🚀 智剪服务启动中...")
    # 清理旧文件
    cleanup_old_files()
    yield
    print("👋 智剪服务关闭")

# 创建FastAPI应用
app = FastAPI(
    title="智剪 - AI智能视频剪辑API",
    description="提供视频上传、裁剪、AI剪辑等功能",
    version="1.0.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 数据模型 ====================

class ClipRequest(BaseModel):
    """剪辑请求模型"""
    video_id: str
    start_time: float = 0
    end_time: Optional[float] = None
    ai_mode: str = "custom"  # highlight, exciting, fast, custom
    output_format: str = "mp4"


class TaskStatus(BaseModel):
    """任务状态模型"""
    task_id: str
    status: str  # pending, processing, completed, failed
    progress: int = 0
    message: str = ""
    result_url: Optional[str] = None
    created_at: str = ""
    error: Optional[str] = None


# ==================== 工具函数 ====================

def cleanup_old_files():
    """清理超过1小时的临时文件"""
    import time
    current_time = time.time()
    max_age = 3600  # 1小时
    
    for directory in [TEMP_DIR, OUTPUT_DIR]:
        if directory.exists():
            for file in directory.iterdir():
                if file.is_file():
                    file_age = current_time - file.stat().st_mtime
                    if file_age > max_age:
                        try:
                            file.unlink()
                            print(f"🗑️ 已清理旧文件: {file.name}")
                        except Exception as e:
                            print(f"⚠️ 清理文件失败: {e}")


def get_file_info(file_path: Path) -> dict:
    """获取视频文件信息"""
    import subprocess
    import json
    
    try:
        cmd = [
            'ffprobe', '-v', 'quiet',
            '-print_format', 'json',
            '-show_format', '-show_streams',
            str(file_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            format_info = data.get('format', {})
            return {
                'duration': float(format_info.get('duration', 0)),
                'size': int(format_info.get('size', 0)),
                'format': format_info.get('format_name', ''),
                'bitrate': int(format_info.get('bit_rate', 0)),
            }
    except Exception as e:
        print(f"获取文件信息失败: {e}")
    
    return {}


# ==================== API路由 ====================

@app.get("/")
async def root():
    """健康检查"""
    return {
        "name": "智剪 - AI智能视频剪辑",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "upload": "/api/v1/upload",
            "clip": "/api/v1/clip",
            "status": "/api/v1/status/{task_id}",
            "download": "/api/v1/download/{filename}",
        }
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "智剪"
    }


@app.post("/api/v1/upload")
async def upload_video(file: UploadFile = File(...)):
    """上传视频文件"""
    # 验证文件类型
    allowed_types = ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/webm', 'video/x-matroska']
    if not any(file.content_type.startswith('video') for _ in [1]):
        # 更宽松的类型检查
        filename = file.filename.lower()
        if not any(filename.endswith(ext) for ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']):
            raise HTTPException(status_code=400, detail="不支持的视频格式")
    
    # 生成唯一ID
    video_id = str(uuid.uuid4())
    extension = Path(file.filename).suffix or '.mp4'
    filename = f"{video_id}{extension}"
    filepath = TEMP_DIR / filename
    
    try:
        # 写入文件
        content = await file.read()
        
        # 检查文件大小 (最大500MB)
        if len(content) > 500 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="文件过大，请上传小于500MB的视频")
        
        with open(filepath, 'wb') as f:
            f.write(content)
        
        # 获取文件信息
        file_info = get_file_info(filepath)
        
        return {
            "success": True,
            "video_id": video_id,
            "filename": filename,
            "size": len(content),
            "duration": file_info.get('duration', 0),
            "message": "视频上传成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # 清理失败的文件
        if filepath.exists():
            filepath.unlink()
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@app.post("/api/v1/clip")
async def clip_video(
    request: ClipRequest,
    background_tasks: BackgroundTasks
):
    """创建剪辑任务"""
    # 检查视频文件是否存在
    video_files = list(TEMP_DIR.glob(f"*{request.video_id}*"))
    if not video_files:
        raise HTTPException(status_code=404, detail="视频文件不存在或已过期")
    
    input_path = video_files[0]
    
    # 获取视频时长
    file_info = get_file_info(input_path)
    duration = file_info.get('duration', 0)
    
    if request.end_time is None:
        request.end_time = duration
    elif request.end_time > duration:
        request.end_time = duration
    
    # 验证时间参数
    if request.start_time < 0:
        request.start_time = 0
    if request.end_time <= request.start_time:
        raise HTTPException(status_code=400, detail="结束时间必须大于开始时间")
    
    # 创建任务
    task_id = str(uuid.uuid4())
    task = TaskStatus(
        task_id=task_id,
        status="processing",
        progress=0,
        message="正在处理视频...",
        created_at=datetime.now().isoformat()
    )
    tasks[task_id] = task
    
    # 后台执行剪辑
    background_tasks.add_task(
        process_clip_task,
        task_id,
        input_path,
        request.start_time,
        request.end_time,
        request.ai_mode,
        request.output_format
    )
    
    return {
        "success": True,
        "task_id": task_id,
        "status": "processing",
        "message": "剪辑任务已创建"
    }


async def process_clip_task(
    task_id: str,
    input_path: Path,
    start_time: float,
    end_time: float,
    ai_mode: str,
    output_format: str
):
    """后台处理剪辑任务"""
    import subprocess
    
    task = tasks.get(task_id)
    if not task:
        return
    
    output_filename = f"{task_id}.{output_format}"
    output_path = OUTPUT_DIR / output_filename
    
    try:
        duration = end_time - start_time
        
        # 根据AI模式调整参数
        if ai_mode == "fast":
            # 快速剪辑 - 调整编码参数
            cmd = [
                'ffmpeg', '-y',
                '-ss', str(start_time),
                '-i', str(input_path),
                '-t', str(duration),
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-crf', '23',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-movflags', '+faststart',
                str(output_path)
            ]
        else:
            # 普通剪辑 - 流复制更快
            cmd = [
                'ffmpeg', '-y',
                '-ss', str(start_time),
                '-i', str(input_path),
                '-t', str(duration),
                '-c', 'copy',
                str(output_path)
            ]
        
        task.progress = 20
        task.message = "正在裁剪视频..."
        
        # 执行FFmpeg命令
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise Exception(stderr.decode() if stderr else "FFmpeg执行失败")
        
        task.progress = 100
        task.status = "completed"
        task.message = "剪辑完成"
        task.result_url = f"/api/v1/download/{output_filename}"
        
    except Exception as e:
        task.status = "failed"
        task.error = str(e)
        task.message = f"剪辑失败: {str(e)}"
    
    # 清理输入文件
    try:
        if input_path.exists():
            input_path.unlink()
    except:
        pass


@app.get("/api/v1/status/{task_id}")
async def get_task_status(task_id: str):
    """获取任务状态"""
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return {
        "task_id": task.task_id,
        "status": task.status,
        "progress": task.progress,
        "message": task.message,
        "result_url": task.result_url,
        "created_at": task.created_at,
        "error": task.error
    }


@app.get("/api/v1/download/{filename}")
async def download_file(filename: str):
    """下载处理后的视频"""
    filepath = OUTPUT_DIR / filename
    
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="文件不存在或已过期")
    
    return FileResponse(
        filepath,
        media_type='video/mp4',
        filename=f"智剪_{filename}"
    )


@app.delete("/api/v1/cleanup")
async def cleanup_files():
    """清理所有临时文件（管理接口）"""
    cleanup_old_files()
    return {"message": "清理完成", "timestamp": datetime.now().isoformat()}


@app.get("/api/v1/info/{video_id}")
async def get_video_info(video_id: str):
    """获取视频信息"""
    video_files = list(TEMP_DIR.glob(f"*{video_id}*")) + list(OUTPUT_DIR.glob(f"*{video_id}*"))
    
    if not video_files:
        raise HTTPException(status_code=404, detail="视频不存在")
    
    filepath = video_files[0]
    file_info = get_file_info(filepath)
    
    return {
        "video_id": video_id,
        "filename": filepath.name,
        **file_info
    }


# ==================== 启动服务 ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
