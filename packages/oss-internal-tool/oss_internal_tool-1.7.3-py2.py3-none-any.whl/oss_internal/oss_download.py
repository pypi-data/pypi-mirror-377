import os
import tempfile
import oss2
import threading

from typing import List, Callable

from .schemas.error import FileNotEnoughError
from .utils.progress_display import show_download_progress

def download_single_file_from_oss(oss_key: str,
                                ali_access_key_id: str,
                                ali_access_secret: str,
                                oss_origin: str,
                                bucket_name: str,
                                internal: bool = True,
                                temp_dir: str = '',
                                progress_callback: Callable = show_download_progress) -> str:
    """
    从 OSS 下载单个文件到临时目录
    
    Args:
        oss_key (str): OSS文件key
        ali_access_key_id (str): 阿里云 AccessKey ID，用于认证
        ali_access_secret (str): 阿里云 AccessKey Secret，用于认证
        oss_origin (str): OSS 服务的地域节点，例如 'oss-cn-hangzhou'
        bucket_name (str): OSS Bucket 的名称
        internal (bool, optional): 是否使用内网访问，默认为 True
        temp_dir (str, optional): 临时目录路径，如果不指定则使用系统临时目录
        
    Returns:
        str: 下载文件的路径
        
    Raises:
        ValueError: 当必要的参数为空时抛出
        FileNotFoundError: 当OSS文件不存在时抛出
        Exception: 当下载过程中发生其他错误时抛出
    """
    if not all([ali_access_key_id, ali_access_secret, oss_origin, bucket_name]):
        raise ValueError("ali_access_key_id, ali_access_secret, oss_origin, bucket_name 不能为空")
    
    # 设置OSS端点
    oss_endpoint = f"https://{oss_origin}-internal.aliyuncs.com" if internal else f"https://{oss_origin}.aliyuncs.com"
    oss_auth = oss2.Auth(ali_access_key_id, ali_access_secret)
    bucket = oss2.Bucket(oss_auth, oss_endpoint, bucket_name)
    
    # 如果没有指定临时目录，使用系统临时目录
    if not temp_dir:
        temp_dir = tempfile.mkdtemp()
    elif not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    try:
        file_path = os.path.join(temp_dir, os.path.basename(oss_key))
        try:
            bucket.get_object_to_file(oss_key, file_path, progress_callback=progress_callback)
            return file_path
        except oss2.exceptions.NoSuchKey:
            raise FileNotFoundError(f"OSS文件不存在: {oss_key}")
            
    except oss2.exceptions.OssError as e:
        raise Exception(f"OSS操作失败: {str(e)}")
    except Exception as e:
        raise Exception(f"下载过程发生错误: {str(e)}")

def download_batch_files_from_oss(oss_keys: List[str],
                                ali_access_key_id: str,
                                ali_access_secret: str,
                                oss_origin: str,
                                bucket_name: str,
                                internal: bool = True,
                                temp_dir: str = '') -> List[str]:
    """
    从 OSS 批量下载文件到临时目录
    
    Args:
        oss_keys (List[str]): OSS文件key列表
        ali_access_key_id (str): 阿里云 AccessKey ID，用于认证
        ali_access_secret (str): 阿里云 AccessKey Secret，用于认证
        oss_origin (str): OSS 服务的地域节点，例如 'oss-cn-hangzhou'
        bucket_name (str): OSS Bucket 的名称
        internal (bool, optional): 是否使用内网访问，默认为 True
        temp_dir (str, optional): 临时目录路径，如果不指定则使用系统临时目录
        
    Returns:
        List[str]: 成功下载的文件路径列表
        
    Raises:
        ValueError: 当必要的参数为空时抛出
        FileNotFoundError: 当没有文件成功下载时抛出
        Exception: 当下载过程中发生其他错误时抛出
    """
    if not all([ali_access_key_id, ali_access_secret, oss_origin, bucket_name]):
        raise ValueError("ali_access_key_id, ali_access_secret, oss_origin, bucket_name 不能为空")
    
    if not isinstance(oss_keys, list):
        raise ValueError(f"oss_keys 必须是列表类型，当前类型: {type(oss_keys)}")
    
    # 设置OSS端点
    oss_endpoint = f"https://{oss_origin}-internal.aliyuncs.com" if internal else f"https://{oss_origin}.aliyuncs.com"
    oss_auth = oss2.Auth(ali_access_key_id, ali_access_secret)
    bucket = oss2.Bucket(oss_auth, oss_endpoint, bucket_name)
    
    # 如果没有指定临时目录，使用系统临时目录
    if not temp_dir:
        temp_dir = tempfile.mkdtemp()
    elif not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    try:
        downloaded_files = []
        for key in oss_keys:
            if not isinstance(key, str):
                raise ValueError(f"无效的OSS key类型: {type(key)}")
            
            file_path = os.path.join(temp_dir, os.path.basename(key))
            try:
                bucket.get_object_to_file(key, file_path)
                downloaded_files.append(file_path)
            except oss2.exceptions.NoSuchKey:
                continue
            
        if not downloaded_files:
            raise FileNotFoundError("没有成功下载任何文件")
        
        elif len(downloaded_files)!=len(oss_keys):
            raise FileNotEnoughError(f"部分文件下载成功，查看路径:{temp_dir}")

        return downloaded_files
            
    except oss2.exceptions.OssError as e:
        raise Exception(f"OSS操作失败: {str(e)}")
    except Exception as e:
        raise Exception(f"下载过程发生错误: {str(e)}")
    
def download_large_file_from_oss(oss_key: str,
                                  ali_access_key_id: str,
                                  ali_access_secret: str,
                                  oss_origin: str,
                                  bucket_name: str,
                                  internal: bool = True,
                                  temp_dir: str = '',
                                  part_size: int = 512 * 1024 * 1024,  # 每段默认256MB
                                  read_chunk_size: int = 8 * 1024 * 1024,  # 每次读8MB
                                  progress_callback: Callable = show_download_progress) -> str:
    """
    从 OSS 多线程下载大文件到本地

    Args:
        oss_key (str): OSS文件key
        ali_access_key_id (str): 阿里云 AccessKey ID
        ali_access_secret (str): 阿里云 AccessKey Secret
        oss_origin (str): OSS服务地域，例如 'oss-cn-hangzhou'
        bucket_name (str): OSS Bucket 名
        internal (bool, optional): 是否使用内网访问
        temp_dir (str, optional): 下载文件临时保存路径
        part_size (int): 每个线程下载的块大小（字节）
        read_chunk_size (int): 每次从OSS读取的最小块大小（字节）
        progress_callback (callable): 进度回调函数(downloaded_bytes, total_bytes)

    Returns:
        str: 下载到本地的文件路径

    Raises:
        ValueError: 如果关键信息为空
        FileNotFoundError: OSS 上找不到文件
        Exception: 其他错误
    """
    if not all([ali_access_key_id, ali_access_secret, oss_origin, bucket_name]):
        raise ValueError("ali_access_key_id, ali_access_secret, oss_origin, bucket_name 不能为空")

    oss_endpoint = f"https://{oss_origin}-internal.aliyuncs.com" if internal else f"https://{oss_origin}.aliyuncs.com"
    auth = oss2.Auth(ali_access_key_id, ali_access_secret)
    bucket = oss2.Bucket(auth, oss_endpoint, bucket_name)

    try:
        meta = bucket.get_object_meta(oss_key)
        total_size = int(meta.headers['Content-Length'])
    except oss2.exceptions.NoSuchKey:
        raise FileNotFoundError(f"OSS文件不存在: {oss_key}")
    except oss2.exceptions.OssError as e:
        raise Exception(f"无法获取文件元信息: {str(e)}")

    if not temp_dir:
        temp_dir = tempfile.mkdtemp()
    elif not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    file_path = os.path.join(temp_dir, os.path.basename(oss_key))

    with open(file_path, 'wb') as f:
        f.truncate(total_size)

    download_lock = threading.Lock()
    downloaded_bytes = 0

    def range_get(start, end):
        nonlocal downloaded_bytes
        try:
            with bucket.get_object(oss_key, byte_range=(start, end)) as stream:
                offset = start
                with open(file_path, 'rb+') as f:
                    while offset <= end:
                        chunk = stream.read(min(read_chunk_size, end - offset + 1))
                        if not chunk:
                            break
                        f.seek(offset)
                        f.write(chunk)
                        offset += len(chunk)
                        with download_lock:
                            downloaded_bytes += len(chunk)
                            if progress_callback:
                                progress_callback(downloaded_bytes, total_size)
        except Exception as e:
            raise Exception(f"下载分段失败 [{start}-{end}]: {str(e)}")

    threads = []
    start = 0
    while start < total_size:
        end = min(start + part_size - 1, total_size - 1)
        t = threading.Thread(target=range_get, args=(start, end))
        threads.append(t)
        t.start()
        start += part_size

    for t in threads:
        t.join()

    return file_path
