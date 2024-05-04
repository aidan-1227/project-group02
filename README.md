# project-group02
# Group 2: Calculating a Growth Curve for a Herd of Goats
## Description
This is a website that allows the user to select either a list of dams ( mother goats ), a range of birth dates, or a set group of goats such as dead, living, sold, or all goats, and visualizes those goats' data graphically as well as provides options to find an overall trend using linear or logarithmic regression. 

# Installation

## Requirements
- Latest version of Python
- pip
- Python virtual environment set up
- Postgres
### Python Librarise
- Flask
- psycopg2-binary
- plotly
- numpy
- pandas
- statsmodels

## Set up on Arch distributions of Linux

- Update system this is the only command that changes between computer versions
```
sudo pacman -Syu
```
- Check python version
```
python –version
```
- Check if pip is installed (it was not for me :D) this is the only other command that changes between computer versions
```
pip –version
```
- If not installed v
```
sudo pacman -S python-pip
```
- Create virtual environment
```
python -m venv [folder of choice, mine was ~ the home folder]
```
- If not installed : 
```
pip install virtualenv
```
- If says not added to path WHEN INSTALLING virtualenv
- Go to home directory (cd ~) and open or create the file .bashrc
- Append to that file 
```
export PATH="$PATH:/var/lib/postgresql/.local/bin"
```
- Then save and quit, and run
```
source ~/.bashrc
```
- Then create a virtual environment
```
virtualenv venv
```
- To run it, run
```
source ./venv/bin/activate
```
- Once its open, install flask (this will install it temporarily as long as the virtual environment is open)
- Activate virtual environment
```
source [folder selected]/bin/activate
```
- Install Flask
```
pip install Flask
```
- Install psycopg2 (specifically the binary)
```
pip install psycopg2-binary
```
- Install plotly
```
pip install plotly
```
- Install numpy
```
pip install numpy
```
- Install pandas
```
pip install pandas
```
- Install statsmodels
```
pip install statsmodels
```
- Create GoatDB database with owner postgres
```
createdb -O postgres GoatDB
```
- Run the server
```
python3 backend.py
```
- Open the link

For other linux distributions / other computers
- Make sure pip is installed
- Make sure prereq libraries are installed
## Usage
- Enter any number of dams to compare different family trees
- Can enter ranges of dates to analyze birth cohorts
- Can select from a predefined list to analyze growth rate of dead, living, sold, or all goats
- In terms of analysis: 
- Scatter plots of weights correlating to their age
- Includes:
- Linear regression lines
- Logarithmic regression lines

## Future Updates
In the future I hope to include piecewise regression for more control over analysis on certain ages, as well as the ability to view the derivative of the given regression lines as to see the rate of growth at any given age. 
## Authors
Milian Ingco



