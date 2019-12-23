# physics

a box2d playpen

## Installation

* clone the repository
* The `Box2D` has a dependency `swig`.
   - Install it on Ubuntu by running 
    ```sudo apt install swig```
   - On Fedora systems, run 
    ```sudo dnf install swig```
* Clone the `pybox2d` repository and build it and install it. See [Installling PyBox](#installing-pybox2d)
* Install the activity in the normal procedure.

### Installing PyBox2D
You may follow any of the option
#### A : Use the automated bash script
* Just run
```
./install-pybox2d
```
### B : Manual PyBox2d Installation
* Run the following commands
```
git clone https://github.com/pybox2d/pybox2d
cd pybox2d
# Make sure you have installed swig
./setup.py build
pip3 install .
```
> NOTE: There is PYPI package for PyBox2d. However, somethings not working at the moment.
> If you find it working, consider opening an Issue to replace the BUILD instructions.

## master branch

* does include library `box2d` as source and binaries,

* does include library `elements`.

## dfsg branch

* does not include library `box2d`, please install Debian package `python-box2d`, or Fedora package `pybox2d`,

* does include library `elements`,

* is regularly rebased on `master` branch.
