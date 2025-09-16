from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="agent-response-transformer",
    version="0.1.0",
    author="yi.zhou",
    author_email="yi.zhou@netmind.ai",
    description="A Python SDK to transform Claude response to OpenAI response format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/protagolabs/agent-response-transformer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "openai",
        "agents"
    ],
)
