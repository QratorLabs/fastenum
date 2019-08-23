import setuptools

with open('README.md', 'r', encoding='utf-8') as rfd:
    long_description = rfd.read()

setuptools.setup(
    name='FastEnum-Meta',
    version='1.2.1',
    license='MIT',
    platforms=['any'],
    author='Andrey Semenov',
    author_email='gatekeeper.mail@gmail.com',
    description='A fast pure-python implementation of Enum',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/SantjagoCorkez/fastenum',
    packages=['fastenum_meta'],
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Natural Language :: Russian',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
