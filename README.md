# DataLabelTool
This is a basic 2D image labeling tool for teeth segmentation for the 3DII CAD team. It is implemented using [Qt](https://doc.qt.io/qtforpython-6/) and [Segment Anything](https://github.com/KyunHwan/segment-anything/tree/main).

Development environment: 
* Windows 11
* Python 3.11.6
* Nvidia RTX4090

Clone this directory
> git clone --recursive https://github.com/KyunHwan/DataLabelTool.git

Check the current Python version you are using before proceeding.
> Python --version

> Python 3.11.6

Create a virtual environment and activate it.
> [!Warning]
> If possible, use Python version 3.11.6 to create the virtual environment.
> Other Python versions may not work as expected.

> python -m venv env 

> cd env/Scripts

> activate

> cd ../..

Install the packages that are required to use this tool that depends on Pyside (Qt for Python), Pytorch (CUDA-enabled version), opencv, and (optionally) ONNX.
> pip install -r requirements.txt

> [!Important]
> Check that the versions of the installed packages are appropriate.
> Some requirements are in [Segment Anything](https://github.com/KyunHwan/segment-anything/tree/main).

Run main.py inside the project's root directory.
> python main.py