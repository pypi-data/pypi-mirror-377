"""
File Upload SDK - 简化大文件上传的Python客户端库
"""
import os
import hashlib
import math
import time
import uuid
from pathlib import Path
from typing import Optional, Dict, Any, Callable
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class FileUploadSDK:
    """文件上传SDK"""
    
    def __init__(self, 
                 base_url: str = "http://localhost:8000",
                 api_key: Optional[str] = None,
                 access_token: Optional[str] = None,
                 user_id: Optional[int] = None,
                 user_name: Optional[str] = None,
                 timeout: int = 30,
                 retry_times: int = 3,
                 chunk_size: int = 10 * 1024 * 1024):  # 10MB
        """
        初始化SDK
        
        Args:
            base_url: 服务器基础URL
            api_key: API Key (兼容旧版本)
            access_token: 访问令牌 (新的Token认证)
            user_id: 用户ID (用于申请API Key或生成Token)
            user_name: 用户名 (用于生成Token)
            timeout: 请求超时时间(秒)
            retry_times: 重试次数
            chunk_size: 分片大小(字节)
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.retry_times = retry_times
        self.chunk_size = chunk_size
        self.api_key = api_key
        self.access_token = access_token
        self.user_id = user_id
        self.user_name = user_name
        
        # 先配置session和重试策略
        self.session = requests.Session()
        
        # 配置重试策略
        # 兼容新旧版本的urllib3
        try:
            # 新版本urllib3使用allowed_methods
            retry_strategy = Retry(
                total=retry_times,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
                backoff_factor=1
            )
        except TypeError:
            # 旧版本urllib3使用method_whitelist
            retry_strategy = Retry(
                total=retry_times,
                status_forcelist=[429, 500, 502, 503, 504],
                method_whitelist=["HEAD", "GET", "OPTIONS", "POST"],
                backoff_factor=1
            )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 认证方式优先级：access_token > api_key > 自动生成
        if not self.access_token and not self.api_key:
            if self.user_id and self.user_name:
                # 自动生成Token
                self.access_token = self._request_token(self.user_id, self.user_name)
            elif self.user_id:
                # 兼容旧版本：生成API Key
                self.api_key = self._request_api_key(self.user_id)
    
    def _request_token(self, user_id: int, user_name: str) -> str:
        """申请访问令牌（永不过期）"""
        url = f"{self.base_url}/api/token/generate"
        data = {
            "user_id": str(user_id),
            "user_name": user_name,
            "role": "user",
            "max_file_size": 10 * 1024 * 1024 * 1024,  # 10GB
            "daily_upload_limit": 100
        }
        
        try:
            response = self.session.post(url, json=data, timeout=self.timeout)
            response.raise_for_status()
            
            result = response.json()
            access_token = result.get("access_token")
            if not access_token:
                raise Exception("服务器未返回访问令牌")
            
            print(f"✅ Token申请成功！")
            print(f"用户: {user_name} (ID: {user_id})")
            print(f"Token: {access_token[:20]}...")
            print(f"状态: 永不过期")
            
            return access_token
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Token申请失败: {str(e)}")
        except Exception as e:
            raise Exception(f"Token申请时发生错误: {str(e)}")
    
    def _request_api_key(self, user_id: int, key_name: str = "SDK Auto Key") -> str:
        """申请API Key"""
        url = f"{self.base_url}/api/auth/generate-key"
        data = {
            "user_id": user_id,
            "key_name": key_name
        }
        
        try:
            response = self.session.post(url, json=data, timeout=self.timeout)
            result = response.json()
            
            if response.status_code == 200:
                api_key = result.get('api_key')
                print(f"✅ API Key申请成功！")
                print(f"用户ID: {user_id}")
                print(f"API Key: {api_key}")
                print(f"请妥善保存您的API Key，后续可直接使用。")
                return api_key
            else:
                error_msg = result.get('detail', '申请API Key失败')
                raise Exception(f"API Key申请失败: {error_msg}")
                
        except Exception as e:
            raise Exception(f"申请API Key时发生错误: {str(e)}")
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """获取认证请求头"""
        if self.access_token:
            # 优先使用Token认证
            return {"Authorization": f"Bearer {self.access_token}"}
        elif self.api_key:
            # 兼容旧版本API Key认证
            return {"X-API-Key": self.api_key}
        else:
            raise Exception("未设置认证信息，请提供access_token或api_key")
    
    def upload_file(self,
                   file_path: str,
                   dataset_name: str,
                   file_name: Optional[str] = None,
                   progress_callback: Optional[Callable[[float], None]] = None,
                   enable_md5_check: bool = True,
                   custom_file_id: Optional[str] = None) -> Dict[str, Any]:
        """
        上传文件（类似于图片中的API调用方式）
        
        Args:
            file_path: 本地文件路径
            dataset_name: 数据集名称，用于确定文件存储路径
            file_name: 目标文件名（如果不指定，使用原文件名）
            progress_callback: 进度回调函数，参数为进度百分比(0-100)
            enable_md5_check: 是否启用MD5校验
            custom_file_id: 自定义文件ID（用于断点续传）
            
        Returns:
            上传结果字典，包含file_url等信息
            
        Example:
            >>> sdk = FileUploadSDK("http://your-server:8000")
            >>> result = sdk.upload_file(
            ...     file_path="/path/to/local/your_file.suffix",
            ...     dataset_name="my-dataset",
            ...     file_name="your_file.suffix",
            ...     progress_callback=lambda p: print(f"上传进度: {p:.1f}%")
            ... )
            >>> print(f"文件URL: {result['file_url']}")
        """
        try:
            # 验证文件
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            # 确定文件名
            if not file_name:
                file_name = file_path.name
            
            # 文件信息
            file_size = file_path.stat().st_size
            file_id = custom_file_id or self._generate_file_id(file_path, file_name)
            total_chunks = math.ceil(file_size / self.chunk_size)
            
            # 计算文件MD5
            file_md5 = None
            if enable_md5_check:
                if progress_callback:
                    progress_callback(0)
                file_md5 = self._calculate_file_md5(file_path, progress_callback)
            
            # 检查文件状态（支持断点续传）
            check_result = self._check_file_status(
                file_id, file_name, file_size, total_chunks, dataset_name, file_md5
            )
            
            if not check_result['success']:
                return {
                    'success': False,
                    'error': check_result['error'],
                    'file_id': file_id
                }
            
            uploaded_chunks = check_result.get('uploaded_chunks', [])
            
            # 上传分片
            upload_result = self._upload_chunks(
                file_path, file_id, file_name, file_size, total_chunks,
                uploaded_chunks, dataset_name, file_md5, progress_callback
            )
            
            if not upload_result['success']:
                return upload_result
            
            # 合并文件
            merge_result = self._merge_chunks(file_id, file_name, total_chunks, dataset_name, file_md5)
            
            if merge_result['success']:
                if progress_callback:
                    progress_callback(100.0)
                
                return {
                    'success': True,
                    'file_id': file_id,
                    'file_name': file_name,
                    'file_url': merge_result.get('file_url'),
                    'file_size': file_size
                }
            else:
                return merge_result
                
        except Exception as e:
            return {
                'success': False,
                'error': f"上传异常: {str(e)}",
                'file_id': file_id if 'file_id' in locals() else None
            }
    
    def _generate_file_id(self, file_path: Path, file_name: str) -> str:
        """生成唯一文件ID"""
        file_stat = file_path.stat()
        unique_string = f"{file_name}_{file_stat.st_size}_{file_stat.st_mtime}_{uuid.uuid4().hex[:8]}"
        return hashlib.md5(unique_string.encode()).hexdigest()
    
    def _calculate_file_md5(self, file_path: Path, 
                           progress_callback: Optional[Callable[[float], None]] = None) -> str:
        """计算文件MD5"""
        hash_md5 = hashlib.md5()
        file_size = file_path.stat().st_size
        processed = 0
        
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                hash_md5.update(chunk)
                processed += len(chunk)
                
                if progress_callback and file_size > 0:
                    # MD5计算占总进度的10%
                    progress = (processed / file_size) * 10
                    progress_callback(progress)
        
        return hash_md5.hexdigest()
    
    def _check_file_status(self, file_id: str, file_name: str, file_size: int,
                          total_chunks: int, dataset_name: str, file_md5: Optional[str]) -> Dict[str, Any]:
        """检查文件状态"""
        url = f"{self.base_url}/api/upload/check"
        data = {
            "file_id": file_id,
            "file_name": file_name,
            "file_size": file_size,
            "total_chunks": total_chunks,
            "dataset_name": dataset_name,
            "file_md5": file_md5
        }
        
        try:
            headers = self._get_auth_headers()
            response = self.session.post(url, json=data, headers=headers, timeout=self.timeout)
            result = response.json()
            
            if result.get('code') == 200:
                return {
                    'success': True,
                    'uploaded_chunks': result.get('uploaded_chunks', []),
                    'is_completed': result.get('is_completed', False)
                }
            else:
                return {
                    'success': False,
                    'error': result.get('message', '检查文件状态失败')
                }
        except Exception as e:
            return {
                'success': False,
                'error': f"检查文件状态异常: {str(e)}"
            }
    
    def _upload_chunks(self, file_path: Path, file_id: str, file_name: str,
                      file_size: int, total_chunks: int, uploaded_chunks: list,
                      dataset_name: str, file_md5: Optional[str], 
                      progress_callback: Optional[Callable[[float], None]]) -> Dict[str, Any]:
        """上传分片"""
        url = f"{self.base_url}/api/upload/chunk"
        
        with open(file_path, 'rb') as f:
            for chunk_index in range(total_chunks):
                if chunk_index in uploaded_chunks:
                    continue  # 跳过已上传的分片
                
                # 读取分片数据
                f.seek(chunk_index * self.chunk_size)
                chunk_data = f.read(self.chunk_size)
                chunk_size = len(chunk_data)
                
                # 计算分片MD5
                chunk_md5 = hashlib.md5(chunk_data).hexdigest() if file_md5 else None
                
                # 上传分片
                files = {
                    'chunk_file': ('chunk', chunk_data, 'application/octet-stream')
                }
                
                data = {
                    'file_id': file_id,
                    'file_name': file_name,
                    'file_size': file_size,
                    'chunk_index': chunk_index,
                    'total_chunks': total_chunks,
                    'chunk_size': chunk_size,
                    'dataset_name': dataset_name,
                    'chunk_md5': chunk_md5,
                    'file_md5': file_md5
                }
                
                try:
                    headers = self._get_auth_headers()
                    response = self.session.post(url, files=files, data=data, headers=headers, timeout=self.timeout)
                    result = response.json()
                    
                    if result.get('code') != 200:
                        return {
                            'success': False,
                            'error': f"分片 {chunk_index} 上传失败: {result.get('message', '未知错误')}",
                            'file_id': file_id
                        }
                    
                    # 更新进度（分片上传占总进度的80%，从10%开始）
                    if progress_callback:
                        upload_progress = 10 + ((chunk_index + 1) / total_chunks) * 80
                        progress_callback(upload_progress)
                        
                except Exception as e:
                    return {
                        'success': False,
                        'error': f"分片 {chunk_index} 上传异常: {str(e)}",
                        'file_id': file_id
                    }
        
        return {'success': True}
    
    def _merge_chunks(self, file_id: str, file_name: str, total_chunks: int,
                     dataset_name: str, file_md5: Optional[str]) -> Dict[str, Any]:
        """合并分片"""
        url = f"{self.base_url}/api/upload/merge"
        data = {
            "file_id": file_id,
            "file_name": file_name,
            "total_chunks": total_chunks,
            "dataset_name": dataset_name,
            "file_md5": file_md5
        }
        
        try:
            headers = self._get_auth_headers()
            response = self.session.post(url, json=data, headers=headers, timeout=self.timeout)
            result = response.json()
            
            if result.get('code') == 200:
                return {
                    'success': True,
                    'file_url': f"{self.base_url}{result.get('file_url', '')}"
                }
            else:
                return {
                    'success': False,
                    'error': result.get('message', '合并文件失败'),
                    'file_id': file_id
                }
        except Exception as e:
            return {
                'success': False,
                'error': f"合并文件异常: {str(e)}",
                'file_id': file_id
            }
    
    def get_upload_status(self, file_id: str) -> Dict[str, Any]:
        """获取上传状态"""
        url = f"{self.base_url}/api/upload/status/{file_id}"
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            result = response.json()
            
            if result.get('code') == 200:
                return {
                    'success': True,
                    'file_id': result.get('file_id'),
                    'file_name': result.get('file_name'),
                    'uploaded_chunks': result.get('uploaded_chunks', []),
                    'is_completed': result.get('is_completed', False),
                    'progress': result.get('progress', 0)
                }
            else:
                return {
                    'success': False,
                    'error': result.get('message', '获取状态失败')
                }
        except Exception as e:
            return {
                'success': False,
                'error': f"获取状态异常: {str(e)}"
            }
    
    def cancel_upload(self, file_id: str) -> Dict[str, Any]:
        """取消上传"""
        url = f"{self.base_url}/api/upload/{file_id}"
        
        try:
            response = self.session.delete(url, timeout=self.timeout)
            result = response.json()
            
            if result.get('code') == 200:
                return {
                    'success': True,
                    'message': result.get('message', '上传已取消')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('message', '取消上传失败')
                }
        except Exception as e:
            return {
                'success': False,
                'error': f"取消上传异常: {str(e)}"
            }


# 便捷的全局API实例
_default_sdk = None

def init_sdk(base_url: str = "http://localhost:8000", 
            user_id: Optional[int] = None, 
            user_name: Optional[str] = None,
            api_key: Optional[str] = None, 
            access_token: Optional[str] = None, 
            **kwargs):
    """
    初始化默认SDK实例
    
    Args:
        base_url: 服务器基础URL
        user_id: 用户ID
        user_name: 用户名 (用于Token认证)
        api_key: API Key (兼容旧版本)
        access_token: 访问令牌 (推荐)
        **kwargs: 其他参数
    """
    global _default_sdk
    _default_sdk = FileUploadSDK(
        base_url=base_url, 
        api_key=api_key, 
        access_token=access_token,
        user_id=user_id, 
        user_name=user_name,
        **kwargs
    )

def upload_file(file_path: str,
               dataset_name: str,
               file_name: Optional[str] = None,
               progress_callback: Optional[Callable[[float], None]] = None,
               **kwargs) -> Dict[str, Any]:
    """
    便捷的文件上传函数（类似图片中的API调用方式）
    
    Args:
        file_path: 本地文件路径
        dataset_name: 数据集名称
        file_name: 目标文件名
        progress_callback: 进度回调函数
        **kwargs: 其他参数
        
    Returns:
        上传结果
    
    Example:
        >>> import file_upload_sdk as api
        >>> # 方式1：使用user_id自动申请API Key
        >>> api.init_sdk("http://your-server:8000", user_id=12345)
        >>> # 方式2：直接使用已有的API Key
        >>> api.init_sdk("http://your-server:8000", api_key="ak_12345_xxx_yyy")
        >>> result = api.upload_file(
        ...     file_path="/path/to/local/your_file.suffix",
        ...     dataset_name="my-dataset"
        ... )
    """
    if _default_sdk is None:
        raise RuntimeError("请先调用 init_sdk() 初始化SDK")
    
    return _default_sdk.upload_file(file_path, dataset_name, file_name, progress_callback, **kwargs)

def get_upload_status(file_id: str) -> Dict[str, Any]:
    """获取上传状态"""
    if _default_sdk is None:
        raise RuntimeError("请先调用 init_sdk() 初始化SDK")
    
    return _default_sdk.get_upload_status(file_id)

def cancel_upload(file_id: str) -> Dict[str, Any]:
    """取消上传"""
    if _default_sdk is None:
        raise RuntimeError("请先调用 init_sdk() 初始化SDK")
    
    return _default_sdk.cancel_upload(file_id)
