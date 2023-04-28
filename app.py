from flask import Flask, request, render_template, url_for, jsonify, redirect
import dbfunc, mysql.connector
from datetime import datetime

app = Flask(__name__)

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

if __name__ == '__main__':
   app.run (debug = True)
