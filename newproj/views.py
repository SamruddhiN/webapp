"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template,request,session,redirect,url_for,flash
from werkzeug import secure_filename
from newproj import app
import pymysql
import json
from pymongo import MongoClient
import bcrypt 

client = MongoClient('localhost:27017')
db = client.test  #connect to test database

def insertSignUp(email,username,password,role,team):
    try:
      
        db.demoDb.insert_one(
            {
                 "name":username,
                 "email":email,
                 "password": password,
                 "role": role,
                 "team":team,
               })
        print '\nInserted data successfully\n'
    
    except Exception, e:
        print str(e)
        return "Username already exists !! Try to login or register as new user"


def  insertWorkItem(username,pull_req,reviewer,doc_file,user_story,win_build,lin_build,pytest,pytest_reports,qa_stat,re_status,final_status,date_created):
     try:
      
        db.demoDb.update({"name":username},{'$push':{
                                                   
                                                   "work_item": 
                                                 {
                                                  "pull_req":pull_req,
                                                  "reviewer":[{"rname":reviewer,
                                                               "rstatus":re_status 
                                                               }], 
                                                   "doc_file" : doc_file,
                                                   "user_story": user_story,
                                                   "win_build": win_build,
                                                   "lin_build":lin_build,
                                                   "pytest":pytest,
                                                   "pytest_reports":pytest_reports,
                                                   "qa_status":qa_stat,
                                                   "final_status":final_status,
                                                   "date_created":date_created,
                                                   "date_merged":""
                                               }             
                                   }
                       }
)
        print '\nInserted data successfully\n'
    
     except Exception, e:
        print str(e)


@app.route('/')
@app.route('/login', methods=["GET","POST"])
def login():
     if request.method == 'POST':
       login_user =db.demoDb.find_one({'name' : request.form['username']})
       if login_user:
            if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password'].encode('utf-8')) == login_user['password'].encode('utf-8'):
                session['username'] = request.form['username']
                return redirect(url_for('home'))
       else:
        flash("username/password wrong combination!!")

     """Renders the login page."""
     return render_template('login.html',title='Login Page',year=datetime.now().year)      

@app.route('/logout', methods=["GET"])
def logout():
     session.pop('username', None)
     return redirect(url_for('login'))
      
@app.route('/signup', methods=["GET","POST"])
def signup():
      if request.method == 'POST':
        email =request.form.get('email','')
        username = request.form.get('username','')
        existing_user = db.demoDb.find_one({"name" : request.form['username']})

        if existing_user:
            flash('That username already exists!')
        else:
            password = request.form.get('password','')
            hashpass = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
            role=request.form.get('role','')
            team=request.form.getlist('team')
            insertSignUp(email,username,hashpass,role,team)
        return redirect(url_for('login'))
         
       
      else:
        """Renders the contact page."""
        return render_template(
        'signup.html',
       title='SignUp',
       year=datetime.now().year,
        message='Your signup page.'
       )

    
  
@app.route('/home', methods =["GET","POST"])
def home():
        query=db.demoDb.find_one({"name":session['username']})
        session['role'] =query["role"]  
        #tasks=db.demoDb.find()  #WorkItems with pytest ==Success and qa_status===pending
        if session['role'] =="QA":
            return redirect(url_for('dashboard'))

        else:
         """Renders the home page."""
         return render_template(
            'home.html',
         title='Home Page',
         year=datetime.now().year,
            message='Pytest home page',
            username = session['username']
         )


@app.route('/upload', methods =['GET','POST'])
def upload():
    if request.method == "POST":
      username = session['username']
      pull_req = request.form.get('pull_req','')
      reviewer= request.form.get('reviewer','')
      doc_file=request.form.getlist('file[]')
      user_story =request.form.get('user_story','') 
      win_build="InProgress"
      lin_build="InProgress"
      pytest="InProgress"
      pytest_reports ="path"
      qa_status="Pending"
      re_status ="Pending"
      final_status="Pending"
      date_created=datetime.now()
      existing_pr=db.demoDb.find_one({"work_item.pull_req":pull_req})
      #query= db.demoDb.aggregate([{'$match':{"work_item.pull_req":pull_req}},{"$unwind":"$work_item"},{'$match':{"work_item.pull_req":pull_req }},{'$project':{"pull_req":"$work_item.pull_req","_id":0}}])
      
      if existing_pr:
        flash('Pull request already exists!!')
      else:  
        insertWorkItem(username,pull_req,reviewer,doc_file,user_story,win_build,lin_build,pytest,pytest_reports,qa_status,re_status,final_status,date_created)
        return redirect(url_for('dashboard'))

    return render_template('info_demo.html',username = session['username'])

@app.route('/dashboard', methods =['GET','POST'])
def dashboard():
   
    if session['role'] =="QA":
      cursor=db.demoDb.aggregate([{'$match':{'$and':[{"work_item.pytest":"Success"},{"work_item.qa_status":"Pending"}]}},{"$unwind":"$work_item"},{'$match':{'$and':[{"work_item.pytest":"Success"},{"work_item.qa_status":"Pending"}]}},{'$project':{"pull_req":"$work_item.pull_req","qa_status":"$work_item.qa_status","_id":0}}])
      return render_template('dashboard.html',year=datetime.now().year,username = session['username'],role=session['role'],cursor=cursor)
    elif session['role'] =="RD":
      cursor1=db.demoDb.find()
      cursor3=db.demoDb.aggregate([{'$match':{"work_item.reviewer.rname":session['username']}},{"$unwind":"$work_item"},{'$match':{"work_item.reviewer.rname":session['username']}},{'$project':{"rname":"$work_item.reviewer.rname"}}])
      rname=False
      for c in cursor3:
        if session['username'] in c['rname']:
            rname=True
      print rname
      cursor2=db.demoDb.aggregate([{'$match':{'$and':[{"work_item.qa_status":"Approved"},{"work_item.reviewer.rstatus":"Pending"},{"work_item.reviewer.rname":session['username']}]}},{"$unwind":"$work_item"},{'$match':{'$and':[{"work_item.qa_status":"Approved"},{"work_item.reviewer.rstatus":"Pending"},{"work_item.reviewer.rname":session['username']}]}},{'$project':{"rname":"$work_item.reviewer.rname","pull_req":"$work_item.pull_req","_id":0,"name":1}}])  
      return render_template('dashboard.html',year=datetime.now().year,username = session['username'],role=session['role'],cursor=cursor1,cursor2=cursor2,rname=rname)
 
@app.route('/update_qastatus',methods=['GET','POST'])
def update_qastatus():
        
        if 'qa_accept' in request.args:
            pull_req = request.args.get('qa_accept')
            print pull_req
            db.demoDb.update({"work_item": { '$elemMatch': { "pull_req": pull_req } } }, { '$set': { "work_item.$.qa_status": "Approved" } } )
        else:
            pull_req = request.args.get('qa_reject')
            print pull_req
            db.demoDb.update({"work_item": { '$elemMatch': { "pull_req": pull_req } } }, { '$set': { "work_item.$.qa_status": "Rejected" } } )
            db.demoDb.update({"work_item": { '$elemMatch': { "pull_req": pull_req } } }, { '$set': { "work_item.$.final_status": "Rejected" } } )
        return redirect(url_for('dashboard'))

@app.route('/update_restatus',methods=['GET'])
def update_restatus():
        pull_req = request.args.get('re_accept')
        print pull_req
        if 're_accept' in request.args:
            pull_req = request.args.get('re_accept')
            print pull_req
            db.demoDb.update({"work_item": { '$elemMatch': { "pull_req": pull_req } } }, { '$set': { "work_item.$.reviewer": [{ "rname":session['username'], "rstatus": "Approved" }] } } )
            db.demoDb.update({"work_item": { '$elemMatch': { "pull_req": pull_req } } }, { '$set': { "work_item.$.final_status": "Approved" } } )
            db.demoDb.update({"work_item": { '$elemMatch': { "pull_req": pull_req } } } , { '$set': { "work_item.$.date_merged": datetime.now()} } )            
        else:
            pull_req = request.args.get('re_reject')
            print pull_req
            db.demoDb.update({"work_item": { '$elemMatch': { "pull_req": pull_req } } }, { '$set': { "work_item.$.reviewer": [{ "rname":session['username'], "rstatus": "Rejected" }] } }  )
            db.demoDb.update({"work_item": { '$elemMatch': { "pull_req": pull_req } } }, { '$set': { "work_item.$.final_status": "Rejected" } } )
        return redirect(url_for('dashboard'))


@app.route('/change_pr',methods=['GET','POST'])
def change_pr():
        if 'del_pr' in request.args:
            pull_req = request.args.get('del_pr')
            db.demoDb.update({"work_item": { '$elemMatch': { "pull_req": pull_req } } }, { '$pull': { "work_item":{ "pull_req": pull_req  } } })
            return redirect(url_for('dashboard'))
        elif 'update_pr' in request.args:
             pull_req = request.args.get('update_pr')
             print pull_req
             cursor=db.demoDb.find({"work_item": { '$elemMatch': { "pull_req": pull_req } } })
             return render_template('change.html', username = session['username'],pull_req=pull_req)

@app.route('/summary', methods=['GET','POST'])
def summary():
    if request.method=='GET':
        cursor=db.demoDb.find().sort('date',1)
        return render_template('summary_table.html',cursor=cursor, username = session['username'])
    
@app.route('/update_bp', methods=['GET'])
def update_bp():
       pull_req = request.args.get("pr")
       #query = db.demoDb.find({'$and':[{"work_item": { '$elemMatch': { "pull_req": pull_req , "qa_status":"Approved"} } }]},{'$project':{"qa_status":"$work_item.qa_status","_id":0}})
   #if query['qa_status'] == 'Approved':
       win_build=request.args.get('win_build')
       db.demoDb.update({"work_item": { '$elemMatch': { "pull_req": pull_req } } }, { '$set': { "work_item.$.win_build": win_build } } )
  
       lin_build=request.args.get('lin_build')  
       db.demoDb.update({"work_item": { '$elemMatch': { "pull_req": pull_req } } }, { '$set': { "work_item.$.lin_build": lin_build} } )

       pytest=request.args.get('pytest') 
       db.demoDb.update({"work_item": { '$elemMatch': { "pull_req": pull_req } } }, { '$set': { "work_item.$.pytest": pytest } } )

       if pytest=='Failed' or win_build=='Failed'or lin_build=='Failed':
          db.demoDb.update({"work_item": { '$elemMatch': { "pull_req": pull_req } } }, { '$set': { "work_item.$.final_status": "Rejected" } } ) 
       else:
          db.demoDb.update({"work_item": { '$elemMatch': { "pull_req": pull_req } } }, { '$set': { "work_item.$.final_status": "Pending" } } )  
       return redirect(url_for('dashboard'))       
   #else:
        #flash('Cannot update!!')





















#from pyteamcity import TeamCity,HTTPError
#from flask_sqlalchemy import *
#import pymysql.cursors
#import requests
#import mock 
#connection=pymysql.connect(host='127.0.0.1',user='root',password='password@123',db='test',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor, autocommit=True)


"""
db.demoDb.findAndModify({query: {"work_item": { '$elemMatch': { "pull_req": pull_req } } },update: { '$set': { "work_item.$.qa_status": "Approved" } } })
if "qa_accept" in request.form:
"""

"""
@app.route('/new')
def new():
    
    cursor = connection.cursor()
    sql = "SELECT * FROM test.user_login;"
    cursor.execute(sql)
    results = cursor.fetchall()
    print(results)
    return render_template('WebPage1.html', results=results) 

  
    user = 'snaik'
    password = ''
    host = 'teamcity.ansys.com'
    port = 8080

    #tc = TeamCity('snaik', '', 'teamcity.ansys.com', 8080)
    tc = TeamCity(user, password, host, port)
    data = tc.get_projects()
    print(json.dumps(data, indent=4))
    #return render_template('WebPage1.html')

    expected_url = 'http://teamcity.ansys.com:8080/teamcity/'
    url = tc.get_projects(return_type='url')
    assert url == expected_url

    req = tc.get_projects(return_type='request')
    assert req.method == 'GET'
    assert req.url == expected_url

     cursor = connection.cursor()
        sql = "INSERT into user_login VALUES (email,username,password);"
        sql1=  "Insert into user_login(email,username,password) values (%s,%s,%s);" %(email,username,password)
        cursor.execute(sql1)
        results = cursor.fetchall()
        print(results)


@app.route('/uploader', methods = ['GET', 'POST'])
def uploader():
   if request.method == 'POST':
     uploaded_files = flask.request.files.getlist("file[]")
     print uploaded_files
     return ""

"""
    
"""
     if session['role'] =="QA":        
        #cursor=db.demoDb.find({'$and':[{"work_item.pytest"=="Success"},{"work_item.qa_status"=="Pending"}]})
        image="/static/dashboard/images/qa.jpg"
        return render_template('dashboard.html',year=datetime.now().year,username = session['username'],role=session['role'],image=image)#,cursor=cursor
     else:
        #cursor=db.demoDb.find({"name":session['name']})
        image="/static/dashboard/images/developer.png"
"""