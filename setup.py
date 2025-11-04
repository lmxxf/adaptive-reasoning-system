from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="adaptive-reasoning-system",
    version="1.0.0",
    author="Research Team",
    author_email="research@example.com",
    description="大语言模型自适应推理系统",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lmxxf/adaptive-reasoning-system",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.2.0",
            "pytest-asyncio>=0.18.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
        ],
        "web": [
            "flask>=2.0.0",
            "fastapi>=0.68.0",
            "uvicorn>=0.15.0",
        ],
        "viz": [
            "matplotlib>=3.4.0",
            "seaborn>=0.11.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "adaptive-reasoning=adaptive_reasoning_system:main",
            "adaptive-demo=demo:main",
        ],
    },
    keywords="llm reasoning adaptive ai machine-learning nlp",
    project_urls={
        "Bug Reports": "https://github.com/lmxxf/adaptive-reasoning-system/issues",
        "Source": "https://github.com/lmxxf/adaptive-reasoning-system",
        "Documentation": "https://github.com/lmxxf/adaptive-reasoning-system/blob/main/README.md",
    },
)