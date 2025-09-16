# Plant phenotyping based on segmentation model

## Purpose and background
**Purpose**: Segment images and extract traits from segmentation masks for root and shoot images collected from various platforms (cylinder, clearpot, black canvas) with different species (Arabidopsis, rice, soybean, sorghum, maize, pennycress).

**Background**: To be updated

## Installation

You can install by two methods:

1. **Clone the repository and navigate to the cloned directory**:  
   Clone the repository to the local drive.
   ```
   git clone https://github.com/Salk-Harnessing-Plants-Initiative/phenotyping-segmentation.git
   cd phenotyping-segmentation
   ```

2. **Install a PyPI package**:  
   
   ```
   pip install phenotyping-segmentation
   ```

## Organize the pipeline and your images
Models can be downloaded from [Box](https://salkinstitute.box.com/s/cqgv1dwm1hkf84eid72hdjqg47nwbpo5).

Please make sure to organize the downloaded pipeline, model, and your own images in the following architecture:

```
phenotyping-segmentation/
├── images/
│   ├── wave name (e.g., wave1)/
│   │   ├── day name (e.g., day7)/
│   │   │   ├── plant name (e.g., ZHOKUWVOIZ)/
│   │   │   │   ├── frame image (e.g., 1.png)
├── scans.csv (the image path and scanner id information)
├── model name (e.g., arabidopsis_model.pth)
├── label_class_dict_lr.csv (class color)
├── params.json (pipeline parameter json file)
├── env.yaml (environment file)
├── Dockerfile
├── pipeline.sh (indicate input_dir and pipeline name)
```

## Running the pipeline with a shell file (pipeline.sh)
1. **create the environment**:
   In terminal, navigate to your root folder and type:
   ```
   conda env create -f env.yaml
   ```
   or
   ```
   mamba env create -f env.yaml
   ```

2. **activate the environment**:
   ```
   conda activate phenotyping-segmentation
   ```

3. **run the shell file**:
   ```
   sed -i 's/\r$//' pipeline.sh
   bash pipeline.sh
   ```

## Running the pipeline with a pip installed
1. **activate your environment**:
   ```
   conda activate your-environment-name
   ```

2. **install the pip package**:
   ```
   pip install phenotyping-segmentation
   ```
   
3. **run the shell file**:
   ```
   sed -i 's/\r$//' pipeline.sh
   bash pipeline.sh
   ```

## Running the pipeline with docker
Make sure you have `images`, and associated files listed above in your root folder.

1. **build the docker**:
   ```
   docker build -t phenoseg .
   ```

2. **run the docker**:
   ```
   docker run --gpus all phenoseg
   ```
