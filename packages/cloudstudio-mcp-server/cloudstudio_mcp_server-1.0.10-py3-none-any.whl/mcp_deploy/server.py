from datetime import datetime
import os
from zoneinfo import ZoneInfo
from fastmcp import FastMCP
from .mcp_handlers import createLiteapp, uploadfile, execute, replaceCloudStudioConfig, restartWorkspace, create_share_link_handler, getAutoRunLog
from .mcp_handlers import File
from .models import CloudStudioConfig, CloudStudioConfigApp

mcp = FastMCP("mcp-deploy")

api_token = os.environ.get("API_TOKEN")
if not api_token:
    raise ValueError("API_TOKEN environment variable is required")
region = os.environ.get("region", "ap-shanghai")
if region == "ap-shanghai":
    region =  "ap-shanghai2"

@mcp.tool()
def create_workspace(title: str) -> dict:
    """
    # 创建Cloud Studio工作空间（含服务预览基础信息）
    ## 核心功能
    - 初始化工作空间，生成唯一标识（`space_key`）、编辑器链接、预览链接模板
    - 自动关联轻应用（`lite_app_id`），支持后续代码编辑与服务访问

    ## 参数说明
    | 参数名   | 类型   | 必填/可选 | 约束条件                                  | 说明                                      |
    |----------|--------|-----------|-------------------------------------------|-------------------------------------------|
    | title    | str    | 必填      | 1. 无特殊字符）<br>2. 长度≤50字符 | 工作空间名称，如"My-Python-Web"           |

    ## 依赖环境变量
    | 变量名    | 说明                                      | 获取途径                                  |
    |-----------|-------------------------------------------|-------------------------------------------|
    | API_TOKEN | 工作空间操作认证令牌（无令牌拒绝请求）     | Cloud Studio控制台→个人设置→API密钥        |

    ## 返回值说明（核心字段关联）
    | 返回字段   | 用途                                      | 关联工具                                  |
    |------------|-------------------------------------------|-------------------------------------------|
    | space_key  | 工作空间唯一ID（后续操作核心标识）         | write_files/execute_command等所有工具      |
    | edit_url   | 代码编辑器访问链接（含lite_app_id）       | 直接提供给用户编辑代码                    |
    | preview    | 预览链接模板（需替换{port}为实际端口）     | execute_command生成预览链接时使用          |
    | lite_app_id| 轻应用ID（拼接编辑链接）                  | 编辑链接格式：https://cloudstudio.net/a/{lite_app_id}/edit |

    ## 错误处理
    | 异常类型       | 可能原因                                  | 解决方案                                  |
    |----------------|-------------------------------------------|-------------------------------------------|
    | ValueError     | title含特殊字符/长度超50字符              | 移除非法字符，缩短名称至50字符内           |
    | PermissionError| API_TOKEN无效/过期                      | 重新获取有效令牌并配置环境变量             |

    ## 示例
    >>> create_workspace(title="Python-Flask-Web")
    {
        "space_key": "c148150324034f2580d775a9c0057b52",
        "title": "Python-Flask-Web",
        "edit_url": "https://cloudstudio.net/a/23728372/edit",
        "webIDE": "https://cloudstudio.net/ide/23728372",
        "preview": "https://{space_key}--{port}.ap-beijing.cloudstudio.club",
        "lite_app_id": "23728372"
    }
    """
    result = createLiteapp(api_token, title)
    return result

@mcp.tool()
def write_files(space_key: str, directory: str = None, files: list[File]=[]) -> dict:
    """上传文件到指定工作空间
    将多个文件上传到Cloud Studio工作空间，支持单文本路径的上传和目录上传，也支持单文件内容直接写入。

    核心上传策略：
    1. 优先使用directory参数：当上传完整项目且满足以下条件时，优先传递directory参数
       - 文件夹大小≤300MB
       - 非单个文件上传场景
    2. 必须使用files参数：当出现以下任意一种情况时，使用files参数上传
       - 文件夹大小＞300MB
       - 仅需上传单个或指定少数文件
       - 明确需要精确控制上传文件范围时
       - 如果是本地文件，一定要优先提供 local_path:

    多文件处理规则：
    - 当files列表包含10个及以上文件时，需按每5-10个文件为一组进行分组
    - 各组需通过多线程并发调用本接口完成上传，提升效率

    Args:
        space_key (str): 目标工作空间ID，格式如'xxxxxx'
        region (str): 工作空间所在区域，如'ap-shanghai'
        directory (str, optional): 本地目录绝对路径，若提供将压缩上传该目录下所有文件（自动排除非必要文件），最终文件直接存放于/workspace下（不额外创建源目录名文件夹）
        files (list[File], optional): 要上传的文件列表，每个File对象包含，注意，如果是本地文件，一定要优先提供 local_path:
            - save_path: str 文件在workspace中的相对路径，如/example/xxx.txt（最终路径为/workspace/example/xxx.txt）
            - local_path: str 本地文件绝对路径，若提供将读取文件内容（最终路径规则同save_path
            - file_content: str 文件内容(UTF-8编码)，仅本地文件不存在时使用，优先级低于local_path


    Returns:
        status: str # 上传结果信息，completed代表完成
        total_operations: int # 总共文件数
        success_count: int # 成功文件数
        failed_count: int # 失败文件数
        details: array # 解压结果

    Raises:
        ValueError: 若workspace_id格式无效，或directory与files同时为空
        IOError: 文件上传过程中出现IO错误
        TypeError: files参数格式不正确
        FileNotFoundError: 指定的目录不存在

    Example:
        1. 上传小型纯净项目（无排除文件，≤300MB）
        >>> write_files("123", directory="/local/project")
        本地/project目录下所有文件将上传至/workspace

        2. 上传需排除文件的项目（如含.git文件夹）
        >>> write_files("123", files=[
                {"save_path": "/src/main.py", "local_path": "/local/project/src/main.py"},
                {"save_path": "/config.json", "local_path": "/local/project/config.json"}
            ])
        仅上传指定文件至/workspace对应路径

        3. 上传15个文件（自动分2组并发上传）
        >>> write_files("123", "ap-shanghai", files=[...15个文件对象...])
        自动分2组（如前10后5）并发处理

    注意事项:
    - 若上下文无工作空间，需先创建再上传
    - 目录上传时会自动过滤非必要文件，无需手动处理
    - 大文件（单文件＞50MB）建议通过files参数单独上传，避免压缩超时
    """

    if space_key is None:
        raise ValueError("Invalid workspace_id format")
    if not files and not directory:
        raise ValueError("No files to upload")

    success = uploadfile(api_token, space_key, region, files, directory)
    return success

@mcp.tool()
def execute_command(space_key: str, command: str) -> dict:
    """
    ### 1. 核心功能
    在 Cloud Studio 工作空间执行 Shell 命令（默认工作目录：`/workspace`），支持两类场景：
    - 普通操作：安装依赖（如 `pip install`/`npm install`）、文件操作等；
    - 服务启动：启动 Web 等长期服务，并生成 **个人预览链接**（仅本人可访问，外部服务禁用）。

    ### 2. 关键权限边界（必看）
    - 个人预览链接：仅工具调用者本人可访问（绑定账号权限），其他用户/外部服务（如接口调用、爬虫）访问会提示「无权限」；
    - 外部访问替代：如果需要分享链接，需调用 `create_share_link_with_command` 工具生成专属分享链接，不可用此工具的链接对外提供。

    ### 3. 参数说明
    | 参数名    | 类型   | 必填 | 约束规则                                                                 |
    |-----------|--------|------|--------------------------------------------------------------------------|
    | space_key | str    | ✅   | 需与 `create_workspace` 返回的 `space_key` 完全一致（例："c148150324034f2580d775a9c0057b52"） |
    | command   | str    | ✅   | 分场景约束：<br>① 普通命令：无特殊格式（例：`pip install flask`）；<br>② 服务命令：必须含 `nohup`+明确端口（例：`nohup python app.py --port 3000 > /dev/null 2>&1 &`） |

    ### 4. 核心规则（服务启动+链接生成）
    #### 4.1 服务启动命令格式（强制）
    长期服务需用 `nohup` 确保进程不终止，格式固定：
    `nohup [服务命令 --port 端口号] > /dev/null 2>&1 &`
    各部分作用：
    - `nohup`：终端关闭后进程持续运行；
    - `--port 端口号`：明确端口（1024≤端口≤65535），用于生成预览链接；
    - `> /dev/null 2>&1`：丢弃日志，避免占用磁盘；
    - `&`：进程放入后台，不阻塞后续操作。

    #### 4.2 个人预览链接生成
    - 生成条件：服务启动后，通过 `lsof -i:端口号` 确认端口处于 `LISTEN` 状态；
    - 链接模板：`https://{space_key}--{端口号}.{region}.cloudstudio.club`；
    - 有效性：与工作空间状态绑定（空间关闭则链接失效）。

    ### 5. 错误处理
    | 异常类型         | 触发场景                                  | 解决方案                                                                 |
    |------------------|-------------------------------------------|--------------------------------------------------------------------------|
    | ValueError       | ① space_key 为空；② region 错误；③ 服务命令无端口；④ command 为空 | ① 从 `create_workspace` 取有效 `space_key`；② 换为 `ap-shanghai`/`ap-beijing`；③ 补充 `--port 端口`；④ 传非空命令 |
    | RuntimeError     | ① 命令退出码非0；② 端口无 LISTEN；③ 个人链接外部访问失败 | ① 看 `stderr` 定位错误（如依赖缺失）；② 延长 `sleep`（例：`sleep 5 && lsof -i:3000`）；③ 用 `create_share_link_with_command` 生成外部链接 |
    | PermissionError  | ① API_TOKEN 无效；② 非本人访问个人链接 | ① 重新获取 API_TOKEN（控制台→个人设置→API 密钥）；② 仅本人使用个人链接 |

    ### 6. 返回值说明
    | 字段名                  | 类型   | 含义                                                                 |
    |-------------------------|--------|----------------------------------------------------------------------|
    | exitCode                | str    | 退出码："0" 成功，非"0" 失败（触发 RuntimeError）                     |
    | stdout                  | str    | 命令标准输出（如端口检查结果、安装日志）                              |
    | stderr                  | str    | 命令错误输出（无错误则为空）                                          |
    | startTime               | str    | 命令开始时间（秒级时间戳）                                            |
    | endTime                 | str    | 命令结束时间（秒级时间戳）                                            |

    ### 7. 使用示例
    #### 示例1：启动 Flask 服务+生成个人链接
    ```python
    # 1. 启动服务（端口3000）
    start_res = execute_command(
        space_key="c148150324034f2580d775a9c0057b52",
        command="nohup python app.py --port 3000 > /dev/null 2>&1 &"
    )
    # 2. 检查端口（等待5秒初始化）
    check_res = execute_command(
        space_key="c148150324034f2580d775a9c0057b52",
        command="sleep 5 && lsof -i:3000"
    )
    # 3. 输出个人链接（仅本人可访问）
    if "LISTEN" in check_res["stdout"]:
        print(check_res["personal_preview_hint"])

    示例 2：安装 Flask 依赖（普通命令）
        python
        install_res = execute_command(
            space_key="c148150324034f2580d775a9c0057b52",
            command="pip install flask -i https://pypi.tuna.tsinghua.edu.cn/simple"
        )
        print(f"安装结果：{install_res['stdout'][:100]}...")
    """
    if space_key is None:
        raise ValueError("Invalid workspace_id format")
    if not command:
        raise ValueError("Command cannot be empty")

    result = execute(api_token, space_key, region, command)
    return result

@mcp.tool()
def create_share_link_with_command(space_key: str, title: str, port: int, command: str) -> dict:
    """
    核心功能：配置服务自启动命令→重启工作空间生效→生成外部可访问的分享链接，支持失败日志排查
    关键场景：项目对外演示（如给客户看Demo）、跨设备访问（如手机/其他电脑打开服务）

    参数说明（强约束，避免端口/命令不匹配）：
    | 参数名     | 类型   | 必填性 | 约束规则                                                                 |
    |------------|--------|--------|--------------------------------------------------------------------------|
    | space_key  | str    | 必选   | 需与`create_workspace`返回的`space_key`一致（如"c148150324034f2580d775a9c0057b52"） |
    | title      | str    | 必选   | 1. 服务名称（将显示在分享链接页面）<br>2. 无特殊字符）<br>3. 长度≤50字符 |
    | port       | int    | 必选   | 1. 合法端口范围：1024 ≤ port ≤ 60000（避免系统端口冲突）<br>2. 必须与`command`中的端口一致 |
    | command    | str    | 必选   | 1. 服务启动命令（无需加`nohup`/`&`，工具自动处理后台运行）<br>2. 必须含`--port {port}`（如"python app.py --port 3000"） |

    关键逻辑（确保服务可访问，避免无效链接）：
    1. 端口一致性校验：`command`必须含`--port {port}`（如port=3000，command需有"--port 3000"），否则服务与链接端口不匹配，无法访问。
    2. 自启动配置：工具会将`command`写入工作空间配置，重启后自动执行（无需每次手动启动）。
    3. 启动失败排查：若`command_result`（端口检查结果）无"LISTEN"，需调用`get_auto_run_log`查看日志（如缺依赖、端口占用）。

    错误处理（覆盖配置/启动/链接生成全流程）：
    | 异常类型         | 触发场景                                  | 解决方案                                                                 |
    |------------------|-------------------------------------------|--------------------------------------------------------------------------|
    | ValueError       | 1. port不在1024-65535<br>2. command不含`--port {port}`<br>3. title含特殊字符/超30字符 | 1. 调整port至合法范围（如3000/8080）<br>2. 补充端口参数（如"python app.py --port 3000"）<br>3. 移除非法字符/缩短title |
    | RuntimeError     | 1. 工作空间重启失败<br>2. 服务启动后端口无LISTEN<br>3. 分享链接生成失败 | 1. 检查`space_key`/`region`是否正确，重新调用工具<br>2. 调用`get_auto_run_log`查看日志排查服务错误<br>3. 确认API_TOKEN有效，重试链接生成 |
    | 分享链接无法打开 | 1. 服务未启动（command_result无LISTEN）<br>2. 端口映射错误 | 1. 按日志修复服务后重新生成链接<br>2. 确认`port`与`command`端口一致，重启工作空间 |

    返回值说明（含关键访问信息）：
    | 字段名         | 类型   | 含义                                                                 |
    |----------------|--------|----------------------------------------------------------------------|
    | share_url      | str    | 外部可访问的分享链接（如"https://c148...--3000.ap-shanghai.cloudstudio.club"） |
    | scheme         | str    | 链接协议（固定为"https"）                                            |
    | port           | int    | 服务监听端口（与输入`port`一致）                                      |
    | expire_time      | int  | 链接过期时间(格式：%Y-%m-%d %H:%M:%S)                              |
    | command_result | dict   | 服务启动后的端口检查结果（含`stdout`/`stderr`，成功时`stdout`含"LISTEN"） |
    | title          | str    | 服务名称（与输入`title`一致）                                        |

    示例（完整生成分享链接流程）：
    >>> # 前提：已创建工作空间（space_key）、上传项目文件、安装依赖
    >>> share_result = create_share_link_with_command(
        space_key="c148150324034f2580d775a9c0057b52",
        title="Flask-Demo-2024",  # 符合title约束
        port=3000,                # 合法端口
        command="python app.py --port 3000"  # 含端口参数，无需nohup
    )
    >>> # 输出关键信息
    >>> print(f"✅ 分享链接生成成功！")
    >>> print(f"🔗 访问地址：{share_result['share_url']}")
    >>> print(f"⏰ 有效期至：{share_result['expire_time']}")
    >>> print(f"📝 服务端口检查结果：{share_result['command_result']['stdout']}")
    """
    # 1. 配置CloudStudio应用
    config = CloudStudioConfig(
        app=[CloudStudioConfigApp(
            cmd=command,
            port=port,
            name=title
        )]
    )
    
    # 2. 替换CloudStudio配置
    config_result = replaceCloudStudioConfig(api_token, space_key, region, config)
    
    # 3. 重启工作空间以应用配置
    restart_result = restartWorkspace(api_token, space_key, region)
    
    # 4. 等待工作空间重启完成
    wait_result = execute(api_token, space_key, region, f"sleep 5 && lsof -i:{port}")
    
    # 5. 创建分享连接
    share_link = create_share_link_handler(api_token, space_key, region, port)
    
    # 6. 构建完整的分享URL
    share_url = f"{share_link.data.scheme}://{share_link.data.host}"
    
    return {
        "share_url": share_url,
        "port": share_link.data.targetPort,
        "expire_time": datetime.fromtimestamp(int(share_link.data.expireAt),ZoneInfo('Asia/Shanghai')).strftime("%Y-%m-%d %H:%M:%S"),
        "command_result": wait_result
    }

@mcp.tool()
def get_auto_run_log(space_key: str, delay: int = 3000, title: str = None) -> dict:
    """
    核心功能：获取工作空间中服务的自动运行日志，支持按服务名称（title）过滤，解决「服务启动失败但无明确错误」问题
    关键场景：1. `create_share_link_with_command`返回启动失败<br>2. 分享链接访问报错（如500/404）<br>3. 服务运行中突然崩溃

    参数说明（灵活适配单/多服务场景）：
    | 参数名     | 类型   | 必填性 | 约束规则                                                                 |
    |------------|--------|--------|--------------------------------------------------------------------------|
    | space_key  | str    | 必选   | 需与`create_workspace`返回的`space_key`一致（如"c148150324034f2580d775a9c0057b52"） |
    | delay      | int    | 可选   | 1. 延迟时间（毫秒），等待日志生成（避免日志未写入）<br>2. 最小值：1000ms（1秒），默认3000ms |
    | title      | str    | 可选   | 1. 服务名称（需与`create_share_link_with_command`的`title`一致）<br>2. 不传递则返回所有服务日志 |

    日志解析指引（常见错误关键词+解决方案，降低排查成本）：
    | 日志关键词                | 错误类型                          | 解决方案（需调用`execute_command`执行）                                  |
    |---------------------------|-----------------------------------|--------------------------------------------------------------------------|
    | ModuleNotFoundError        | Python依赖缺失（如"No module named 'flask'"） | `pip install flask -i https://pypi.tuna.tsinghua.edu.cn/simple`          |
    | Cannot find module         | Node依赖缺失（如"Cannot find module 'vue'"） | `npm install vue --registry=https://registry.npm.taobao.org`             |
    | Address already in use     | 端口被占用（如"port 3000 is already in use"） | `kill -9 $(lsof -t -i:3000)`（强制杀死占用端口的进程）                  |
    | Permission denied          | 文件权限不足（如"Permission denied: '/workspace/app.py'"） | `chmod 755 /workspace/app.py`（赋予文件读写执行权限）                    |
    | SyntaxError                | 代码语法错误（如"invalid syntax"） | 打开工作空间编辑器（edit_url），修改对应文件的语法错误                  |
    | Connection refused         | 服务未监听端口（如"Connection refused to 127.0.0.1:3000"） | 检查服务启动命令是否含`--port`，重新启动服务                            |

    错误处理（覆盖日志获取全流程）：
    | 异常类型         | 触发场景                                  | 解决方案                                                                 |
    |------------------|-------------------------------------------|--------------------------------------------------------------------------|
    | ValueError       | 1. space_key为空<br>2. delay<1000ms       | 1. 从`create_workspace`获取有效`space_key`<br>2. 调整delay≥1000ms（如5000ms） |
    | RuntimeError     | 1. 工作空间未启动<br>2. 日志获取接口调用失败 | 1. 先调用`create_workspace`启动空间<br>2. 检查API_TOKEN有效性，重试工具调用 |
    | 日志为空         | 1. title错误（无对应服务）<br>2. delay不足（日志未生成）<br>3. 服务未运行 | 1. 核对title是否与`create_share_link_with_command`一致<br>2. 增加delay至5000-10000ms<br>3. 先启动服务（调用`create_share_link_with_command`） |

    返回值说明（结构化日志，便于解析）：
    | 字段名     | 类型   | 含义                                                                 |
    |------------|--------|----------------------------------------------------------------------|
    | status     | str    | 日志获取状态（"success"表示成功，"error"表示失败）                    |
    | message    | str    | 状态描述（如"成功获取1个服务的日志"、"未获取到日志，可能title错误"）   |
    | data       | dict   | 日志数据（key：服务名称(title)，value：该服务的完整运行日志）          |

    示例（排查Flask服务启动失败）：
    >>> # 前提：`create_share_link_with_command`返回启动失败，title="Flask-Demo-2024"
    >>> log_result = get_auto_run_log(
        space_key="c148150324034f2580d775a9c0057b52",
        delay=5000,  # 增加延迟，确保日志生成
        title="Flask-Demo-2024"  # 过滤指定服务日志
    )
    >>> # 解析日志结果
    >>> if log_result["status"] == "success":
        service_log = log_result["data"]["Flask-Demo-2024"]
        print(f"✅ 服务日志：\n{service_log}")
        # 检查是否含依赖缺失错误
        if "ModuleNotFoundError: No module named 'flask'" in service_log:
            print("\n❌ 错误原因：缺少Flask依赖")
            print("✅ 解决方案：执行`execute_command`安装Flask")
            # 调用execute_command安装依赖
            execute_command(
                space_key="c148150324034f2580d775a9c0057b52",
                command="pip install flask -i https://pypi.tuna.tsinghua.edu.cn/simple"
            )
    else:
        print(f"❌ 获取日志失败：{log_result['message']}")
    """
    result = getAutoRunLog(api_token, space_key, region, delay, title)
    return {
        "data": result.data
    }

def main():
    mcp.run()

if __name__ == "__main__":
    main()
