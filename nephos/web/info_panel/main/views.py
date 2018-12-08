"""
main/views.py

Controller Responsible for Handling the main page

"""
import json
from flask import render_template, Response
from ..main import MAIN_BP
from .. import DB



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
    <url>/api/channels

    View that Returns the channel and displays them in a nice table

    """
    data = DB.session.execute('SELECT * FROM channels;')
    # http://codeandlife.com/2014/12/07/sqlalchemy-results-to-json-the-easy-way/
    channels = [dict(r) for r in data]
    return render_template('channels.html', channels=channels)
