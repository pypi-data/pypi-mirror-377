from setuptools import setup, find_packages

setup(
    name="lolgram-inapp-bot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["requests>=2.25.1"],
    author="Your Name",  # Replace with your name
    author_email="your.email@example.com",  # Replace with your email
    description="A Python library for creating and managing in-apps in Lolgram",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/lolgram-inapp-bot",  # Replace with your repo
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)