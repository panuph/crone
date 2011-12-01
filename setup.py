from distutils.core import setup

setup(
    name="crone",
    version="1.0.3",
    author="Panu P",
    author_email="panuph@gmail.com",
    maintainer="Panu P",
    maintainer_email="panuph@gmail.com",
    url="https://github.com/panuph/crone",
    description="a little extension to cron with timezone support",
    long_description=open("README").read(),
    download_url="https://github.com/panuph/crone/downloads",
    classifiers=["Programming Language :: Python", "Operating System :: POSIX"],
    platforms=["python"],
    license="Freeware",
    py_modules=["crone"]
)
