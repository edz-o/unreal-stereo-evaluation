# UnrealStereo

[UnrealStereo](https://stereo.unrealcv.org/) is a project for generating images from virtual worlds for stereo vision. It is based on [UnrealCV](http://unrealcv.github.io/) which is an open source software connecting Computer Vision to Unreal Engine.

This repository contains codes and data for reproducing the results in our paper.

## Getting Started

### Prerequisites

- Ubuntu
- Python 3


    ```shell
    pip install -r requirements.txt
    ```
- Csh (To run the ELAS algorithm)

    ```shell
    sudo apt-get install csh
    ```

### Installation

1. Clone the repository.

    ```shell
    git clone https://github.com/edz-o/minimum_evaluation.git
    ```
    We'll call the directory that you cloned UnrealStereo into `$ROOT`

### Config ELAS algorithm

1. We are using the implementation from [Middlebury website](http://vision.middlebury.edu/stereo/submit3/). 

    ```shell
    wget http://vision.middlebury.edu/stereo/submit3/zip/MiddEval3-SDK-1.6.zip
    unzip MiddEval3-SDK-1.6.zip
    cd MiddEval3
    ```

2. Compile Libelas as follows:

    ```shell
    cd alg-ELAS/build
    cmake ..
    make
    cd ../..
    ```

3. Compile the tools in code/ as follows:

    ```shell
    cd code/imageLib
    make
    cd ..
    make
    cd ..
    ```

4. Copy our python wrapper for the algorithm to `MiddEval3/alg-ELAS`.

    ```shell
    cd $ROOT
    cp run_ELAS.py MiddEval3/alg-ELAS
    ```

### Download unrealstereo data

Download the data we used as follows,

```shell
wget https://cs.jhu.edu/~yzh/unrealstereo_data_hazardous.zip 
unzip unrealstereo_data_hazardous.zip
```

### Reproduce the result

```shell
sh run_all.sh
```
## Annotation of hazardous regions on Middlebury and KITTI 2015

The annotations used in our paper can be downloaded [here](https://cs.jhu.edu/~yzh/kitti15_mb.zip).

## License and Citation

This project is licensed under the MIT License - see the LICENSE file for details.

If you find UnrealStereo useful in your research, please consider citing:
    
    @inproceedings{zhang2018unrealstereo,
      title={Unrealstereo: Controlling hazardous factors to analyze stereo vision},
      author={Zhang, Yi and Qiu, Weichao and Chen, Qi and Hu, Xiaolin and Yuille, Alan},
      booktitle={2018 International Conference on 3D Vision (3DV)},
      pages={228--237},
      year={2018},
      organization={IEEE}
    }
