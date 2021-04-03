import setuptools

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name='mwenclubhouse-bot',
    install_requires=requirements,
    author="Matthew Wen",
    author_email="mattwen2018@gmail.com",
    scripts=["bin/mwenclubhouse-discord"],
    packages=setuptools.find_packages(),
    version='1.0.0',
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ]
)
