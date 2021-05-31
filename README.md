This repository contains the implementation of the `Convolutional Shapelet Transform (CST)`, a state-of-the-art shapelet algorithm.
It compute a set of convolutional shapelets that match small parts of the input space with highly discriminative points in multiple convolutional spaces.

## Installation

The package support Python 3.7 & 3.8. To install the package and run the example you must :

0. If you are making a new installation, first install python, pip and setuptools.
1. Clone the repository https://github.com/baraline/CST.git
3. run `python3 setup.py install`

This will install the package and automaticaly look for the dependencies using `pip`. We recommend doing this in a new virtual environment using anaconda to avoid any conflict with an existing installation.
We do not yet support installation via `pip` in the initial release. If you wish to install dependencies individually, you can the strict dependencies used in the `requierements.txt` file.

An optional dependency that can help speed up numba, which is used in our implementation is the Intel vector math library (SVML). When using conda it can be installed by running `conda install -c numba icc_rt`

## Tutorial
We give here a minimal example to run the `CST` algorithm on any univariate dataset of the UCR archive:

```python
import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import RidgeClassifierCV
from sklearn.metrics import accuracy_score
from CST.shapelet_transforms.convolutional_ST import ConvolutionalShapeletTransformer
from CST.utils.dataset_utils import load_sktime_dataset_split

# Load Dataset by name. Any name of the univariate UCR archive can work.
X_train, X_test, y_train, y_test, _ = load_sktime_dataset_split(
    'GunPoint', normalize=True)

# First run will be slow due to numba compilations on the first call. Run small dataset like GunPoint the first time !
# Put verbose = 1 to see the progression of the algorithm.

cst = make_pipeline(
    ConvolutionalShapeletTransformer(verbose=0),
    RidgeClassifierCV(alphas=np.logspace(-6, 6, 20),
                      normalize=True, class_weight='balanced')
)

cst.fit(X_train, y_train)
pred = cst.predict(X_test)

print("Accuracy Score for CST : {}".format(accuracy_score(y_test, pred)))
```

We use the standard scikit-learn interface and expect as input a 3D matrix of shape `(n_samples, n_features, n_timestamps)`, altought we didn't yet extended the approach to the multivariate context, one can use the `id_ft` parameter of CST to change on which feature the algorithm is computing the transform.

In the `Example` folder, you can find some other scripts/notebooks to help you get started and show you how to plot some results. Additional experiments mentioned in the paper are also found in this folder.

## Reproducing the paper results

Multiple scripts are available under the `PaperScripts` folder. It contains the exact same scripts used to generate our results.

To obtain the same resampling data as the UCR archive, you muse use the [tsml](https://github.com/uea-machine-learning/tsml/blob/master/src/main/java/examples/DataHandling.java) java repository, then from the class `DataHandling` in the package examples, use the function `resamplingData` and change where to read and write the data from. The function assumes the input is in arff format, they can be obtained on the [time serie classification website](http://www.timeseriesclassification.com/)

## Contributing, Citing and Contact

If you are experiencing bugs in the CST implementation, or would like to contribute in any way, please create an issue or pull request in this repository
For other question or to take contact with me, you can email me at XXXX (institutional email might change soon so i provide this as a temporary address)

If you use our algorithm or publication in any work, please cite the following paper :
```bibtex
@article{CST,
  title={Convolutional Shapelet Transform: A new approach for time series shapelets},
  author={Guillaume Antoine, Vrain Christel, Elloumi Wael},
  journal={},
  volume={},
  number={},
  pages={},
  year={2021}
  publisher={}
}
```
## License
[GPL-3.0](https://www.gnu.org/licenses/gpl-3.0.en.html)

## Citations
Here are the code-related citations that were not made in the paper

[1]: [Loning, Markus and Bagnall, Anthony and Ganesh, Sajaysurya and Kazakov, Viktor and Lines, Jason and Kiraly, Franz J, "sktime: A Unified Interface for Machine Learning with Time Series", Workshop on Systems for ML at NeurIPS 2019}](https://www.sktime.org/en/latest/)


[2]: [The Scikit-learn development team, "Scikit-learn: Machine Learning in Python", Journal of Machine Learning Research 2011](https://scikit-learn.org/stable/)


[3]: [The Numpy development team, "Array programming with NumPy", Nature 2020](https://numpy.org/)

