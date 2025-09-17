from setuptools import setup, find_packages

setup(
    name='warlock_waker',
    version='0.2.1',
    packages=find_packages(),
    install_requires=[
        # 你的包的依赖列表
    ],
    author='zqyu14',
    author_email='zqyu14@iflytek.com',
    description='a log structure obj',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com',
    classifiers=[
        # 包的分类和许可证等信息
    ],
)