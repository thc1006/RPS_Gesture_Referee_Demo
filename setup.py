from setuptools import setup, find_packages

setup(
    name="rps-gesture-referee",
    version="1.0.0",
    description="Rock-Paper-Scissors Gesture Referee System using MediaPipe",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "mediapipe==0.10.21",
        "opencv-python==4.11.0.86",
        "numpy==1.26.4",
        "opencv-contrib-python==4.11.0.86",
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.0",
        ]
    },
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "rps-referee=main:main",
        ],
    },
)
