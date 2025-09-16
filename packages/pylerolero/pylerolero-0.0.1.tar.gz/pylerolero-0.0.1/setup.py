from setuptools import setup

with open("README.md", "r") as arq:
    readme = arq.read()

setup(name='pylerolero',
    version='0.0.1',
    license='MIT License',
    author='João Marcos Campagnolo',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='jota.campagnolo@gmail.com',
    project_urls={
        "Bug Tracker": "https://github.com/JotaCampagnolo/pylerolero/issues",
        "Source Code": "https://github.com/JotaCampagnolo/pylerolero",
    },
    keywords='fake lero frase texto',
    description=u'Gerador de lero-lero em formato de frases e textos.',
    packages=['pylerolero'],
    install_requires=[],
    python_requires=">=3.10",)