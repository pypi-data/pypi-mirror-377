from setuptools import setup, find_packages


with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="active_request",
    version="2025.9.152128",
    author="Eugene Evstafev",
    author_email="chigwel@gmail.com",
    description="Sliding-window active request counter (last 60s) using Redis for FastAPI or any Python app.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chigwell/active_request",
    packages=find_packages(),
    install_requires=[
        "redis>=5.0.0",
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    license="MIT",
    tests_require=["unittest"],
    test_suite="test",
)
