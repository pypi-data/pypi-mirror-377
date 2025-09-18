BOLIB-3 
==================================================
***Bilevel Optimisation Library***

<!-- TOC -->
* [BOLIB-3](#bolib-3-)
  * [Bilevel optimisation](#bilevel-optimisation)
  * [Installation](#installation)
  * [Contributing](#contributing)
  * [Unit tests](#unit-tests)
  * [Authors](#authors)
<!-- TOC -->


## Bilevel optimisation
The bilevel program is defined as an upper-level program with a second lower-level program embedded in its constraints.
It is written as follows:
<pre>
minimise_{x,y} F(x,y);  
subject to     G(x,y)>=0;  
               H(x,y)==0;  
               y ∈ argmin_{y}{ f(x,y):
                             { g(x,y)>=0;  
                             { h(x,y)=0.
</pre>

The choice between representing inequality constraints as non-negative (>=0) or non-positive (<=0) remains inconsistent throughout the literature.
In this library we follow the non-negative (>=0) formulation.
The notation defined in the table below is consistent thought the library:

| Symbol | Level       | Represent                       | Dimension |
|--------|-------------|---------------------------------|-----------|
| x      | Upper-level | Decision variables              | n_x       |
| y      | Lower-level | Decision variables              | n_x       |
| F(x,y) | Upper-level | Objective function              | 1         |
| f(x,y) | Lower-level | Objective function              | 1         |
| G(x,y) | Upper-level | Inequality constraint functions | m_G       |
| g(x,y) | Lower-level | Inequality constraint functions | m_g       |
| H(x,y) | Upper-level | Equality constraint functions   | m_H       |
| h(x,y) | Lower-level | Equality constraint functions   | m_h       |


## Requirements
Depending on your usage, you may require:
* A LaTeX and BibTeX compiler ([miktex.org](https://miktex.org/))
* Python 3 ([python.org](https://www.python.org/downloads/)) (`pip install -r requirements.txt`)
* GAMS ([gams.com](https://www.gams.com/))
* MATLAB ([matlab.mathworks.com](https://matlab.mathworks.com/))



## Contributing
This is a community project to gather an extensive collection of bilevel programs for robust benchmarking.
Please do contribute! There are a few things to note.
You will need to request collaborator access from s.ward@soton.ac.uk. 
Please follow the standard file layouts found in the template folder.
1. Clone the repository (`git clone https://github.com/bolib3/bolib3`)
2. Create a personal branch (`git checkout -b BranchName`)
3. Commit your Changes (`git commit -m 'comment'`)
4. Push to the Branch (`git push origin BranchName`)
5. Open a Pull Request

ALL file and directory names are to be lowercase!!





## Unit tests
The unit tests check that the library is set up correctly. From the top level directory run:

```sh
python -m unittest "automation\unit_tests\python_unit_tests.py"
```

```sh
matlab -r "run('automation\unit_tests\matlab_test_suite.m')"
```

1. __Test 001__:
Check that the file structure is consistent.
For example the folder 'latex' should only contain '.tex' files.
2. __Test 002__:
Checks that each bilevel program has a complete set of non-empty files.
For example every instance 'example' must have a corresponding 'example.json' and 'example.pdf' file.
3. __Test 003__:
Checks that each python module (respectively matlab class) representing a bilevel program
implements all the necessary properties (e.g. 'name', 'category') and methods (e.g. F, G, ...).
4. __Test 004__:
Checks that the JSON metadata files are consistent.
They should fulfill the schema file and the properties should match the properties in the python/matlab files.
5. __Test 005__:
Some bilevel programs have a list of datasets.
This tests that there exists a file for each of them within /bolib3/data/.
6. __Test 006__:
Checks the functions F,G,H,f,g,h return arrays of the correct dimension.
7. __Test 007__:
Checks the solutions recorded in the JSON metadata are feasible.

## Authors
| Name          | Email                                                     |
|---------------|-----------------------------------------------------------|
| Samuel Ward   | [s.ward@soton.ac.uk](mailto:test\s.ward@soton.ac.uk)      |
| Yaru Qian     | [y.qian@soton.ac.uk](mailto:test\y.qian@soton.ac.uk)      |
| Jordan Fisher | [jdjfisher@outlook.com](mailto:jdjfisher@outlook.com)     |
| Alain Zemkoho | [a.b.zemkoho@soton.ac.uk](mailto:a.b.zemkoho@soton.ac.uk) |
