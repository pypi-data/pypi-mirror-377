from setuptools import setup, find_packages

setup(
    name="leet-stats",           
    version="1.0.0",
    description="See your Leetcode stats and compare with your friends",
    author="Luigi Schmitt",
    author_email="schmittluigi@gmail.com",
    url="https://github.com/luigischmitt/leet-stats",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "leet-stats = leet_stats.__main__:main"
        ]
    },
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="leetcode stats cli programming competition",
)
