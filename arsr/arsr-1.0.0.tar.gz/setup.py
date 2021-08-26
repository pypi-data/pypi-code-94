from setuptools import setup, find_packages

setup(
name='arsr', # 패키지 명

version='1.0.0',

description='Arbitrary Scale Super resolution',

author='epsilon',

author_email='kokomong1316@gmail.com',

url='https://github.com/epsilon-deltta/arbitrary-sr/',

license='MIT', # MIT에서 정한 표준 라이센스 따른다

py_modules=[''], # 패키지에 포함되는 모듈

python_requires='>=3',

install_requires=[], # 패키지 사용을 위해 필요한 추가 설치 패키지

# packages=['arsr'] # 패키지가 들어있는 폴더들
packages=find_packages(exclude=['tests']),

long_description=open('README.md').read(),

)