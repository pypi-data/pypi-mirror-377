from setuptools import find_packages, setup

setup(name='CyVer',
      version='2.0.2',
      description='An open-source Python library to validate whether a Cypher query adheres to the schema and properties of a Neo4j graph, as well as checking for correct syntax.',
      long_description='An open-source Python library to validate whether a Cypher query adheres to the schema and properties \
      of a Neo4j graph, as well as checking for correct syntax. This library can be useful for evaluating large language models (LLMs),\
      as it allows the generated Cypher queries to be validated against the schema and properties defined in a Neo4j graph.',
      url='https://gitlab.com/netmode/CyVer',
      author=['Ioanna Mandilara','Christina Maria Androna'],
      author_email=['ioanna_mandilara@yahoo.gr','androna.xm@gmail.com'],
    #   license='GNU GPL',
      packages=find_packages(include=['CyVer','CyVer.validators']),
      install_requires=[
        'regex>=2024.11.6',
        'neo4j>=5.27',
        'pandas>=2.2.3'
      ],
      classifiers=[
        'Programming Language :: Python :: 3',
        'License ::  CC BY-SA 4.0 License',  # License type
        'Operating System :: OS Independent',
    ],
    #   test_suite='nose.collector',
    #   tests_require=['nose'],
    #   setup_requires=['pytest-runner'],
    #   tests_require=['pytest'],
    #   test_suite='tests',
      python_requires=">=3.10",
      include_package_data=True,
      zip_safe=False
      )
