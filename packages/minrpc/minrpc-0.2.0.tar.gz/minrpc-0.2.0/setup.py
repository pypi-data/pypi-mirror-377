from setuptools import setup

meta = {}
with open('src/minrpc/__init__.py', 'rb') as f:
    exec(f.read(), meta, meta)

setup(
    name='minrpc',
    version=meta['__version__'],
    package_dir={'': 'src'},
)
