from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort


import bd 

bp_api = Blueprint('api', __name__)