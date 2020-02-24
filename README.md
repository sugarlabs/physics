# physics

a box2d playpen

## Installation

* clone the repository
* The `Box2D` has a dependency `swig`.
   - Install it on Ubuntu/Debian by running 
    ```sudo apt install swig```
   - On Fedora/RHEL systems, run 
    ```sudo dnf install swig```
* To install python packages, you will need python and dependencies
   - Install it on Ubuntu/Debian by running
   ```sudo apt install python3 python3-setuptools python3-pip python3-all-dev ```
   - Install it on Fedora/RHEL by running
   ```sudo dnf install python3-pip python3-setuptools```
* Clone the `pybox2d` repository and build it and install it. See [Installling PyBox](#installing-pybox2d)
* Install the activity in the normal procedure.

### Installing PyBox2D

* Run the following commands
```
git clone https://github.com/pybox2d/pybox2d
cd pybox2d
# Make sure you have installed swig
python3 setup.py build
pip3 install . --system

```
> * NOTE: There is PYPI package for PyBox2d. However, somethings not working at the moment.
> If you find it working, consider opening an Issue to replace the BUILD instructions.
> * `--system` may be replaced by `--user` too. 

## master branch

* does include library `elements`.

## dfsg branch

* does not include library `box2d`, please install Debian package `python-box2d`, or Fedora package `Box2D`,

* does include library `elements`,

* is regularly rebased on `master` branch.
