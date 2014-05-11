# Your Game Title

Entry in PyWeek #2014  <http://www.pyweek.org/>
URL: http://pyweek.org/e/threadless
Team: YOUR TEAM NAME (leave the "Team: bit")
Members: YOUR TEAM MEMBERS (leave the "Members: bit")
License: see LICENSE.txt

## Running the Game

On Windows or Mac OS X, locate the "run_game.pyw" file and double-click it.

Othewise open a terminal / console and "cd" to the game directory and run:

    python run_game.py

## How to Play the Game

TBD

## Development notes

```
pip install cython==0.20.1
pip install -r requirements.txt
```

Then just to check that you've got everything installed correctly try
running the test script.

```
python test.py
```

Creating a source distribution with

    python setup.py sdist

You may also generate Windows executables and OS X applications:

    python setup.py py2exe
    python setup.py py2app

Upload files to PyWeek with:

    python pyweek_upload.py

Upload to the Python Package Index with:

    python setup.py register
    python setup.py sdist upload
