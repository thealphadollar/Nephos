"""
main/views.py

Controller Responsible for Handling the main page

"""
import json
from datetime import datetime
from flask import render_template, Response
from ..main import MAIN_BP
from .. import DB, APP


@MAIN_BP.route('/', methods=['GET'])
def homepage():
    """
    <url>/

    View that Renders the Homepage

    """
    return "Hello World!"


@MAIN_BP.route('/api/channels', methods=['GET'])
def channels():
    """
    <url>/api/channels

    View that Returns the channel

    """
    data = DB.session.execute('SELECT * FROM channels;')
    # http://codeandlife.com/2014/12/07/sqlalchemy-results-to-json-the-easy-way/
    return Response(json.dumps([dict(r) for r in data]), mimetype='application/json')


@MAIN_BP.route('/channels', methods=['GET'])
def show_channels():
    """
    <url>/channels

    View that Returns the channel and displays them in a nice table

    """
    data = DB.session.execute('SELECT * FROM channels;')
    # http://codeandlife.com/2014/12/07/sqlalchemy-results-to-json-the-easy-way/
    channels = [dict(r) for r in data]
    return render_template('channels.html', channels=channels)


@MAIN_BP.route('/api/jobs', methods=['GET'])
def jobs():
    """
    <url>/api/jobs
    
    View that Returns the jobs

    """

    # This is Used to get the Jobs Database instead of storage.db
    jobs_engine = DB.get_engine(APP, 'jobs')
    data_raw = jobs_engine.execute('SELECT * FROM apscheduler_jobs;')

    data = {}

    number = 0
    
    # Put Everything in a Global Dict so we can later send it as a JSON
    for row in data_raw:
    # This Function exists because the one line solution didn't work

    # Create a Dictionary and Put it inside a Main Dictionary
        dat = {'job_name': row[0], 'next_run_time': str(row[1]), 'job_state': str(row[2])}
        data[number] = dict(dat)
        number += 1

    return Response(json.dumps(data), mimetype='application/json')

@MAIN_BP.route('/jobs', methods=['GET'])
def show_jobs():
    """
    <url>/jobs

    View that Returns the jobs and displays them in a nice table
    """

    # This is Used to get the Jobs Database instead of storage.db
    jobs_engine = DB.get_engine(APP, 'jobs')
    data_raw = jobs_engine.execute('SELECT * FROM apscheduler_jobs;')
    
    data = {}

    number = 0

    # Convert into Dict so Jinja Can Easily Parse it
    for row in data_raw:
    # This Function exists because the one line solution didn't work

    # Convert to Human Readable Date
        timestamp = int(row[1])
        date = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            
    # Create a Dictionary and Put it inside a Main Dictionary
    dat = {'channel_name': row[0], 'next_run_time': str(date)}
        data[number] = dict(dat)
        number += 1

    return render_template('jobs.html', jobs=data)

