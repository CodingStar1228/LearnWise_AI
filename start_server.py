#!/usr/bin/env python3
"""
启动服务器脚本，自定义输出信息
"""
import subprocess
import sys
import re

def main():
    print("\n" + "="*50)
    print("🚀 启动服务器...")
    print("="*50 + "\n")
    
    # 启动uvicorn
    process = subprocess.Popen(
        ["python", "-m", "uvicorn", "web.main:app", "--host", "0.0.0.0", "--port", "3003", "--workers", "1"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    # 实时输出并替换显示
    for line in process.stdout:
        # 替换 0.0.0.0 为 127.0.0.1
        if "0.0.0.0:3003" in line:
            line = line.replace("0.0.0.0:3003", "127.0.0.1:3003")
            # 在 Press CTRL+C 后面添加访问提示
            if "Press CTRL+C to quit" in line:
                line = line.replace(
                    "Press CTRL+C to quit",
                    "Press CTRL+C to quit\n\n" + 
                    "="*50 + "\n" +
                    "✅ 服务器已启动！\n" +
                    "📌 访问地址: http://127.0.0.1:3003\n" +
                    "📌 或访问: http://localhost:3003\n" +
                    "="*50
                )
        print(line, end='', flush=True)
    
    process.wait()
    return process.returncode

if __name__ == "__main__":
    sys.exit(main())
