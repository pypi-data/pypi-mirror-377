# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['arcp',
 'arcp.api',
 'arcp.core',
 'arcp.models',
 'arcp.services',
 'arcp.utils',
 'web']

package_data = \
{'': ['*'], 'web': ['static/css/*', 'static/js/*', 'templates/*']}

install_requires = \
['PyJWT>=2.10.1,<3.0.0',
 'deprecated>=1.2.0,<2.0.0',
 'fastapi>=0.115.0,<1.0.0',
 'importlib-metadata>=1.7.0,<7.0.0',
 'openai>=1.3.0,<2.0.0',
 'opentelemetry-api>=1.21.0,<2.0.0',
 'opentelemetry-exporter-jaeger-thrift>=1.21.0,<2.0.0',
 'opentelemetry-exporter-otlp-proto-grpc>=1.21.0,<2.0.0',
 'opentelemetry-instrumentation-fastapi>=0.42b0,<1.0.0',
 'opentelemetry-instrumentation-httpx>=0.42b0,<1.0.0',
 'opentelemetry-instrumentation-redis>=0.42b0,<1.0.0',
 'opentelemetry-instrumentation>=0.42b0,<1.0.0',
 'opentelemetry-sdk>=1.21.0,<2.0.0',
 'opentelemetry-semantic-conventions>=0.42b0,<1.0.0',
 'prometheus-client>=0.19.0,<1.0.0',
 'psutil>=7.0.0,<8.0.0',
 'pydantic>=2.5.0,<3.0.0',
 'python-dotenv>=1.0.0,<2.0.0',
 'redis>=5.0.1,<7.0.0',
 'thrift>=0.13.0,<1.0.0',
 'uvicorn[standard]>=0.24.0,<1.0.0',
 'websockets>=11.0.3,<16.0.0',
 'wrapt>=1.10.0,<2.0.0']

extras_require = \
{':extra == "dev" or extra == "all"': ['httpx>=0.25.2,<1.0.0']}

setup_kwargs = {
    'name': 'arcp-py',
    'version': '2.0.0',
    'description': 'ARCP (Agent Registry & Control Protocol) is a sophisticated agent orchestration protocol that provides centralized service discovery, registration, and control for distributed agent systems.',
    'long_description': '# ARCP - Agent Registry & Control Protocol\n\n[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](./LICENSE)\n[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Security](https://img.shields.io/badge/security+-brightgreen.svg)](#security)\n[![PyPI version](https://badge.fury.io/py/arcp-py.svg)](https://badge.fury.io/py/arcp-py)\n[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)\n\n**ARCP** (Agent Registry & Control Protocol) is a sophisticated agent orchestration protocol that provides centralized service discovery, registration, and control for distributed agent systems.\n\n## Documentation\n\nhttps://arcp.0x001.tech/docs\n\n## 📄 License\n\nThis project is licensed under the Apache License 2.0',
    'author': 'Muhannad',
    'author_email': '01muhannad.a@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/0x00K1/ARCP',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.11,<4.0',
}


setup(**setup_kwargs)
