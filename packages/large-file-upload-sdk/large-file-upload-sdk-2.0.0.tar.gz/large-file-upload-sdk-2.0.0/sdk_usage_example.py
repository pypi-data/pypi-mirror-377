"""
SDK使用示例 - 展示如何像图片中那样简单调用
"""
import file_upload_sdk as api

# 方式1: 使用全局API（最简单，类似图片中的调用方式）
def example_simple_usage():
    """简单用法示例"""
    
    # 初始化SDK（类似设置服务器地址）
    api.init_sdk("http://localhost:8000")
    
    # 直接上传文件（类似图片中的API调用）
    result = api.upload_file(
        file_path="/path/to/local/your_file.suffix",
        file_name="your_file.suffix"
    )
    
    if result['success']:
        print(f"上传成功！文件URL: {result['file_url']}")
    else:
        print(f"上传失败: {result['error']}")


# 方式2: 带进度回调的用法
def example_with_progress():
    """带进度显示的用法"""
    
    api.init_sdk("http://localhost:8000")
    
    def progress_callback(progress):
        print(f"\r上传进度: {progress:.1f}%", end="", flush=True)
    
    result = api.upload_file(
        file_path="/path/to/local/large_file.zip",
        file_name="uploaded_large_file.zip",
        progress_callback=progress_callback
    )
    
    print()  # 换行
    if result['success']:
        print(f"上传完成！文件URL: {result['file_url']}")
    else:
        print(f"上传失败: {result['error']}")


# 方式3: 面向对象的用法（更灵活）
def example_oop_usage():
    """面向对象用法示例"""
    
    # 创建SDK实例
    sdk = api.FileUploadSDK(
        base_url="http://localhost:8000",
        chunk_size=5 * 1024 * 1024,  # 5MB分片
        retry_times=5
    )
    
    # 上传文件
    result = sdk.upload_file(
        file_path="/path/to/local/your_file.suffix",
        file_name="your_file.suffix",
        enable_md5_check=True
    )
    
    if result['success']:
        print(f"文件ID: {result['file_id']}")
        print(f"文件URL: {result['file_url']}")
    else:
        print(f"上传失败: {result['error']}")


# 方式4: 类似图片中API的完整示例
def example_api_style():
    """模拟图片中API调用风格的示例"""
    
    # 初始化（相当于设置连接参数）
    server_url = "http://localhost:8000"
    api.init_sdk(server_url)
    
    # 设置用户和数据集信息（如果需要的话）
    owner_name = 'user'
    dataset_name = 'my-test-data'
    
    # 上传文件（核心调用，类似图片中的api.upload_file）
    result = api.upload_file(
        file_path='/path/to/local/your_file.suffix',
        file_name=f'{owner_name}/{dataset_name}/your_file.suffix',  # 可以包含路径
        progress_callback=lambda p: print(f"Progress: {p:.1f}%")
    )
    
    if result['success']:
        print(f"Upload successful!")
        print(f"File URL: {result['file_url']}")
        print(f"File ID: {result['file_id']}")
    else:
        print(f"Upload failed: {result['error']}")


# 方式5: 断点续传示例
def example_resume_upload():
    """断点续传示例"""
    
    api.init_sdk("http://localhost:8000")
    
    # 第一次上传（可能中断）
    file_id = "my_unique_file_id_123"
    
    result1 = api.upload_file(
        file_path="/path/to/large_file.zip",
        file_name="large_file.zip",
        custom_file_id=file_id  # 指定文件ID以支持断点续传
    )
    
    if not result1['success']:
        print(f"第一次上传失败: {result1['error']}")
        
        # 检查上传状态
        status = api.get_upload_status(file_id)
        if status['success']:
            print(f"已上传进度: {status['progress']:.1f}%")
            
            # 继续上传（从中断处继续）
            result2 = api.upload_file(
                file_path="/path/to/large_file.zip",
                file_name="large_file.zip",
                custom_file_id=file_id  # 使用相同的文件ID
            )
            
            if result2['success']:
                print("断点续传成功!")
            else:
                print(f"断点续传失败: {result2['error']}")


# 实际使用的简化版本（最接近图片中的调用方式）
def main():
    """主函数 - 展示最简单的用法"""
    
    # 初始化SDK
    api.init_sdk("http://localhost:8000")
    
    # 上传文件（就像图片中那样简单）
    result = api.upload_file(
        file_path="./test_file.txt",  # 本地文件路径
        file_name="uploaded_test_file.txt"  # 上传后的文件名
    )
    
    # 处理结果
    if result['success']:
        print("✅ 上传成功!")
        print(f"📁 文件名: {result['file_name']}")
        print(f"🔗 文件URL: {result['file_url']}")
        print(f"📊 文件大小: {result['file_size']} bytes")
    else:
        print("❌ 上传失败!")
        print(f"💥 错误信息: {result['error']}")


if __name__ == "__main__":
    # 创建一个测试文件
    with open("test_file.txt", "w") as f:
        f.write("Hello, this is a test file for upload SDK!\n" * 1000)
    
    # 运行示例
    main()
    
    # 清理测试文件
    import os
    if os.path.exists("test_file.txt"):
        os.remove("test_file.txt")
