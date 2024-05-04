'''
CSC 315-01
Professor DeGood
Summary:
    Handles all the backend:
        - Connects to Goat database
        - Updates the goat database each time the server is restarted
        - Reads inputs from home webpage
        - Adds function to redirect to the webpage where processing will be handled
        
Primary Contributor: Milian Ingco
'''

from flask import Flask, redirect, url_for, request, render_template, session
from datetime import datetime
import psycopg2
import csv
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
import pandas as pd
import statsmodels.api as sm

# connect to GoatDB
conn = psycopg2.connect("dbname=GoatDB user=postgres password=")

print(conn)

# cursors are used to perform db operations
cur = conn.cursor()

# Copy commands from Import Goat file
with open('ImportGoat.sql', 'r') as f:
    ImportGoat = f.read()

# Run ImportGoat.sql
cur.execute(ImportGoat)

# did i change status to a'liv'e? yeah. it fit the 3 letter scheme better. murder me ig
# Get values from Animal.csv and insert into Animal relation
with open('Animal.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        animal_id = str(row[0])
        tag = "''" if row[2] == '' else "'{}'".format(str(row[2]))
        sex = "''" if row[7] == '' else "'{}'".format(str(row[7]))
        dob = "NULL" if row[8] == '' else "'{}'".format(str(row[8]))
        dam = "''" if row[10] == '' else "'{}'".format(str(row[10]))
        liv = "''" if row[25] == '' else "'{}'".format(str(row[25]))
        command = "INSERT INTO Animal (animal_id, tag, sex, dob, dam, status) VALUES ({}, {}, {}, {}, {}, {});".format(animal_id, tag, sex, dob, dam, liv)
        cur.execute(command)

# Get values from Note.csv and insert into Note relation
# -- we never use anything from note --

# Get values from SessionAnimalActivity.csv and insert into SessionAnimalActivity relation
# -- we never use anything from sessionanimalactivity

# Get values from SessionAnimalTrait.csv and insert into SessionAnimalTrait relation
with open('SessionAnimalTrait.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        session_id = str(row[0])
        animal_id = str(row[1])
        trait_code = str(row[2])
        alpha_value = "''" if row[3] == '' else "'{}'".format(str(row[3]))
        when_measured = "'{}'".format(str(row[5]))
        command = "INSERT INTO SessionAnimalTrait (session_id, animal_id, trait_code, alpha_value, when_measured) VALUES ({}, {}, {}, {}, {});".format(session_id, animal_id, trait_code, alpha_value, when_measured)
        cur.execute(command)

# Copy commands from CreateTables file
with open('CreateTables.sql', 'r') as f:
    CreateTable = f.read()

# Run CreateTables.sql
cur.execute(CreateTable)

# commit changes to db
conn.commit()

# -----------------------------------------------------[ EVERYTHING PRIOR IS JUST SETTING UP THE DATABASE : line 76 ]-------------------------------------------------

# flask constructor
app = Flask(__name__)
# create secret key for the session
app.secret_key = '11594232024'

@app.route('/')
def return_home():
    return render_template('webpage.html')

#--------------------------------------------------------------------------[ FAMILY TREE ]---------------------------------------------------------------------------------- 
@app.route('/family_tree', methods=['POST'])
def get_familytree_form():
    # Get text input
    dam_input_list = request.form['dam_text']
    
    # Split text into an array, separated by commas and not including spaces before or after commas
    dam_input_list = [x.strip() for x in dam_input_list.split(',')]
    
    # Each string can only be 16 characters long, since thats the max length of the tag
    dam_input_list = [string[:16] for string in dam_input_list]
    
    # Check if all tags exist in dam
    dam_list = []
    for dam in dam_input_list:
        cur.execute("SELECT * FROM GoatDam WHERE dam='{}'".format(dam))
        out = cur.fetchone()
        if out is not None:
            # Get all the dam tags that exist in the database
            dam_list.append(out[4])

    # if no valid tags, redirect home
    if len(dam_list) == 0:
        return redirect(url_for('return_home'))
    
    session['family_tree'] = dam_list
    session['compare_type'] = 'family_tree'

    return redirect(url_for('goat_calculations', compare_type='family_tree', redirect='0'))

#-----------------------------------------------------------------------[ BIRTH COHORT ]-----------------------------------------------------------------------------------
@app.route('/birth_cohort', methods=['POST'])
def get_birthcohort_form():
    # Get input dates
    earliest_date = request.form['earliest_birthdate']
    latest_date = request.form['latest_birthdate']
    current_date = datetime.now()

    # Ensures dates entered are valid dates
    try:
        earliest_date = datetime.strptime(earliest_date, '%Y-%m-%d')
        latest_date = datetime.strptime(latest_date, '%Y-%m-%d')
    except ValueError:
        return redirect(url_for('return_home'))
    
    # Ensure they are not living in the future
    if latest_date > current_date:
        return redirect(url_for('return_home'))

    session['birth_cohort'] = [earliest_date, latest_date]
    session['compare_type'] = 'birth_cohort'

    return redirect(url_for('goat_calculations', compare_type='birth_cohort', redirect='0'))

#--------------------------------------------------------------------------[ ALL GOATS ]-----------------------------------------------------------------------------------
@app.route('/all_goats', methods=['POST'])
def get_allgoats_form():

    session['all_goats'] = request.form['all_goat_options']
    session['compare_type'] = 'all_goats'
    
    return redirect(url_for('goat_calculations', compare_type='all_goats', redirect='0'))

# IMPLEMENT GRAPHING PAGE !!! OH DEAR OH GOD OH LORD
#--------------------------------------------------------------------------[ CALCULATIONS ]-----------------------------------------------------------------------------
@app.route('/graph_comparison/<compare_type>/<redirect>')
def goat_calculations(compare_type, redirect):
    
    # threw long parsing using session data into a function bc clutter
    lists = parse_array(compare_type)
    
    days_x = lists[0]
    weights_y = lists[1]
    group_num = lists[2]
    label = lists[3]
    
    figures = []
    # if redirect is 0, only display plain scatter plot
    if redirect == '0':
        figures = create_scatter_plot(days_x, weights_y, group_num, label)
    # if redirect is 1, display scatter plot with linear regression, display derivative of linear regression
    elif redirect == '1':
        figures = create_linear_plot(days_x, weights_y, group_num, label)
    # if redirect is 2, display scatter plot with log regression, display derivative of log regression
    elif redirect == '2':
        figures = create_log_plot(days_x, weights_y, group_num, label)
    # if redirect is 3, display scatter plot with piecewise regression, display derivative of piecewise regression
    else:
        figures = create_piecewise_plot(days_x, weights_y, group_num, label)

    # Turn figures to HTML to display them
    scatter_plot_html = pio.to_html(figures[0], full_html=False)
    deriv_plot_html = pio.to_html(figures[1], full_html=False)
    return render_template('graph.html', scatter_plot=scatter_plot_html, deriv_plot=deriv_plot_html)

@app.route('/linear', methods=['POST'])
def linear_regression():
    return redirect(url_for('goat_calculations', compare_type=session['compare_type'], redirect='1'))

@app.route('/logarithmic', methods=['POST'])
def log_regression():
    return redirect(url_for('goat_calculations', compare_type=session['compare_type'], redirect='2'))

@app.route('/piecewise', methods=['POST'])
def piecewise_regression():
    return redirect(url_for('goat_calculations', compare_type=session['compare_type'], redirect='3'))


#-------------------------------------------------------------------- GRAPHING FUNCTIONS -------------------------------------------------------------------------------------
# Should return two figures [ scatter plot with trendline, plot with derivative of trendline

# Create scatter plot
def create_scatter_plot(x, y, group_num, label):
    # Create a dataframe with the parameters
    df = pd.DataFrame({
            'Goats Age in Days' : x,
            'Goats Weight in Pounds (lbs)' : y,
            'group' : group_num,
            'label' : label
        })

    # Create a default scatter plot with no trend lines
    fig = px.scatter(df, x='Goats Age in Days', y='Goats Weight in Pounds (lbs)', color='group', hover_data='label', title="Goats Weight over Time")
   
    fig_list = [fig, fig]

    return fig_list

# Create plots with linear trend lines
def create_linear_plot(x, y, group_num, label):
    df = pd.DataFrame({
            'Goats Age in Days' : x,
            'Goats Weight in Pounds (lbs)' : y,
            'group' : group_num,
            'label' : label
        })
    
    fig = px.scatter(df, x='Goats Age in Days', y='Goats Weight in Pounds (lbs)', color='group', hover_data='label', title="Goats Weight over Time", trendline="ols")
   
    fig_list = [fig, fig]

    return fig_list

# Create plots with logarithmic trend lines
def create_log_plot(x, y, group_num, label):
    df = pd.DataFrame({
        'Goats Age in Days' : x,
        'Goats Weight in Pounds (lbs)' : y,
        'group' : group_num,
        'label' : label
    })

    fig = px.scatter(df, x='Goats Age in Days', y='Goats Weight in Pounds (lbs)', color='group', hover_data='label', title="Goats Weight over Time", trendline="ols", trendline_options=dict(log_x=True))

    fig_list = [fig, fig]

    return fig_list

# Create plots with piecewise trend lines
def create_piecewise_plot(x, y, group_num, label):
    df = pd.DataFrame({
        'Goats Age in Days' : x,
        'Goats Weight in Pounds (lbs)' : y,
        'group' : group_num,
        'label' : label
    })

    fig = px.scatter(df, x='Goats Age in Days', y='Goats Weight in Pounds (lbs)', color='group', hover_data='label', title="Goats Weight over Time")

    fig_list = [fig, fig]

    return fig_list


#-------------------------------------------------------------------- Parses and returns mega array ------------------------------------------------------------------------
def parse_array(compare_type) :
    '''
                NOTES
        session['family_tree']  = [ ALL VALID DAM TAGS ]
        session['birth_cohort'] = [ EARLIEST BIRTHDATE , LATEST BIRTHDATE ]
        session['all_goats']    = TYPE OF ALL GOATS
    '''

    goat_list = [[]]

    if compare_type == 'family_tree': #---------------------------------{ FAMILY TREE
        dam_list = session.get('family_tree')
        # SQL Code to recursively select the full family tree of a given dam
        recurse_family = """
            WITH RECURSIVE FamilyTree AS (
                SELECT tag, dam
                FROM GoatDam
                WHERE dam = '{}'

                UNION ALL
                
                SELECT g.tag, g.dam
                FROM GoatDam g
                INNER JOIN FamilyTree ft on g.dam = ft.tag
            )
            SELECT ft.tag FROM FamilyTree ft
            WHERE EXISTS (
                SELECT 1
                FROM Weights w
                WHERE w.tag = ft.tag
            );
        """
        # For each dam, return a list of all its children
        for dam in dam_list:
            cur.execute(recurse_family.format(dam))
            goat_list.append(cur.fetchall())

        conn.commit()

        # Remove empty row
        del goat_list[0]
        
        # Ensure that each goat returned exists in weights

        #-------------------------------------------------------------- RETURNS TOTAL_DAM_CHILDREN

    elif compare_type == 'birth_cohort': #--------------------------------{ BIRTH COHORT
        earliest_date = session.get('birth_cohort')[0]
        latest_date = session.get('birth_cohort')[1]
        # Get goats in a specific birth cohort
        birth_cohort = """
            SELECT gt.tag
            FROM GoatDam gt
            WHERE gt.dob > '{}' AND gt.dob < '{}' AND EXISTS (
                SELECT 1
                FROM Weights w
                WHERE w.tag = gt.tag
            );
        """.format(earliest_date, latest_date)
        cur.execute(birth_cohort)
        # returns all those goat's tags
        goat_list[0] = cur.fetchall()
        # commit all changes
        conn.commit()
        
        if goat_list is None:
            return redirect(url_for('return_home'))

        # Ensure that each goat returned exists in weights

        #------------------------------------------------------------- RETURNS BIRTH_COHORT_LIST

    elif compare_type == 'all_goats': #------------------------------------{ ALL GOATS
        goat_option = session.get('all_goats')
        # Get which group is selected
        all_goats = """
            SELECT a.tag
                FROM Animal a
            WHERE status = '{}' AND EXISTS (
                SELECT 1 
                FROM Weights w
                WHERE w.tag = a.tag
            );
        """
        if goat_option == 'all':
            cur.execute("SELECT a.tag FROM Animal a WHERE EXISTS (SELECT 1 FROM Weights w WHERE w.tag = a.tag);")
        else:
            cur.execute(all_goats.format(goat_option))
        goat_list[0] = cur.fetchall()

        # Ensure that each goat returned exists in weights

        conn.commit()
        
        #-------------------------------------------------------------- RETURNS ALL_GOATS_LIST
   
    #------------------------------------------------------------------- GOAL : For each goat's tag, get their entire weighing history
    #          |
    #          |
    #        w |
    #        e |                     *
    #        i |              *
    #        g |        *
    #        h |    *
    #        t | *
    #          |_______________________
    #               days since birth

    # For each group in goat_list, get their dob, when measured, and weight
    group_num = 0
    tag_num = 0
    goat_data = [[[]]]
    
    for goat_group in goat_list:
        # For a group of goats, go through each tag
        group_array = []
        goat_data.append(group_array)
        for goat in goat_group:
            # For each tag, get all times it was measured, and the associated data
            cur.execute("SELECT tag, (when_measured - dob) AS time_since_birth, weight FROM Weights WHERE tag = '{}' AND dob IS NOT NULL AND when_measured >= dob;".format(goat[0]))
            temp_array = cur.fetchall()
            tag_array = []
            # Only add tags that return non empty reponses
            if len(temp_array) != 0:
                goat_data[group_num].append(tag_array)
                for item in temp_array:
                    # Get           tag      when - dob    weight
                    measure_temp = [item[0], item[1].days, item[2]]
                    goat_data[group_num][tag_num].append(measure_temp)
                tag_num = tag_num + 1  
        group_num = group_num + 1
        tag_num = 0

    # Delete any empty arrays that might've gotten through
    group_index = 0
    tag_index = 0
    for group in goat_data:
        if len(group) == 0:
            del goat_data[group_index]
            group_index = group_index - 1
        else:
            for tag in group:
                if len(tag) == 0:
                    del goat_data[group_index][tag_index]
                    tag_index = tag_index - 1
                tag_index = tag_index + 1
        tag_index = 0
        group_index = group_index + 1

    weights_y = []
    days_x = []
    group_num = []
    label = []
    group_index = 0
    min_weight = 10000
    max_weight = 0
    min_day = 10000
    max_day = 0
    for group in goat_data:
        for tag in group:
            for weight_session in tag:
                weights_y.append(float(weight_session[2]))
                days_x.append(int(weight_session[1]))
                label.append(weight_session[0])
                if compare_type == 'family_tree':
                    group_num.append(session.get(compare_type)[group_index])
                else:
                    group_num.append(group_index)
        group_index = group_index + 1

    lists = [days_x, weights_y, group_num, label]

    return lists

if __name__ == '__main__':
    app.run(debug=True)
