from setuptools import setup,find_packages


setup(name="BilliardsDistinguish",
      version="0.0.1",
      description="Distinguish different billiards images",
      author="tran-wang",
      author_email="doublechuan.wang@gmail.com",
      packages=find_packages(),
      install_requires=["PIL"],
      tests_require = ["nose>=1.3"],
      test_suite="nose.collector"
      )