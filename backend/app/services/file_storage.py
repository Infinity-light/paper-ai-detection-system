"""
File Storage Service

role: 文件存储抽象层，支持本地文件系统和云存储
depends: [config.py]
exports: [FileStorage]
status: IMPLEMENTED

functions:
- FileStorage.save_upload(file, batch_id): 保存上传的文件
- FileStorage.save_result(content, paper_id): 保存检测结果
- FileStorage.get_upload_path(batch_id, filename): 获取上传文件路径
- FileStorage.get_result_path(paper_id): 获取结果文件路径
- FileStorage.delete_batch_files(batch_id): 删除批次相关文件
"""

from pathlib import Path
from typing import BinaryIO
import shutil
from app.config import get_settings

settings = get_settings()


class FileStorage:
    """文件存储服务"""

    def __init__(self):
        """初始化存储服务"""
        self.upload_dir = Path(settings.upload_dir)
        self.result_dir = Path(settings.result_dir)

        # 确保目录存在
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.result_dir.mkdir(parents=True, exist_ok=True)

    def save_upload(self, file: BinaryIO, batch_id: int, filename: str) -> str:
        """
        保存上传的文件

        Args:
            file: 文件对象
            batch_id: 批次ID
            filename: 文件名

        Returns:
            保存的文件路径
        """
        # 创建批次目录
        batch_dir = self.upload_dir / str(batch_id)
        batch_dir.mkdir(parents=True, exist_ok=True)

        # 保存文件
        file_path = batch_dir / filename

        with open(file_path, 'wb') as f:
            # 读取并写入文件内容
            shutil.copyfileobj(file, f)

        return str(file_path)

    def save_result(self, content: str, paper_id: int, filename: str) -> str:
        """
        保存检测结果

        Args:
            content: 结果内容
            paper_id: 论文ID
            filename: 文件名

        Returns:
            保存的文件路径
        """
        # 创建论文结果目录
        paper_dir = self.result_dir / str(paper_id)
        paper_dir.mkdir(parents=True, exist_ok=True)

        # 保存结果文件
        file_path = paper_dir / filename

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return str(file_path)

    def get_upload_path(self, batch_id: int, filename: str) -> Path:
        """
        获取上传文件路径

        Args:
            batch_id: 批次ID
            filename: 文件名

        Returns:
            文件路径
        """
        return self.upload_dir / str(batch_id) / filename

    def get_result_path(self, paper_id: int, filename: str) -> Path:
        """
        获取结果文件路径

        Args:
            paper_id: 论文ID
            filename: 文件名

        Returns:
            文件路径
        """
        return self.result_dir / str(paper_id) / filename

    def delete_batch_files(self, batch_id: int) -> None:
        """
        删除批次相关文件

        Args:
            batch_id: 批次ID
        """
        batch_dir = self.upload_dir / str(batch_id)

        if batch_dir.exists() and batch_dir.is_dir():
            shutil.rmtree(batch_dir)
