from setuptools import setup, find_packages

setup(
    name="systemctl-manager",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "PySide6>=6.5.0",
    ],
    entry_points={
        "gui_scripts": [
            "systemctl-manager=src.main:main",
        ],
    },
    author="Zyad",
    author_email="zyad8594@gmail.com",  # Placeholder
    description="A professional and comprehensive GUI suite for managing systemd units and services.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/zyad/systemctl-manager",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Topic :: System :: Systems Administration",
        "Intended Audience :: System Administrators",
    ],
    python_requires=">=3.8",
)