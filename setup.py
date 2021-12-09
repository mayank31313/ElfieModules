import setuptools

long_description = '''''';

# with open("README.md", "r") as fh:
#     long_description = fh.read()

setuptools.setup(
     name='elfie_modules',
     version='1',
     author="Mayank Shinde",
     author_email="mayank31313@gmail.com",
     description="Extension Elfie Modules",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/mayank31313/ElfieModules",
     packages=setuptools.find_packages(),
     # packages=['elfie'],
     keywords=['elfie','rasa','conversional_bots', 'control_net'],
     classifiers=[
         "Programming Language :: Python :: 3",
         "Operating System :: OS Independent",
         'Intended Audience :: Developers',
     ]
 )