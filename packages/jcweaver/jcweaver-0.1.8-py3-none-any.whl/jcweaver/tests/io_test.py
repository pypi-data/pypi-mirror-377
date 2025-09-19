from jcweaver.api.api import input_prepare, output_prepare
from jcweaver.api.decorators import lifecycle
from jcweaver.core.const import DataType, Platform


@lifecycle(platform=Platform.MODELARTS)
def my_io():
    dataset = input_prepare(DataType.DATASET, "bootfile.py")
    print("dataset path: ", dataset.path)
    output = output_prepare(DataType.DATASET, "output.pt")
    print("output file path: ", output.path)


def test_io():
    my_io()
