from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="jimeng-mcp-apicore",
    version="1.0.0",
    author="Ceeon",
    author_email="your-email@example.com",  # 替换为您的邮箱
    description="即梦AI MCP服务器 - 基于APICore平台调用doubao-seedream-4.0模型",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ceeon/jimeng-mcp-apicore",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Graphics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastmcp>=0.1.0",
        "httpx>=0.24.0",
        "Pillow>=10.0.0",
    ],
    entry_points={
        'console_scripts': [
            'jimeng-mcp-apicore=jimeng_mcp:main',
        ],
    },
    keywords="mcp jimeng ai image-generation apicore doubao seedream",
    project_urls={
        "Bug Reports": "https://github.com/Ceeon/jimeng-mcp-apicore/issues",
        "Source": "https://github.com/Ceeon/jimeng-mcp-apicore",
    },
)