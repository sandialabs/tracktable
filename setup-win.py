import setuptools
from glob import glob

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tracktable",
    version="1.1.0",
    author="Andy Wilson",
    author_email="atwilso@sandia.gov",
    description="A tool for analyzing the paths of moving objects (tracks or trajectories)",
    include_package_data=True,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://www.sandia.gov",
    packages=setuptools.find_packages(),
    python_requires=">=3",  #may want to change
    license_files = ["LICENSE_boost"],
    classifiers=[
        "Programming Language :: Python :: 3.6", 
        "Operating System :: Windows :: x64",
        "Programming Language :: Python :: Implementation :: CPython"
    ],
    data_files=[
        ("lib\\site-packages\\tracktable\\analysis", ["tracktable\\analysis\\_dbscan_clustering.pyd", "tracktable\\analysis\\_rtree.pyd"]),
        ("lib\\site-packages\\tracktable\\core", ["tracktable\\core\\_core_types.pyd", "tracktable\\core\\_domain_algorithm_overloads.pyd", "tracktable\\core\\_tracktable_hello.pyd"]),
        ("lib\\site-packages\\tracktable\\domain", ["tracktable\\domain\\_cartesian2d.pyd", "tracktable\\domain\\_cartesian3d.pyd", "tracktable\\domain\\_feature_vector_points.pyd", "tracktable\\domain\\_terrestrial.pyd"]),
        ("lib", glob("lib/*.dll")),
        ("lib", ["bin\\TracktableCore.dll","bin\\TracktableDomain.dll"])]
)
