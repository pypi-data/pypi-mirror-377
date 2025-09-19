from setuptools import setup ,find_packages
setup( 
    name="puzzle game",
    version= "0.1.0",
    description = "program using BFS ",
    long_description= open("README.md").read(),
    long_description_content_type = "text/markdown",
    author= "en.shaima",
    author_email= "shaimamanager3@example.com",
    packages=find_packages(),
    python_requires='>=3.13',
    license="MIT",

)