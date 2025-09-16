from setuptools import setup, find_packages

setup(
    name='sort-algorithms-pack',      # Package name used in import
    version='0.3',
    packages=find_packages(),
    description= """
My sorting package includes two sorting algorithms:

1. Merge Sort: Contains a class named `MergeSort` with a method `mergeSort` that takes a list, a starting index, and an ending index as inputs.

2. Quick Sort: Contains a class named `QuickSort` with a method `quickSort`, which accepts the same parameters as `mergeSort`.

Note: Do not directly access the internal methods `__swap`, `__partition`, or `__Merge`.
""",
    author='Arpit Kumar',
    author_email='arpitkumar172004@gmail.com',
)
