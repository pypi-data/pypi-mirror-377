import json
import logging
import requests
import os
from typing import Optional, Dict, Union, Any
from dataclasses import asdict
from .models import Connections, WorkspaceStatus, RuntimePool, Runtime, LiteAppRequest, VGPUConfig, GPUConfig, \
    RuntimeSpec, Storage, CBDStorage, WorkspaceResponse, LiteAppResponse, WorkspaceResponseData, WorkspaceRequest, \
    CommandInput, CloudStudioConfig, CloudStudioConfigApp, CloudStudioConfigResponse, AutoRunLogResponse, \
    CommandOutput, LiteAppResponseData, RestartWorkspaceResponse, ShareLinkRequest, ShareLinkResponse, ShareLinkResponseData
from .models import File

# 配置日志 - 只使用控制台输出
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


def createworkspace(
        api_token: str,
        cpu: str = "1",
        memory: str = "2",
        storage_quota: str = "1024M",
        pool_name: Optional[str] = None,
        pool_owner_token: Optional[str] = None,
) -> dict[str, Optional[str]]:
    """创建一个工作空间并返回spaceKey"""
    if not all([cpu, memory, storage_quota]):
        raise ValueError("CPU, memory and storage_quota are required")

    request = WorkspaceRequest()

    logger.debug(f"Creating workspace with request: {request}")
    response = requests.post(
        "https://api.cloudstudio.net/workspaces",
        data=request.to_json(),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {api_token}"
        },
        timeout=30
    )
    response.raise_for_status()
    response_data = response.json()

    if not all(field in response_data for field in ['code', 'msg', 'data']):
        raise ValueError("Invalid response structure")

    workspace_response = WorkspaceResponse(
        code=response_data['code'],
        msg=response_data['msg'],
        data=WorkspaceResponseData(
            spaceKey=response_data['data']['spaceKey'],
            connections=Connections(**response_data['data']['connections']),
            runtime=Runtime(**response_data['data']['runtime']),
            runtimeSpec=RuntimeSpec(**response_data['data']['runtimeSpec']),
            storage=Storage(
                cbd=CBDStorage(
                    id=response_data['data']['storage']['diskId'],
                    quota=response_data['data']['storage']['quota']
                ),
                type="cbd"
            ),
            status=WorkspaceStatus(**response_data['data']['status'])
        )
    )

    logger.info(f"Created workspace {workspace_response.data}")
    logger.info(f"Created workspace {workspace_response.data.spaceKey}")
    return {
        "space_key": workspace_response.data.spaceKey,
        "webIDE": workspace_response.data.connections.webIDE,
        "preview": workspace_response.data.connections.preview,
    }


def createLiteapp(
        api_token: str,
        title="",
) -> dict[str, Optional[str]]:
    """创建一个工作空间并返回spaceKey"""

    request = LiteAppRequest(title=title)

    logger.debug(f"Creating workspace with request: {request}")
    response = requests.post(
        "https://api.cloudstudio.net/liteapps",
        data=request.to_json(),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {api_token}"
        },
        timeout=30
    )
    logger.debug(f"Creating workspace with response: {response}")
    logger.debug(f"Creating workspace with api token: {api_token}")
    response.raise_for_status()
    response_data = response.json()

    if not all(field in response_data for field in ['code', 'msg', 'data']):
        raise ValueError("Invalid response structure")
    logger.info(f"Created workspace {response_data}")
    workspace_response = LiteAppResponse(
        code=response_data['code'],
        msg=response_data['msg'],
        data=LiteAppResponseData(title=response_data['data']['title'],
                                 id=response_data['data']['id'],
                                 workspace=WorkspaceResponseData(
                                     spaceKey=response_data['data']['workspace']['spaceKey'],
                                     connections=Connections(**response_data['data']['workspace']['connections']))
                                 )
    )

    logger.info(f"Created workspace {workspace_response.data}")
    return {
        "space_key": workspace_response.data.workspace.spaceKey,
        "webIDE": workspace_response.data.workspace.connections.webIDE,
        "preview": workspace_response.data.workspace.connections.preview,
        "lite_app_id": workspace_response.data.id,
        "title": workspace_response.data.title,
        "edit_url": f"https://cloudstudio.net/a/{workspace_response.data.id}/edit",
    }


import tempfile
import zipfile
import os
import shutil
from pathlib import Path


def uploadfile(api_token: str, space_key: str, region: str, files: list[File],
               directory: Optional[str] = None) -> Union[dict[str, Union[str, int, list[Any]]], str]:
    """上传文件到指定工作空间，支持文件列表和目录上传"""

    server_url = f"https://{space_key}--api.{region}.cloudstudio.club"
    try:
        results = []

        # 处理目录上传
        if directory:
            if not os.path.isdir(directory):
                raise FileNotFoundError(f"目录不存在: {directory}")

            logger.info(f"准备上传目录: {directory}")

            # 创建临时zip文件
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
                temp_zip_path = temp_zip.name

            try:
                # 压缩目录
                with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    base_path = Path(directory)
                    for file_path in base_path.rglob('*'):
                        if file_path.is_file():
                            # 计算相对路径
                            relative_path = file_path.relative_to(base_path)
                            zipf.write(file_path, arcname=relative_path)
                            logger.debug(f"添加文件到压缩包: {relative_path}")

                # 上传zip文件
                zip_upload_path = "temp_upload.zip"
                with open(temp_zip_path, 'rb') as zip_file:
                    zip_content = zip_file.read()

                upload_url = f"{server_url}/filesystem/workspace/{zip_upload_path}"
                logger.info(f"上传压缩文件到: {upload_url}")

                response = requests.post(
                    upload_url,
                    data=zip_content,
                    headers={
                        "Accept": "application/json",
                        "Content-Type": "application/octet-stream",
                        "Authorization": f"Bearer {api_token}"
                    },
                    # verify=False,
                    timeout=30  # 增加超时时间，因为压缩文件可能较大
                )

                response.raise_for_status()
                results.append({
                    "path": zip_upload_path,
                    "status": "success",
                    "response": response.json()
                })

                # 在远程服务器上解压文件
                unzip_command = f"unzip -o /workspace/{zip_upload_path} -d /workspace/ && rm /workspace/{zip_upload_path}"

                # 直接调用远程命令执行API，避免循环导入
                execute_url = f"{server_url}/console"
                execute_response = requests.post(
                    execute_url,
                    json={"command": unzip_command},
                    headers={
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_token}"
                    },
                    # verify=False,
                    timeout=60  # 解压可能需要更长时间
                )
                execute_response.raise_for_status()
                execute_result = execute_response.json()

                logger.info(f"解压结果: {execute_result}")
                results.append({
                    "path": "directory_extraction",
                    "status": "success",
                    "response": execute_result
                })

            finally:
                # 清理临时文件
                if os.path.exists(temp_zip_path):
                    os.unlink(temp_zip_path)

        # 处理文件列表上传
        if files:
            # 验证文件数据
            for idx, file in enumerate(files):
                if not file.save_path:
                    raise ValueError(f"文件#{idx + 1}的save_path不能为空")
                if file.file_content is None and not file.local_path:
                    raise ValueError(f"文件#{idx + 1}的file_content不能为None")

            # 对每个文件单独上传
            for file in files:
                # 确保路径格式正确（移除开头的斜杠）
                filepath = file.save_path.lstrip('/')
                upload_url = f"{server_url}/filesystem/workspace/{filepath}"

                logger.info(f"上传文件到: {upload_url}")

                # 将文件内容转换为字节流
                if file.local_path and os.path.isfile(file.local_path):
                    with open(file.local_path, 'rb') as f:
                        file_content = f.read()
                else:
                    if isinstance(file.file_content, str):
                        file_content = file.file_content.encode('utf-8')
                    else:
                        file_content = file.file_content

                response = requests.post(
                    upload_url,
                    data=file_content,  # 直接发送文件内容
                    headers={
                        "Accept": "application/json",
                        "Content-Type": "application/octet-stream",
                        "Authorization": f"Bearer {api_token}"
                    },
                    # verify=False,  # 临时禁用SSL验证，仅用于开发测试
                    timeout=30
                )

                response.raise_for_status()
                results.append({
                    "path": filepath,
                    "status": "success",
                    "response": response.json()
                })
        elif not directory:
            logger.warning("没有文件或目录需要上传")
            return json.dumps({"status": "success", "message": "没有文件或目录需要上传"})

        # 记录并返回详细的上传结果
        success_count = len([r for r in results if r['status'] == 'success'])
        failed_count = len(results) - success_count

        logger.info(f"上传完成 - 成功: {success_count}, 失败: {failed_count}")
        for result in results:
            if result['status'] == 'success':
                logger.info(f"{result['path']} 上传成功")
            else:
                logger.error(f"{result['path']} 上传失败: {result.get('error', '未知错误')}")

        return {
            "status": "completed",
            "total_operations": len(results),
            "success_count": success_count,
            "failed_count": failed_count,
            "details": results
        }

    except requests.exceptions.RequestException as e:
        error_msg = f"文件上传失败: {str(e)}"
        if e.response is not None:
            error_msg += f", 响应: {e.response.text}"
        logger.error(error_msg)
        raise
    except Exception as e:
        logger.error(f"文件上传处理失败: {str(e)}")
        raise


def execute(api_token: str, space_key: str, region: str, command: str):
    """执行命令并返回结果"""
    server_url = f"https://{space_key}--api.{region}.cloudstudio.club"
    try:
        command_input = CommandInput(
            command=command,
            timeoutMs=300000,
            maxOutputSize=10000000
        )
        logger.info(f"Server URL: {server_url}")
        logger.info(f"Executing command: {asdict(command_input)}")
        logger.info(f"api_token: {api_token}")
        response = requests.post(
            url=f"{server_url}/console",
            json=asdict(command_input),  # 使用json参数让requests处理序列化
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_token}"
            },
            timeout=300
        )

        # 先获取响应文本用于调试
        response_text = response.text
        if not response_text.strip():
            raise ValueError("Empty response from server")

        try:
            response_json = response.json()
            logger.info(f"command output: {response_json}")
            return response_json
        except json.JSONDecodeError as json_err:
            logger.error(f"Failed to parse JSON response: {json_err}\nResponse text: {response_text}")
            raise ValueError(f"Invalid JSON response: {response_text}") from json_err

    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request failed: {str(req_err)}")
        raise
    except Exception as e:
        logger.error(f"Command execution failed: {str(e)}")
        raise


def replaceCloudStudioConfig(api_token: str, space_key: str, region: str, config: CloudStudioConfig) -> CloudStudioConfigResponse:
    """替换工作空间的 CloudStudio 配置
    
    Args:
        api_token: API令牌
        space_key: 工作空间key
        region: 区域
        config: CloudStudio配置对象
        
    Returns:
        CloudStudioConfigResponse: 配置响应对象
    """
    server_url = f"https://{space_key}--pty.{region}.cloudstudio.club"
    try:
        # 构建请求URL
        url = f"{server_url}/replaceCloudStudioConfig"

        logger.info(f"Replacing CloudStudio config for workspace {space_key}")
        
        # 发送请求
        response = requests.post(
            url=url,
            data=json.dumps(asdict(config)),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {api_token}"
            },
            timeout=30
        )
        
        response.raise_for_status()
        response_data = response.json()
        
        # 解析响应
        config_response = CloudStudioConfigResponse(
            code=response_data.get('code', 0),
            msg=response_data.get('msg', '')
        )
        
        logger.info(f"CloudStudio config replaced: {config_response.msg}")
        return config_response
        
    except requests.exceptions.RequestException as e:
        error_msg = f"替换CloudStudio配置失败: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            error_msg += f", 响应: {e.response.text}"
        logger.error(error_msg)
        raise
    except Exception as e:
        logger.error(f"替换CloudStudio配置处理失败: {str(e)}")
        raise


def restartWorkspace(api_token: str, space_key: str, region: str) -> RestartWorkspaceResponse:
    """重启工作空间
    
    Args:
        api_token: API令牌
        space_key: 工作空间key
        region: 区域
        
    Returns:
        RestartWorkspaceResponse: 重启响应对象
    """
    try:
        # 构建请求URL
        url = f"https://bpi.cloudstudio.net/workspaces/{space_key}/restart"
        
        logger.info(f"Restarting workspace {space_key}")
        
        # 发送请求
        response = requests.get(
            url=url,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {api_token}"
            },
            timeout=30
        )
        
        response.raise_for_status()
        response_data = response.json()
        restart_response = RestartWorkspaceResponse(
            code=response_data.get('code', ''),
            msg=response_data.get('msg', '')
        )
        if restart_response.code != 0:
            raise restart_response.msg

    except requests.exceptions.RequestException as e:
        error_msg = f"重启工作空间失败: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            error_msg += f", 响应: {e.response.text}"
        logger.error(error_msg)
        raise
    except Exception as e:
        logger.error(f"重启工作空间处理失败: {str(e)}")
        raise


def getAutoRunLog(api_token: str, space_key: str, region: str, delay: int = 3000, title: str = None) -> AutoRunLogResponse:
    """获取自动运行日志
    
    Args:
        api_token: API令牌
        space_key: 工作空间key
        region: 区域
        delay: 延迟时间（毫秒），默认3000
        title: 应用名称，可选
        
    Returns:
        AutoRunLogResponse: 自动运行日志响应对象
    """
    server_url = f"https://{space_key}--pty.{region}.cloudstudio.club"
    try:
        # 构建请求URL，添加查询参数
        url = f"{server_url}/getAutoRunLog"
        params = {"delay": delay}
        if title:
            params["name"] = title
            
        logger.info(f"Getting auto run log for workspace {space_key}, name {title}, delay {delay}ms")
        
        # 发送请求
        response = requests.get(
            url=url,
            params=params,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {api_token}"
            },
            timeout=30 + (delay / 1000)  # 增加超时时间，考虑延迟因素
        )
        
        response.raise_for_status()
        response_data = response.json()
        
        # 解析响应
        auto_run_log_response = AutoRunLogResponse(
            data=response_data.get('data', {})
        )
        
        logger.info(f"Auto run log retrieved for workspace {space_key}")
        return auto_run_log_response
        
    except requests.exceptions.RequestException as e:
        error_msg = f"获取自动运行日志失败: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            error_msg += f", 响应: {e.response.text}"
        logger.error(error_msg)
        raise
    except Exception as e:
        logger.error(f"获取自动运行日志处理失败: {str(e)}")
        raise


def create_share_link_handler(api_token: str, space_key: str, region: str, port: int) -> ShareLinkResponse:
    """创建工作空间端口分享连接
    
    Args:
        api_token: API令牌
        space_key: 工作空间key
        region: 区域
        port: 需要分享的端口号
        
    Returns:
        ShareLinkResponse: 分享连接响应对象
    """
    url = f"https://bpi.cloudstudio.net"
    try:
        # 构建请求URL
        url = f"{url}/workspaces/{space_key}/links"
        
        # 构建请求体
        request = ShareLinkRequest(port=port)
        
        logger.info(f"Creating share link for workspace {space_key}, port {port}")
        
        # 发送请求
        response = requests.post(
            url=url,
            data=request.to_json(),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {api_token}"
            },
            timeout=30
        )
        
        response.raise_for_status()
        response_data = response.json()
        
        # 解析响应
        share_link_response = ShareLinkResponse(
            code=response_data.get('code', 0),
            message=response_data.get('message', ''),
            data=ShareLinkResponseData(
                host=response_data['data']['host'],
                scheme=response_data['data']['scheme'],
                targetPort=response_data['data']['targetPort'],
                expireAt=response_data['data']['expireAt']
            )
        )
        
        logger.info(f"Share link created: {share_link_response.data.host}")
        return share_link_response
        
    except requests.exceptions.RequestException as e:
        error_msg = f"创建分享连接失败: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            error_msg += f", 响应: {e.response.text}"
        logger.error(error_msg)
        raise
    except Exception as e:
        logger.error(f"创建分享连接处理失败: {str(e)}")
        raise