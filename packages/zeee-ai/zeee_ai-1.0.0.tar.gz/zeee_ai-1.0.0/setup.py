from setuptools import setup, find_packages

setup(
    name="zeee-ai",
    version="1.0.0",
    author="Muhammad Aziz ur Rehman",
    author_email="azizhoreaofficial@gmail.com",
    description="ZeeE AI: Zero Effort, Everything Enabled AI Assistant (CLI)",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/AzizHorea/zeee-ai",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "prompt_toolkit>=3.0.39",
        "ollama>=0.1.0"
    ],
    entry_points={
        'console_scripts': [
            'zeee-ai = zeee_ai.cli:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
    ],
    python_requires='>=3.7',
)
 
