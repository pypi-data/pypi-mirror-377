from setuptools import setup, find_packages

setup(
    name='hafoo_order_sdk',
    version='0.0.1',
    packages=find_packages(),
    description='A simple example package',
    long_description=open('README.md').read(),
    # python3，readme文件中文报错
    # long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='http://github.com/KuBoy/hafoo_order_sdk',
    author='KuBoy',
    author_email='1757378111@qq.com',
    license='MIT',
    install_requires=[
        "requests>=2.25.1",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
