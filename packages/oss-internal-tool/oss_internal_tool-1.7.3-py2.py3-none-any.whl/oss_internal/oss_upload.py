import os
import oss2
import asyncio_oss
import threading
import tempfile
import alibabacloud_oss_v2 as oss

from datetime import datetime
from typing import Callable, List, Tuple, Optional

from .utils.progress_display import show_upload_progress
from .schemas.error import EmptyDirectoryError, NotADirectoryError, FileNotFoundError

def upload_file_to_oss(file_path: str,
                       ali_access_key_id: str = None,
                       ali_access_secret: str = None,
                       oss_origin: str = None,
                       bucket_name: str = None,
                       default_prefix: str = None,
                       prefix: str = None,
                       progress_callback: Callable = show_upload_progress,
                       internal: bool = True) -> Tuple[str, str]:
    """
    上传单个文件到阿里云 OSS。

    Args:
        file_path (str): 要上传的本地文件路径
        ali_access_key_id (str, optional): 阿里云 AccessKey ID，用于认证
        ali_access_secret (str, optional): 阿里云 AccessKey Secret，用于认证
        oss_origin (str, optional): OSS 服务的地域节点，例如 'oss-cn-hangzhou'
        bucket_name (str, optional): OSS Bucket 的名称
        default_prefix (str, optional): 默认的 OSS 对象前缀路径
        prefix (str, optional): 自定义的 OSS 对象前缀路径，如果不指定则使用时间戳生成
        progress_callback (Callable, optional): 进度回调函数，默认为 show_upload_progress
        internal (bool, optional): 是否使用内网访问，默认为 True

    Returns:
        Tuple[str, str]: 返回 (oss_key, bucket_name) 元组，其中：
            - oss_key: 上传后的 OSS 对象键
            - bucket_name: 使用的 Bucket 名称

    Raises:
        ValueError: 当必要的参数（ali_access_key_id, ali_access_secret, oss_origin, bucket_name）为空时抛出
        FileNotFoundError: 当本地文件不存在时抛出
        Exception: 当上传过程中发生错误时抛出
    """
    if not prefix:
        prefix = datetime.now().strftime("simple_upload_%Y-%m-%d_%H-%M")
    
    if not all([ali_access_key_id, ali_access_secret, oss_origin, bucket_name]):
        raise ValueError("ali_access_key_id, ali_access_secret, oss_origin, bucket_name 不能为空")
    
    filename = os.path.basename(file_path)
    oss_key = f"{default_prefix}/{prefix}/{filename}"
    oss_endpoint = f"https://{oss_origin}-internal.aliyuncs.com" if internal else f"https://{oss_origin}.aliyuncs.com"
    oss_auth = oss2.Auth(ali_access_key_id, ali_access_secret)
    bucket = oss2.Bucket(
        oss_auth,
        oss_endpoint,
        bucket_name=bucket_name,
    )

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        with open(file_path, "rb") as f:
            bucket.put_object(oss_key, f, progress_callback=progress_callback)
        return oss_key, bucket_name
    except Exception as e:
        raise Exception(f"Upload file to oss failed: {e}")
    
def batch_upload_file_to_oss(file_paths: List[str],
                            ali_access_key_id: str = None,
                            ali_access_secret: str = None,
                            oss_origin: str = None,
                            bucket_name: str = None,
                            default_prefix: str = None,
                            prefix: str = None,
                            progress_callback: Callable = show_upload_progress,
                            internal: bool = True) -> Tuple[List[str], str]:
    """
    批量上传多个文件到阿里云 OSS。

    Args:
        file_paths (List[str]): 要上传的本地文件路径列表
        ali_access_key_id (str, optional): 阿里云 AccessKey ID，用于认证
        ali_access_secret (str, optional): 阿里云 AccessKey Secret，用于认证
        oss_origin (str, optional): OSS 服务的地域节点，例如 'oss-cn-hangzhou'
        bucket_name (str, optional): OSS Bucket 的名称
        default_prefix (str, optional): 默认的 OSS 对象前缀路径
        prefix (str, optional): 自定义的 OSS 对象前缀路径，如果不指定则使用时间戳生成
        progress_callback (Callable, optional): 进度回调函数，默认为 show_upload_progress
        internal (bool, optional): 是否使用内网访问，默认为 True

    Returns:
        Tuple[List[str], str]: 返回 (oss_keys, bucket_name) 元组，其中：
            - oss_keys: 上传成功的所有 OSS 对象键列表
            - bucket_name: 使用的 Bucket 名称

    Raises:
        ValueError: 当必要的参数为空时抛出
        FileNotFoundError: 当本地文件不存在时抛出
        Exception: 当上传过程中发生错误时抛出
    """
    if not prefix:
        prefix = datetime.now().strftime("simple_upload_%Y-%m-%d_%H-%M")

    oss_keys = []
    for file_path in file_paths:
        filename = os.path.basename(file_path)
        oss_key = f"{default_prefix}/{prefix}/{filename}"
        oss_key, bucket_name = upload_file_to_oss(file_path=file_path, 
                                                ali_access_key_id=ali_access_key_id, 
                                                ali_access_secret=ali_access_secret, 
                                                oss_origin=oss_origin, 
                                                bucket_name=bucket_name, 
                                                default_prefix=default_prefix, 
                                                prefix=prefix, 
                                                progress_callback=progress_callback, 
                                                internal=internal)
        if oss_key:
            oss_keys.append(oss_key)
    return oss_keys, bucket_name

def upload_directory_to_oss(directory_path: str,
                            ali_access_key_id: str = None,
                            ali_access_secret: str = None,
                            oss_origin: str = None,
                            bucket_name: str = None,
                            default_prefix: str = None,
                            prefix: str = None,
                            progress_callback: Callable = show_upload_progress,
                            internal: bool = True) -> Tuple[List[str], str]:
    """
    上传目录到阿里云 OSS。

    Args:
        directory_path (str): 要上传的本地目录路径
        ali_access_key_id (str, optional): 阿里云 AccessKey ID，用于认证
        ali_access_secret (str, optional): 阿里云 AccessKey Secret，用于认证
        oss_origin (str, optional): OSS 服务的地域节点，例如 'oss-cn-hangzhou'
        bucket_name (str, optional): OSS Bucket 的名称
        default_prefix (str, optional): 默认的 OSS 对象前缀路径
        prefix (str, optional): 自定义的 OSS 对象前缀路径，如果不指定则使用时间戳生成
        progress_callback (Callable, optional): 进度回调函数，默认为 show_upload_progress
        internal (bool, optional): 是否使用内网访问，默认为 True

    Returns:
        Tuple[List[str], str]: 返回 (oss_keys, bucket_name) 元组，其中：
            - oss_keys: 上传成功的所有 OSS 对象键列表
            - bucket_name: 使用的 Bucket 名称

    Raises:
        ValueError: 当必要的参数为空时抛出
        FileNotFoundError: 当目录不存在时抛出
        NotADirectoryError: 当指定路径不是目录时抛出
        EmptyDirectoryError: 当目录为空时抛出
        Exception: 当上传过程中发生错误时抛出
    """
    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"目录不存在: {directory_path}")
    
    if not os.path.isdir(directory_path):
        raise NotADirectoryError(f"指定路径不是目录: {directory_path}")

    file_paths = []
    for root, _, files in os.walk(directory_path):
        for filename in files:
            file_paths.append(os.path.join(root, filename))
    
    if not file_paths:
        raise EmptyDirectoryError(f"目录为空: {directory_path}")

    try:
        return batch_upload_file_to_oss(file_paths, 
                                      ali_access_key_id=ali_access_key_id, 
                                      ali_access_secret=ali_access_secret, 
                                      oss_origin=oss_origin, 
                                      bucket_name=bucket_name, 
                                      default_prefix=default_prefix, 
                                      prefix=prefix, 
                                      progress_callback=progress_callback, 
                                      internal=internal)
    except Exception as e:
        raise Exception(f"上传目录到 OSS 失败: {e}")

async def aupload_file_to_oss(file_path: str,
                             ali_access_key_id: str = None,
                             ali_access_secret: str = None,
                             oss_origin: str = None,
                             bucket_name: str = None,
                             default_prefix: str = None,   
                             prefix: str = None,
                             progress_callback: Callable = show_upload_progress,
                             internal: bool = True) -> Tuple[str, str]:
    """
    异步上传单个文件到阿里云 OSS。

    Args:
        file_path (str): 要上传的本地文件路径
        ali_access_key_id (str, optional): 阿里云 AccessKey ID，用于认证
        ali_access_secret (str, optional): 阿里云 AccessKey Secret，用于认证
        oss_origin (str, optional): OSS 服务的地域节点，例如 'oss-cn-hangzhou'
        bucket_name (str, optional): OSS Bucket 的名称
        default_prefix (str, optional): 默认的 OSS 对象前缀路径
        prefix (str, optional): 自定义的 OSS 对象前缀路径，如果不指定则使用时间戳生成
        progress_callback (Callable, optional): 异步进度回调函数，默认为 show_upload_progress
        internal (bool, optional): 是否使用内网访问，默认为 True

    Returns:
        Tuple[str, str]: 返回 (oss_key, bucket_name) 元组，其中：
            - oss_key: 上传后的 OSS 对象键
            - bucket_name: 使用的 Bucket 名称

    Raises:
        ValueError: 当必要的参数为空时抛出
        FileNotFoundError: 当本地文件不存在时抛出
        Exception: 当上传过程中发生错误时抛出
    """
    if not all([ali_access_key_id, ali_access_secret, oss_origin, bucket_name]):
        raise ValueError("ali_access_key_id, ali_access_secret, oss_origin, bucket_name 不能为空")

    oss_endpoint = f"https://{oss_origin}-internal.aliyuncs.com" if internal else f"https://{oss_origin}.aliyuncs.com"
    oss_auth = oss2.Auth(ali_access_key_id, ali_access_secret)
    bucket = oss2.Bucket(
        oss_auth,
        oss_endpoint,
        bucket_name=bucket_name,
    )
    filename = os.path.basename(file_path)
    oss_key = f"{default_prefix}/{prefix}/{filename}"

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        async with asyncio_oss.Bucket(oss_auth, oss_endpoint, bucket_name) as bucket:
            with open(file_path, "rb") as f:
                await bucket.put_object(oss_key, f, progress_callback=progress_callback)
        return oss_key, bucket_name
    except Exception as e:
        raise Exception(f"Upload file to oss failed: {e}")
    
async def abatch_upload_file_to_oss(file_paths: List[str],
                                   ali_access_key_id: str = None,
                                   ali_access_secret: str = None,
                                   oss_origin: str = None,
                                   bucket_name: str = None,
                                   default_prefix: str = None,
                                   prefix: str = None,
                                   progress_callback: Callable = show_upload_progress,
                                   internal: bool = True) -> Tuple[List[str], str]:
    """
    异步批量上传多个文件到阿里云 OSS。

    Args:
        file_paths (List[str]): 要上传的本地文件路径列表
        ali_access_key_id (str, optional): 阿里云 AccessKey ID，用于认证
        ali_access_secret (str, optional): 阿里云 AccessKey Secret，用于认证
        oss_origin (str, optional): OSS 服务的地域节点，例如 'oss-cn-hangzhou'
        bucket_name (str, optional): OSS Bucket 的名称
        default_prefix (str, optional): 默认的 OSS 对象前缀路径
        prefix (str, optional): 自定义的 OSS 对象前缀路径，如果不指定则使用时间戳生成
        progress_callback (Callable, optional): 异步进度回调函数，默认为 show_upload_progress
        internal (bool, optional): 是否使用内网访问，默认为 True

    Returns:
        Tuple[List[str], str]: 返回 (oss_keys, bucket_name) 元组，其中：
            - oss_keys: 上传成功的所有 OSS 对象键列表
            - bucket_name: 使用的 Bucket 名称

    Raises:
        ValueError: 当必要的参数为空时抛出
        FileNotFoundError: 当本地文件不存在时抛出
        Exception: 当上传过程中发生错误时抛出
    """
    if not prefix:
        prefix = datetime.now().strftime("async_upload_%Y-%m-%d_%H-%M")

    oss_keys = []
    for file_path in file_paths:
        oss_key, bucket_name = await aupload_file_to_oss(file_path=file_path, 
                                                        ali_access_key_id=ali_access_key_id, 
                                                        ali_access_secret=ali_access_secret, 
                                                        oss_origin=oss_origin, 
                                                        bucket_name=bucket_name, 
                                                        default_prefix=default_prefix, 
                                                        prefix=prefix, 
                                                        progress_callback=progress_callback, 
                                                        internal=internal)
        if oss_key:
            oss_keys.append(oss_key)
    return oss_keys, bucket_name

async def aupload_directory_to_oss(directory_path: str,
                                  ali_access_key_id: str = None,
                                  ali_access_secret: str = None,
                                  oss_origin: str = None,
                                  bucket_name: str = None,
                                  default_prefix: str = None,
                                  prefix: str = None,
                                  progress_callback: Callable = show_upload_progress,
                                  internal: bool = True) -> Tuple[List[str], str]:
    """
    异步上传目录到阿里云 OSS。

    Args:
        directory_path (str): 要上传的本地目录路径
        ali_access_key_id (str, optional): 阿里云 AccessKey ID，用于认证
        ali_access_secret (str, optional): 阿里云 AccessKey Secret，用于认证
        oss_origin (str, optional): OSS 服务的地域节点，例如 'oss-cn-hangzhou'
        bucket_name (str, optional): OSS Bucket 的名称
        default_prefix (str, optional): 默认的 OSS 对象前缀路径
        prefix (str, optional): 自定义的 OSS 对象前缀路径，如果不指定则使用时间戳生成
        progress_callback (Callable, optional): 异步进度回调函数，默认为 show_upload_progress
        internal (bool, optional): 是否使用内网访问，默认为 True

    Returns:
        Tuple[List[str], str]: 返回 (oss_keys, bucket_name) 元组，其中：
            - oss_keys: 上传成功的所有 OSS 对象键列表
            - bucket_name: 使用的 Bucket 名称

    Raises:
        ValueError: 当必要的参数为空时抛出
        FileNotFoundError: 当目录不存在时抛出
        NotADirectoryError: 当指定路径不是目录时抛出
        EmptyDirectoryError: 当目录为空时抛出
        Exception: 当上传过程中发生错误时抛出
    """
    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"目录不存在: {directory_path}")
    
    if not os.path.isdir(directory_path):
        raise NotADirectoryError(f"指定路径不是目录: {directory_path}")

    file_paths = []
    for root, _, files in os.walk(directory_path):
        for filename in files:
            file_paths.append(os.path.join(root, filename))
    
    if not file_paths:
        raise EmptyDirectoryError(f"目录为空: {directory_path}")

    try:
        return await abatch_upload_file_to_oss(file_paths, 
                                             ali_access_key_id=ali_access_key_id, 
                                             ali_access_secret=ali_access_secret, 
                                             oss_origin=oss_origin, 
                                             bucket_name=bucket_name, 
                                             default_prefix=default_prefix, 
                                             prefix=prefix, 
                                             progress_callback=progress_callback, 
                                             internal=internal)
    except Exception as e:
        raise Exception(f"异步上传目录到 OSS 失败: {e}")

def upload_large_file_to_oss(
    file_path: str,
    ali_access_key_id: str,
    ali_access_secret: str,
    oss_origin: str,
    bucket_name: str,
    default_prefix: Optional[str] = None,
    prefix: Optional[str] = None,
    oss_key: Optional[str] = None,
    internal: bool = True,
    endpoint: Optional[str] = None,
    part_size: int = 5 * 1024 * 1024,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> str:
    """
    多线程分片上传大文件到阿里云 OSS

    Args:
        file_path (str): 本地文件路径
        ali_access_key_id (str): 阿里云 AccessKey ID
        ali_access_secret (str): 阿里云 AccessKey Secret
        oss_origin (str): OSS服务地域，例如 'oss-cn-hangzhou'
        bucket_name (str): OSS Bucket 名
        default_prefix (str, optional): OSS对象默认前缀
        prefix (str, optional): OSS对象自定义前缀
        oss_key (str, optional): OSS对象名，若不指定则自动生成
        internal (bool, optional): 是否使用内网endpoint
        endpoint (str, optional): 自定义endpoint，优先级高于internal/oss_origin拼接
        part_size (int): 分片大小
        progress_callback (callable, optional): 进度回调

    Returns:
        str: 上传完成后OSS对象的key
    """
    # 1. 生成 oss_key
    filename = os.path.basename(file_path)
    if not prefix:
        prefix = datetime.now().strftime("simple_upload_%Y-%m-%d_%H-%M")
    if not default_prefix:
        default_prefix = ""
    if not oss_key:
        oss_key = f"{default_prefix}/{prefix}/{filename}".lstrip("/")
    # 2. 认证与配置
    os.environ["OSS_ACCESS_KEY_ID"] = ali_access_key_id
    os.environ["OSS_ACCESS_KEY_SECRET"] = ali_access_secret
    credentials_provider = oss.credentials.EnvironmentVariableCredentialsProvider()
    cfg = oss.config.load_default()
    cfg.credentials_provider = credentials_provider
    cfg.region = oss_origin.replace("oss-", "")
    if endpoint:
        cfg.endpoint = endpoint
    else:
        # 按 internal 规则拼接 endpoint
        if internal:
            cfg.endpoint = f"https://{oss_origin}-internal.aliyuncs.com"
        else:
            cfg.endpoint = f"https://{oss_origin}.aliyuncs.com"
    client = oss.Client(cfg)

    # 3. 初始化分片上传
    init_result = client.initiate_multipart_upload(oss.InitiateMultipartUploadRequest(
        bucket=bucket_name,
        key=oss_key,
    ))
    upload_id = init_result.upload_id

    # 4. 计算分片信息
    file_size = os.path.getsize(file_path)
    part_count = (file_size + part_size - 1) // part_size
    upload_parts: List[oss.UploadPart] = []
    uploaded_bytes = 0
    lock = threading.Lock()

    def upload_part(part_number, start, size):
        nonlocal uploaded_bytes
        with open(file_path, 'rb') as f:
            f.seek(start)
            reader = oss.io_utils.SectionReader(oss.io_utils.ReadAtReader(f), start, size)
            up_result = client.upload_part(oss.UploadPartRequest(
                bucket=bucket_name,
                key=oss_key,
                upload_id=upload_id,
                part_number=part_number,
                body=reader
            ))
            with lock:
                upload_parts.append(oss.UploadPart(part_number=part_number, etag=up_result.etag))
                uploaded_bytes += size
                if progress_callback:
                    progress_callback(min(uploaded_bytes, file_size), file_size)

    # 5. 多线程上传
    threads = []
    for i in range(part_count):
        start = i * part_size
        size = min(part_size, file_size - start)
        t = threading.Thread(target=upload_part, args=(i + 1, start, size))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

    # 6. 合并分片
    parts_sorted = sorted(upload_parts, key=lambda p: p.part_number)
    complete_result = client.complete_multipart_upload(oss.CompleteMultipartUploadRequest(
        bucket=bucket_name,
        key=oss_key,
        upload_id=upload_id,
        complete_multipart_upload=oss.CompleteMultipartUpload(parts=parts_sorted)
    ))

    return complete_result.key, bucket_name
