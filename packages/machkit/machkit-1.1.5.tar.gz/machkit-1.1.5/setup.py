from setuptools import find_packages, setup


def load_requirements(filename):
    with open(filename) as fd:
        return fd.readlines()


requirements = load_requirements("requirements.txt")
test_requirements = load_requirements("requirements-dev.txt")


setup(
    name="machkit",
    description="mach team kit wrapper library",
    version="1.1.5",
    author="machkit",
    author_email="zhangtao03@megvii.com",
    url="https://git-core.megvii-inc.com/transformer/yueying/data-service-sdk",
    packages=find_packages(exclude=("tests")),
    classifiers=[
        "License :: Other/Proprietary License",
    ],
    tests_require=test_requirements,
    install_requires=requirements,
    python_requires=">=3.5",
)
