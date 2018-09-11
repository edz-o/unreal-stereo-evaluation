# Unrealstereo

## Getting Started

### Prerequisites

- Python 3


    ```
    $ pip install -r requirements.txt
    ```

### Installation

1. Clone the repository.

    ```
    $ git clone https://github.com/edz-o/minimum_evaluation.git
    ```
    We'll call the directory that you cloned UnrealStereo into `$ROOT`

### Config ELAS algorithm

1. We are using the implementation from [Middlebury website](http://vision.middlebury.edu/stereo/submit3/). 

    ```
    $ wget http://vision.middlebury.edu/stereo/submit3/zip/MiddEval3-SDK-1.6.zip
    $ unzip MiddEval3-SDK-1.6.zip
    $ cd MiddEval3
    ```

2. Compile Libelas as follows:

    ```
    $ cd alg-ELAS/build
    $ cmake ..
    $ make
    $ cd ../..
    ```

3. Compile the tools in code/ as follows:

    ```
    $ cd code/imageLib
    $ make
    $ cd ..
    $ make
    $ cd ..
    ```

4. Copy our python wrapper for the algorithm to `MiddEval3/alg-ELAS`.

    ```
    $ cd $ROOT
    $ cp run_ELAS.py MiddEval3/alg-ELAS
    ```

### Download unrealstereo data

Download the data we used as follows,

```
$ wget https://stereo.unrealcv.org/Data.zip (128.220.35.143:/home/yzhang/bin/unrealstereo-release/minimum/Data.zip)
$ unzip Data.zip
```

## Reproduce result

```shell
$ sh run.sh
```