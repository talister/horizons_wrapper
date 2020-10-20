# horizons_wrapper
Simple wrapper routine for querying JPL HORIZONS

## Installation instructions

### Linux/Unix

:If you want to look at and (potentially) modify the code, the method below will give you a local checkout, creates a virtualenv and install it (assumes some version of Python3 installed):
1. `python3 -m venv ~/horwrap_venv`
2. `source ~/horwrap_venv/bin/activate`
3. `git clone https://github.com/talister/horizons_wrapper`
4. `cd horizons_wrapper`
5. `pip install -r requirements.txt`
6. `python setup.py install`

To install it in one step, you can just do: `pip install git+https://github.com/talister/horizons_wrapper`

### Windows

This will setup a Virtual Environment, activate it and then install the code. You will need to `activate` the Virtualenv again if you restart the computer or quit the Git Bash shell.

0. Get and install Python3 if you don't have it already (https://www.python.org/downloads/)
1. Launch Git Bash (https://git-scm.com/downloads)
2. `virtualenv ~/horwrap_venv`
3. `source ~/horwrap_venv/Scripts/activate`
4. `pip install git+https://github.com/talister/horizons_wrapper`

### Mac

Not sure I'm afraid as I don't have one; Linux/Unix instructions should hopefully work

## Usage

An example use is shown below to calculate an ephemeris for 2020 SO for 3 days with custom quantities

```python
In [1]: from horizons_wrapper.ephem_subs import horizons_ephem

In [2]: from datetime import datetime

In [3]: start =  datetime(2020,10,19)

In [4]: end = datetime(2020,10,22)

In [5]: site_code = '-1'

In [6]: table = horizons_ephem('2020 SO', start, end, site_code, quantities='6,18')

In [7]: print(table)

Out[7]: 
<Table masked=True length=73>
targetname    datetime_str      datetime_jd       H    ...       RA_rate              DEC_rate             datetime           mean_rate     
   ---            ---                d           mag   ...     arcsec / min         arcsec / min                             arcsec / min   
   str9          str17            float64      float64 ...       float64              float64               object             float64      
---------- ----------------- ----------------- ------- ... ------------------- --------------------- ------------------- -------------------
 (2020 SO) 2020-Oct-19 00:00         2459141.5  28.649 ... -0.7422716666666667             -0.090774 2020-10-19 00:00:00  0.7478015419963449
 (2020 SO) 2020-Oct-19 01:00 2459141.541666667  28.649 ... -1.2821566666666666  -0.10429166666666667 2020-10-19 01:00:00  1.2863912583712191
 (2020 SO) 2020-Oct-19 02:00 2459141.583333333  28.649 ... -1.7245666666666668  -0.12371249999999999 2020-10-19 02:00:00  1.7289982563421018
 (2020 SO) 2020-Oct-19 03:00       2459141.625  28.649 ... -2.0383833333333334  -0.14766333333333334 2020-10-19 03:00:00    2.04372480378896
 (2020 SO) 2020-Oct-19 04:00 2459141.666666667  28.649 ... -2.2012833333333335              -0.17444 2020-10-19 04:00:00  2.2081842376058916
 (2020 SO) 2020-Oct-19 05:00 2459141.708333333  28.649 ... -2.2015333333333333  -0.20212666666666665 2020-10-19 05:00:00  2.2107926648954566
 (2020 SO) 2020-Oct-19 06:00        2459141.75  28.649 ...            -2.03885  -0.22874666666666665 2020-10-19 06:00:00  2.0516418693356573
 (2020 SO) 2020-Oct-19 07:00 2459141.791666667  28.649 ... -1.7244666666666666  -0.25239666666666666 2020-10-19 07:00:00  1.7428394538192233
 (2020 SO) 2020-Oct-19 08:00 2459141.833333333  28.649 ...            -1.28022   -0.2713983333333333 2020-10-19 08:00:00  1.3086711977177885
       ...               ...               ...     ... ...                 ...                   ...                 ...                 ...
 (2020 SO) 2020-Oct-21 15:00       2459144.125  28.649 ...  2.5100566666666664             -0.181445 2020-10-21 15:00:00   2.516606198415393
 (2020 SO) 2020-Oct-21 16:00 2459144.166666667  28.649 ...  2.6530816666666666  -0.15397366666666665 2020-10-21 16:00:00  2.6575459017728282
 (2020 SO) 2020-Oct-21 17:00 2459144.208333333  28.649 ...   2.628511666666667  -0.12591883333333334 2020-10-21 17:00:00   2.631526008685988
 (2020 SO) 2020-Oct-21 18:00        2459144.25  28.649 ...             2.43776             -0.099101 2020-10-21 18:00:00  2.4397735193662955
 (2020 SO) 2020-Oct-21 19:00 2459144.291666667  28.649 ...  2.0932983333333333  -0.07526166666666666 2020-10-21 19:00:00   2.094650861314495
 (2020 SO) 2020-Oct-21 20:00 2459144.333333333  28.649 ...  1.6179068333333333             -0.055955 2020-10-21 20:00:00   1.618874140682868
 (2020 SO) 2020-Oct-21 21:00       2459144.375  28.649 ...  1.0433095000000001             -0.042447 2020-10-21 21:00:00   1.044172620115683
 (2020 SO) 2020-Oct-21 22:00 2459144.416666667  28.649 ... 0.40819866666666665  -0.03562766666666666 2020-10-21 22:00:00 0.40975051201988205
 (2020 SO) 2020-Oct-21 23:00 2459144.458333333  28.649 ...           -0.244245 -0.035944166666666666 2020-10-21 23:00:00 0.24687568357851913
 (2020 SO) 2020-Oct-22 00:00         2459144.5  28.649 ... -0.8692216666666667  -0.04335933333333333 2020-10-22 00:00:00  0.8703024402987096

```
