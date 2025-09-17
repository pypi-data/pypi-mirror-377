"""文件服务"""

import logging
import mimetypes
import os
from pathlib import Path
from typing import Optional, Union, Dict, Any

import aiohttp

from ..utils.config import Config


class FileService:
    """文件服务类

    提供文件上传、下载等功能，集成uniCloud OSS服务。
    """

    def __init__(self, config: Config):
        """初始化文件服务

        Args:
            config: 配置对象
        """
        self.config = config
        self.logger = logging.getLogger("FileService")

        # HTTP会话
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """获取HTTP会话"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        """关闭HTTP会话"""
        if self._session and not self._session.closed:
            await self._session.close()

    async def upload_file(
        self,
        file_path: Union[str, Path],
        filename: Optional[str] = None,
        content_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """上传文件到OSS

        Args:
            file_path: 本地文件路径
            filename: 指定文件名，默认使用原文件名
            content_type: MIME类型，默认自动检测

        Returns:
            上传结果，包含文件URL等信息
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")

            # 确定文件名和MIME类型
            filename = filename or file_path.name
            if not content_type:
                content_type, _ = mimetypes.guess_type(str(file_path))
                content_type = content_type or 'application/octet-stream'

            self.logger.info(f"上传文件: {filename} ({content_type})")

            # TODO: 实现实际的OSS上传逻辑
            # 这里返回一个模拟的URL，实际项目中需要调用uniCloud OSS API
            file_url = f"https://oss.example.com/{filename}"

            return {
                "success": True,
                "file_url": file_url,
                "filename": filename,
                "content_type": content_type,
                "size": file_path.stat().st_size
            }

        except Exception as e:
            self.logger.error(f"上传文件失败: {e}")
            raise

    async def download_file(
        self,
        file_url: str,
        save_path: Optional[Union[str, Path]] = None
    ) -> Path:
        """下载文件

        Args:
            file_url: 文件URL
            save_path: 保存路径，默认保存到临时目录

        Returns:
            下载文件的本地路径
        """
        try:
            session = await self._get_session()

            self.logger.info(f"下载文件: {file_url}")

            async with session.get(file_url) as resp:
                if resp.status != 200:
                    raise Exception(f"下载失败: HTTP {resp.status}")

                # 确定保存路径
                if save_path is None:
                    filename = os.path.basename(file_url.split('?')[0])
                    save_path = Path.cwd() / "downloads" / filename
                else:
                    save_path = Path(save_path)

                # 创建目录
                save_path.parent.mkdir(parents=True, exist_ok=True)

                # 写入文件
                with open(save_path, 'wb') as f:
                    async for chunk in resp.content.iter_chunked(8192):
                        f.write(chunk)

                self.logger.info(f"文件已保存到: {save_path}")
                return save_path

        except Exception as e:
            self.logger.error(f"下载文件失败: {e}")
            raise

    async def get_file_info(self, file_url: str) -> Dict[str, Any]:
        """获取文件信息

        Args:
            file_url: 文件URL

        Returns:
            文件信息
        """
        try:
            session = await self._get_session()

            async with session.head(file_url) as resp:
                if resp.status != 200:
                    raise Exception(f"获取文件信息失败: HTTP {resp.status}")

                return {
                    "url": file_url,
                    "content_type": resp.headers.get('Content-Type'),
                    "content_length": int(resp.headers.get('Content-Length', 0)),
                    "last_modified": resp.headers.get('Last-Modified'),
                }

        except Exception as e:
            self.logger.error(f"获取文件信息失败: {e}")
            raise

    def get_mime_type(self, filename: str) -> str:
        """获取文件MIME类型

        Args:
            filename: 文件名

        Returns:
            MIME类型
        """
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or 'application/octet-stream'

    def is_image(self, filename: str) -> bool:
        """判断是否为图片文件"""
        mime_type = self.get_mime_type(filename)
        return mime_type.startswith('image/')

    def is_video(self, filename: str) -> bool:
        """判断是否为视频文件"""
        mime_type = self.get_mime_type(filename)
        return mime_type.startswith('video/')

    def is_audio(self, filename: str) -> bool:
        """判断是否为音频文件"""
        mime_type = self.get_mime_type(filename)
        return mime_type.startswith('audio/')

    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()