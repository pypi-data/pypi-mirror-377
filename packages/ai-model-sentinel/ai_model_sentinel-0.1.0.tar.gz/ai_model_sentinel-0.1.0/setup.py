from setuptools import setup, find_packages
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="ai-model-sentinel",
    version="0.1.0",
    author="Saleh Asaad Abughabraa",
    author_email="saleh.abughabraa@example.com",
    description="Comprehensive AI Model Monitoring and Drift Detection Toolkit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SalehAsaadAbughabraa/ai-model-sentinel",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
   "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    test_suite="tests",
    tests_require=[
        "pytest==7.4.0",
        "pytest-cov==4.1.0",
        "pytest-flask==1.2.0"
    ],
    entry_points={
        "console_scripts": [
            "ai-sentinel=ai_model_sentinel.cli:main",
            "ai-model-monitor=ai_model_sentinel.monitor:start_monitoring",
        ],
    },
    include_package_data=True,
    keywords=[
        "ai",
        "machine-learning",
        "monitoring",
        "drift-detection",
        "mlops",
        "model-management"
    ],
    project_urls={
        "Documentation": "https://github.com/SalehAsaadAbughabraa/ai-model-sentinel#readme",
        "Source": "https://github.com/SalehAsaadAbughabraa/ai-model-sentinel",
        "Tracker": "https://github.com/SalehAsaadAbughabraa/ai-model-sentinel/issues",
    },
    license="MIT",
    platforms=["any"],
)