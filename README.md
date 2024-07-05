# DataLabelTool

Development environment: 
* Windows 11
* Python 3.11.6
* Nvidia RTX4090

This is a basic 2D image labeling tool for teeth segmentation for the 3DII CAD team. It is implemented using [Qt](https://doc.qt.io/qtforpython-6/).

Move to the project directory, where the **./src** directory resides. Then create **segment-anything-checkpoint** directory and move there.
> mkdir segment-anything-checkpoint

> cd segment-anything-checkpoint

Then download the default model checkpoint, [ViT-H SAM model](https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth), into this directory.
Check [Segment Anything](https://github.com/KyunHwan/segment-anything/tree/main) for more details.

Once the model has been saved as described above, move back to the **root** of the project directory, where the **./src** directory is.
> cd ..

Install the packages that are required to use this tool that depends on Pyside (Qt for Python), Pytorch (CUDA-enabled version), opencv, and (optionally) ONNX.
> pip install -r requirements.txt

> [!Important]
> Check that the versions of the installed packages are appropriate.
> Some requirements are in [Segment Anything](https://github.com/KyunHwan/segment-anything/tree/main).

Run main.py
> python main.py