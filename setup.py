from distutils.core import setup

setup(
    name="crone",
    version="1.0.1",
    author="Panu P",
    author_email="panuph@gmail.com",
    maintainer="Panu P",
    maintainer_email="panuph@gmail.com",
    url="https://github.com/panuph/crone",
    description="A little extension to cron",
    long_description="Like cron but you can further indicate the timezone, " + \
        "the period and interval to run a job (tested on python 2.6 but " + \
        "should be fine to run with older python releases).",
    download_url="https://github.com/panuph/crone/downloads",
    classifiers=["Programming Language :: Python", "Operating System :: POSIX"],
    platforms=["python"],
    license="Freeware",
    py_modules=["crone"]
)
