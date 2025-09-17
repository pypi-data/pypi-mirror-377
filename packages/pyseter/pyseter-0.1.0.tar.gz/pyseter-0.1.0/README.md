# Pyseter

A Python package that sorts images by an automatically generated ID before photo-identification. 

## Installation

### New to Python?

While most biologists use R, we chose to release Pyseter as a Python package because it relies heavily on Pytorch, a deep learning library. If you're new to Python, please follow these steps to getting started with Python and conda. 

#### Step 1: Install conda 

Conda is an important tool for managing packages in Python. Unlike Python, R (for the most part) handles packages for you behind the scenes. Python requires a more hands on approach.

   - Download and install [Miniforge](https://conda-forge.org/download/) (a form of conda)

After installing, you can verify your installation by opening the **command line interface** (CLI), which will depend on your operating system. Are you on Windows? Open the "miniforge prompt" in your start menu. Are you on Mac? Open the Terminal application. Then, type the following command into the CLI and hit return. 

```bash
conda --version
```

You should see something like `conda 25.5.1`. Of course, Anaconda, miniconda, mamba, or any other form of conda will work too.

#### Step 2: Create a new environment

Then, you'll create an environment for the package will live in. Environments are walled off areas where we can install packages. This allows you to have multiple versions of the same package installed on your machine, which can help prevent conflicts. 

Enter the following two commands into the CLI:

``` bash
conda create -n pyseter_env
conda activate pyseter_env
```

Here, I name (hence the `-n`) the environment `pyseter_env`, but you can call it anything you like!

Now your environment is ready to go! Try installing your first package, pip. Pip is another way of installing Python packages, and will be helpful for installing PyTorch and pyseter (see below). To do so, enter the following command into the CLI.

``` bash
conda install pip -y
```

#### Step 3: Install Pytorch

Installing PyTorch will allow users to extract features from images, i.e., identify individuals in images. This will be fast for users with an NVIDIA GPU or 16 GB Mac with Apple Silicon. **For all other users, extracting features from images will be extremely slow.** 

PyTorch installation can be a little finicky. I recommend following [these instructions](https://pytorch.org/get-started/locally/). Below is an example for Windows users. If you haven't already, activate your environment before installing.

``` bash
conda activate pyseter_env
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
```
PyTorch is pretty big (over a gigabyte), so this may take a few minutes.

#### Step 4: Install pyseter

Now, install pyseter. If you haven't already, activate your environment before installing.

``` bash
conda activate pyseter_env
pip3 install pyseter
```

Now you're ready to go! You can verify your pyseter installation by opening Python in the CLI (assuming your environment is still activated).


``` bash
python
```

Then, run the following Python commands.

``` python
import pyseter
pyseter.verify_pytorch()
quit()
```

If successful, you should see a message like this. 

```
✓ PyTorch 2.7.0 detected
✓ Apple Silicon (MPS) GPU available
```


## Step 5: AnyDorsal weights

Pyseter relies on the [AnyDorsal algorithm](https://besjournals.onlinelibrary.wiley.com/doi/full/10.1111/2041-210X.14167) to extract features from images. Please download the weights and place them anywhere you like. You'll reference the file location later when using the `FeatureExtractor`. 


## Jupyter

There are several different ways to interact with Python. The most common way for data analysts is through a *Jupyter Notebook*, which is similar to an RMarkdown document or a Quarto document. 

Just to make things confusing, there are several ways to open Jupyter Notebooks. Personally, I think the easiest way is through [VS Code](https://code.visualstudio.com/download). VS Code is an IDE (like R Studio) for editing code of all languages, and has great support for [Jupyter notebooks](https://code.visualstudio.com/docs/datascience/jupyter-notebooks). Alternatively, [Positron](https://positron.posit.co) is a VS-Code-based editor developed by the R Studio team.

Alternatively, you can try [Jupyter Lab](https://docs.jupyter.org/en/latest/). To do so, [install Jupyter](https://jupyter.org/install) via the command line (see below). I also recommend installing the [ipykernel](https://ipython.readthedocs.io/en/stable/install/kernel_install.html#kernels-for-different-environments), which helps you select the right conda environment in Jupyter Lab.

``` bash
conda activate pyseter_env
conda install jupyter ipykernel -y
python -m ipykernel install --user --name pyseter --display-name "Python (pyseter)"
```

Note that you only need to activate `pyseter_env` when you open a new command line (i.e., terminal or miniforge prompt). Then you can open Jupyter Lab with the following command:

``` bash
jupyter lab
```

## Getting Started

To get started with pyseter, please check out the "General Overview" [notebook](https://github.com/philpatton/pyseter/blob/main/examples/general-overview.ipynb) in the examples folder of this repository! 
