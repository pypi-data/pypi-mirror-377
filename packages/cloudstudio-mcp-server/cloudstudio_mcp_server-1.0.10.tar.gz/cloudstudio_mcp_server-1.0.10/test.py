from src.mcp_deploy.mcp_handlers import createworkspace,execute, createLiteapp, uploadfile, replaceCloudStudioConfig, restartWorkspace, create_share_link_handler
from src.mcp_deploy.models import File, CloudStudioConfig, CloudStudioConfigApp, ShareLinkRequest

# 测试创建工作空间
workspace_result = createLiteapp(
    api_token="eyJhbGciOiJIUzI1NiJ9.eyJ1c2VySWQiOjM2NzI5NCwiaWF0IjoxNzU0OTc4OTQwLCJleHAiOjE3NjI3MDQwMDAsImp0aSI6IjA3MzcwZThjLWRkMjctNGQ0Yi1iOTU1LWYzYjg1OTUxM2Y3YyJ9.OYHgEX3njwKVSsSsr7DBoFL2dCE0kiMEoe0IXe8_dcQ",
    title="mcp 测试"
)
print("创建工作空间结果:", workspace_result)
new_space_key = workspace_result["space_key"]
print("新创建的工作空间 space_key:", new_space_key)
print("新创建的工作空间 uri:", workspace_result["edit_url"])

# 定义通用参数
api_token = "eyJhbGciOiJIUzI1NiJ9.eyJ1c2VySWQiOjM2NzI5NCwiaWF0IjoxNzU0OTc4OTQwLCJleHAiOjE3NjI3MDQwMDAsImp0aSI6IjA3MzcwZThjLWRkMjctNGQ0Yi1iOTU1LWYzYjg1OTUxM2Y3YyJ9.OYHgEX3njwKVSsSsr7DBoFL2dCE0kiMEoe0IXe8_dcQ"
region = "ap-shanghai2"

# 测试上传文件
upload = uploadfile(
    api_token=api_token,
    space_key=new_space_key,  # 使用新创建的工作空间
    region=region,
    files=[
        File(
            save_path="/test_app.py",
            local_path="./test_app.py"
        )
    ]
)
print("上传文件结果:", upload)

# 测试替换CloudStudio配置
config = CloudStudioConfig(
    app=[CloudStudioConfigApp(
        cmd="python test_app.py",
        port=8080,
        name="test_app"
    )]
)
config_result = replaceCloudStudioConfig(
    api_token=api_token,
    space_key=new_space_key,  # 使用新创建的工作空间
    region=region,
    config=config
)
print("替换配置结果:", config_result)

# 测试重启工作空间
restart_result = restartWorkspace(
    api_token=api_token,
    space_key=new_space_key,  # 使用新创建的工作空间
    region=region
)
print("重启工作空间结果:", restart_result)

# 测试创建分享连接
share_link = create_share_link_handler(
    api_token=api_token,
    space_key=new_space_key,  # 使用新创建的工作空间
    region=region,
    port=8080
)
print("创建分享连接结果:", share_link)

# 构建完整的分享URL
share_url = f"{share_link.data.scheme}://{share_link.data.host}"
print("分享链接:", share_url)

# 测试 create_share_link_with_command 函数
# 注意：这个函数是在 server.py 中定义的，需要导入才能使用
# 这里只是示例代码，实际运行时需要取消注释并导入函数
'''
from src.mcp_deploy.server import create_share_link_with_command

# 测试创建分享连接并启动服务
share_link_with_command = create_share_link_with_command(
    space_key=new_space_key,  # 使用新创建的工作空间
    title="测试应用",
    port=8080,
    command="nohup python app.py > /dev/null 2>&1 &"
)
print("创建分享连接并启动服务结果:", share_link_with_command)
print("分享链接:", share_link_with_command["share_url"])
'''

# 测试 getAutoRunLog 函数
# 注意：这个函数需要在应用启动后调用才能获取日志
from src.mcp_deploy.mcp_handlers import getAutoRunLog

# 测试获取自动运行日志
auto_run_log = getAutoRunLog(
    api_token=api_token,
    space_key=new_space_key,  # 使用新创建的工作空间
    region=region,
    delay=3000,  # 等待3秒
    title="test_app"  # 应用名称，与CloudStudioConfigApp中的name一致
)
print("获取自动运行日志结果:", auto_run_log)
if auto_run_log.data and "test_app" in auto_run_log.data:
    print("应用日志:", auto_run_log.data["test_app"])

# 测试端口是否启动
executeRes = execute(
    api_token=api_token,
    space_key=new_space_key,  # 使用新创建的工作空间
    region=region,
    command="lsof -i:8080"
)
print("获取测试端口是否启动结果:", executeRes)