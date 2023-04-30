from flask import Flask, request, session, render_template, url_for, jsonify, redirect
import dbfunc, mysql.connector
from datetime import datetime

from passlib.hash import sha256_crypt
import hashlib
import gc
from functools import wraps

app = Flask(__name__)

app.secret_key = 'sixtussecretkey'     #secret keey for sessions

# / or /index creates a route that loads the main page where 
# register and login options are offered to end users
# @app.route('/')
# @app.route('/index/')
# def mainpage_override():
#     return render_template('index.html')

# # /index/<usertype> creates an end point that should display contents on 
# # mainpage.html based on user type e.g., if user type is admin then 
# # show adminfeatures, or if user type is standard then show standard 
# # user feastures

# @app.route('/index/<usertype>')
# def mainpage(usertype):
#     return render_template('index.html', usertype=usertype)

@app.route('/')
def index():
	conn = dbfunc.getConnection()
	if conn != None:    #Checking if connection is None         
		print('MySQL Connection is established')                          
		dbcursor = conn.cursor()    #Creating cursor object            
		dbcursor.execute('SELECT DISTINCT deptCity FROM routes;')   
		#print('SELECT statement executed successfully.')             
		rows = dbcursor.fetchall()                                    
		dbcursor.close()              
		conn.close() #Connection must be 
		cities = []
		for city in rows:
			city = str(city).strip("(")
			city = str(city).strip(")")
			city = str(city).strip(",")
			city = str(city).strip("'")
			cities.append(city)
		return render_template('index.html', departurelist=cities)
	else:
		print('DB connection Error')
		return 'DB Connection Error'
	
@app.route ('/returncity/', methods = ['POST', 'GET'])
def ajax_returncity():   
	print('/returncity') 

	if request.method == 'GET':
		deptcity = request.args.get('q')
		conn = dbfunc.getConnection()
		if conn != None:    #Checking if connection is None         
			print('MySQL Connection is established')                          
			dbcursor = conn.cursor()    #Creating cursor object            
			dbcursor.execute('SELECT DISTINCT arrivCity FROM routes WHERE deptCity = %s;', (deptcity,))   
			#print('SELECT statement executed successfully.')             
			rows = dbcursor.fetchall()
			total = dbcursor.rowcount                                    
			dbcursor.close()              
			conn.close() #Connection must be closed			
			return jsonify(returncities=rows, size=total)
		else:
			print('DB connection Error')
			return jsonify(returncities='DB Connection Error')

@app.route ('/selectBooking/', methods = ['POST', 'GET'])
def selectBooking():
	if request.method == 'POST':
		#print('Select booking initiated')
		departcity = request.form['departureslist']
		arrivalcity = request.form['arrivalslist']
		outdate = request.form['outdate']
		returndate = request.form['returndate']
		adultseats = request.form['adultseats']
		childseats = request.form['childseats']
		lookupdata = [departcity, arrivalcity, outdate, returndate, adultseats, childseats]
		#print(lookupdata)
		conn = dbfunc.getConnection()
		if conn != None:    #Checking if connection is None         
			print('MySQL Connection is established')                          
			dbcursor = conn.cursor()    #Creating cursor object            
			dbcursor.execute('SELECT * FROM routes WHERE deptCity = %s AND arrivCity = %s;', (departcity, arrivalcity))   
		#	print('SELECT statement executed successfully.')             
			rows = dbcursor.fetchall()
			datarows=[]			
			for row in rows:
				data = list(row)                    
				fare = (float(row[5]) * float(adultseats)) + (float(row[5]) * 0.5 * float(childseats))
				#print(fare)
				data.append(fare)
				#print(data)
				datarows.append(data)			
			dbcursor.close()              
			conn.close() #Connection must be closed
			#print(datarows)
			#print(len(datarows))			
			return render_template('booking_start.html', resultset=datarows, lookupdata=lookupdata)
		else:
			print('DB connection Error')
			return redirect(url_for('index'))

	
@app.route ('/booking_confirm/', methods = ['POST', 'GET'])
def booking_confirm():
	if request.method == 'POST':		
		#print('booking confirm initiated')
		journeyid = request.form['bookingchoice']		
		departcity = request.form['deptcity']
		arrivalcity = request.form['arrivcity']
		outdate = request.form['outdate']
		returndate = request.form['returndate']
		adultseats = request.form['adultseats']
		childseats = request.form['childseats']
		totalfare = request.form['totalfare']
		cardnumber = request.form['cardnumber']

		totalseats = int(adultseats) + int(childseats)
		bookingdata = [journeyid, departcity, arrivalcity, outdate, returndate, adultseats, childseats, totalfare]
		#print(bookingdata)
		conn = dbfunc.getConnection()
		if conn != None:    #Checking if connection is None         
			print('MySQL Connection is established')                          
			dbcursor = conn.cursor()    #Creating cursor object     	
			dbcursor.execute('INSERT INTO bookings (deptDate, arrivDate, idRoutes, noOfSeats, totFare) VALUES \
				(%s, %s, %s, %s, %s);', (outdate, returndate, journeyid, totalseats, totalfare))   
			print('Booking statement executed successfully.')             
			conn.commit()	
			#dbcursor.execute('SELECT AUTO_INCREMENT - 1 FROM information_schema.TABLES WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s;', ('TEST_DB', 'bookings'))   
			dbcursor.execute('SELECT LAST_INSERT_ID();')
			#print('SELECT statement executed successfully.')             
			rows = dbcursor.fetchone()
			#print ('row count: ' + str(dbcursor.rowcount))
			bookingid = rows[0]
			bookingdata.append(bookingid)
			dbcursor.execute('SELECT * FROM routes WHERE idRoutes = %s;', (journeyid,))   			
			rows = dbcursor.fetchall()
			deptTime = rows[0][2]
			arrivTime = rows[0][4]
			bookingdata.append(deptTime)
			bookingdata.append(arrivTime)
			#print(bookingdata)
			#print(len(bookingdata))
			cardnumber = cardnumber[-4:-1]
			print(cardnumber)
			dbcursor.execute
			dbcursor.close()              
			conn.close() #Connection must be closed
			return render_template('booking_confirm.html', resultset=bookingdata, cardnumber=cardnumber)
		else:
			print('DB connection Error')
			return redirect(url_for('index'))

@app.route ('/dumpsVar/', methods = ['POST', 'GET'])
def dumpVar():
	if request.method == 'POST':
		result = request.form
		output = "<h2>Data Received: </h2></br>"
		output += "Number of Data Fields : " + str(len(result))
		for key in list(result.keys()):
			output = output + " </br> " + key + " : " + result.get(key)
		return output
	else:
		result = request.args
		output = "<h2>Data Received: </h2></br>"
		output += "Number of Data Fields : " + str(len(result))
		for key in list(result.keys()):
			output = output + " </br> " + key + " : " + result.get(key)
		return output  


#/register/ route registers a new user. By default user type is standard.
@app.route('/register/', methods=['POST', 'GET'])
def register():
    error = ''
    print('Register start')
    try:
        if request.method == "POST":         
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']                      
            if username != None and password != None and email != None:           
                conn = dbfunc.getConnection()
                if conn != None:    #Checking if connection is None           
                    if conn.is_connected(): #Checking if connection is established
                        print('MySQL Connection is established')                          
                        dbcursor = conn.cursor()    #Creating cursor object 
                        #here we should check if username / email already exists                                                           
                        password = sha256_crypt.hash((str(password)))           
                        Verify_Query = "SELECT * FROM users WHERE username = %s;"
                        dbcursor.execute(Verify_Query,(username,))
                        rows = dbcursor.fetchall()           
                        if dbcursor.rowcount > 0:   #this means there is a user with same name
                            print('username already taken, please choose another')
                            error = "User name already taken, please choose another"
                            return render_template("register.html", error=error)    
                        else:   #this means we can add new user             
                            dbcursor.execute("INSERT INTO users (username, password_hash, \
                                 email) VALUES (%s, %s, %s)", (username, password, email))                
                            conn.commit()  #saves data in database              
                            print("Thanks for registering!")
                            dbcursor.close()
                            conn.close()
                            gc.collect()                        
                            session['logged_in'] = True     #session variables
                            session['username'] = username
                            session['usertype'] = 'standard'   #default all users are standard
                            return render_template("success.html",\
                             message='User registered successfully and logged in..')
                    else:                        
                        print('Connection error')
                        return 'DB Connection Error'
                else:                    
                    print('Connection error')
                    return 'DB Connection Error'
            else:                
                print('empty parameters')
                return render_template("register.html", error=error)
        else:            
            return render_template("register.html", error=error)        
    except Exception as e:                
        return render_template("register.html", error=e)    
    return render_template("register.html", error=error)

#/login/ route receives user name and password and checks against db user/pw
@app.route('/login/', methods=["GET","POST"])
def login():
    form={}
    error = ''
    try:	
        if request.method == "POST":            
            username = request.form['username']
            password = request.form['password']            
            form = request.form
            print('login start 1.1')
            
            if username != None and password != None:  #check if un or pw is none          
                conn = dbfunc.getConnection()
                if conn != None:    #Checking if connection is None                    
                    if conn.is_connected(): #Checking if connection is established                        
                        print('MySQL Connection is established')                          
                        dbcursor = conn.cursor()    #Creating cursor object                                                 
                        dbcursor.execute("SELECT password_hash, usertype \
                            FROM users WHERE username = %s;", (username,))                                                
                        data = dbcursor.fetchone()
                        #print(data[0])
                        if dbcursor.rowcount < 1: #this mean no user exists                         
                            error = "User / password does not exist, login again"
                            return render_template("login.html", error=error)
                        else:                            
                            #data = dbcursor.fetchone()[0] #extracting password   
                            # verify passowrd hash and password received from user                                                             
                            if sha256_crypt.verify(request.form['password'], str(data[0])):                                
                                session['logged_in'] = True     #set session variables
                                session['username'] = request.form['username']
                                session['usertype'] = str(data[1])                          
                                print("You are now logged in")                                
                                return render_template('dashboard.html', \
                                    username=username, data='this is user specific data',\
                                         usertype=session['usertype'])
                            else:
                                error = "Invalid credentials username/password, try again."                               
                    gc.collect()
                    print('login start 1.10')
                    return render_template("login.html", form=form, error=error)
    except Exception as e:                
        error = str(e) + " <br/> Invalid credentials, try again."
        return render_template("login.html", form=form, error = error)   
    
    return render_template("login.html", form=form, error = error)
            
#https://pythonprogramming.net/decorator-wrappers-flask-tutorial-login-required/?completed=/flask-user-log-in-system-tutorial/
#Now that we can have users register and log in, we're also allowing them 
# to log out. It makes a little sense to not let users log out, unless 
# they are logged in! Here, we define the function, where the parameter is f, 
# which is convention for the fact that it wraps a function. Then, we define 
# the wrapper. 
# #Our wrapper here is simple, it just simply checks if the user 
# has a "logged_in" in their session. If so, great. If not, they should get   
# a message and a redirect to the login page.
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:            
            print("You need to login first")
            #return redirect(url_for('login', error='You need to login first'))
            return render_template('login.html', error='You need to login first')    
    return wrap

#We also write a wrapper for admin user(s). It will check with the user is 
# logged in and the usertype is admin and only then it will allow user to
# perform admin functions
def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if ('logged_in' in session) and (session['usertype'] == 'admin'):
            return f(*args, **kwargs)
        else:            
            print("You need to login first as admin user")
            #return redirect(url_for('login', error='You need to login first as admin user'))
            return render_template('login.html', error='You need to login first as admin user')    
    return wrap

#We also write a wrapper for standard user(s). It will check with the usertype is 
#standard and user is logged in, only then it will allow user to perform standard user functions
def standard_user_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if ('logged_in' in session) and (session['usertype'] == 'standard'):
            return f(*args, **kwargs)
        else:            
            print("You need to login first as standard user")
            #return redirect(url_for('login', error='You need to login first as standard user'))
            return render_template('login.html', error='You need to login first as standard user')    
    return wrap

#/logout is to log out of the system.
# Here we us @login_required wrapper ... this means that a user can only 
# log out if that user is logged in
@app.route("/logout/")
@login_required
def logout():    
    session.clear()    #clears session variables
    print("You have been logged out!")
    gc.collect()
    return render_template('mainpage.html', optionalmessage='You have been logged out')

#/userfeatures is loaded for standard users
# Here we us @standard_user_login_required wrapper ... 
# this means that only users with user type standard can access this function
# the function implements features related to standard users
@app.route('/userfeatures/')
@login_required
@standard_user_required
def user_features():
        print('fetchrecords')
        #records from database can be derived
        #user login can be checked..
        print ('Welcome ', session['username'])
        return render_template('standarduser.html', \
            user=session['username'], message='User data from app and standard \
                user features can go here....')

#/adminfeatures is loaded for admin users
# Here we us @admin_required wrapper ... 
# this means that only users with user type admin can access this function
# the function implements features related to admin users
@app.route('/adminfeatures/')
@login_required
@admin_required
def admin_features():
        print('create / amend records / delete records / generate reports')
        #records from database can be derived, updated, added, deleted
        #user login can be checked..
        print ('Welcome ', session['username'], ' as ', session['usertype'])
        return render_template('adminuser.html', user=session['username'],\
             message='Admin data from app and admin features can go here ...')

#/generateadminreport is loaded for admin users only
# Here we us @admin_required wrapper ... 
# this means that only users with user type admin can access this function
# the function implements features related to admin users
@app.route('/generateadminreport/')
@login_required
@admin_required
def generate_admin_report():
    print('admin reports')
    #here you can generate required data as per business logic
    return """
        <h1> this is admin report for {} </h1>
        <a href='/adminfeatures')> Go to Admin Features page </a>
    """.format(session['username'])

#/generateuserrecord is loaded for standard users only
# Here we us @standard_user_required wrapper ... 
# this means that only users with user type standard can access this function
# the function implements features related to standard users
@app.route('/generateuserrecord/')
@login_required
@standard_user_required
def generate_user_record():
    print('User records')
    #here you can generate required data as per business logic
    return """
        <h1> this is User record for user {} </h1>
        <a href='/userfeatures')> Go to User Features page </a>
    """.format(session['username'])
   

if __name__ == '__main__':
   app.run (debug = True)
