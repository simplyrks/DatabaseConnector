#Program for MYSQL
from flask import Flask, render_template, url_for, request, redirect
import mysql.connector
from functions import check, createReturnString
import datetime
import re
import pymongo
import json
connection = mysql.connector.connect(host='localhost',
                                     database='employee',
                                    user='root',
                                     password='password')

# Connection TO MongoDB
client = pymongo.MongoClient(
   "MONGODB Conection String with collection name Employee having attributes sam eas MYSQL table")
db = client.employee
cursor = connection.cursor();

StringDataTypes = ['char','varchar','binary','varbinary','tinyblob','tinytext','text','blob','mediumtext','mediumblob','longtext','longblob']
NumericDataTypes = ['bit','tinyint','bool','boolean','smallint','mediumint','int','integer','bigint','float','double','double precision','decimal','dec']
DateDataTypes = ['date','datetime','timestamp','time','year']
app = Flask(__name__)
rows=[]
cursor = connection.cursor();
field_names = []
queryinput =""

@app.route('/post', methods = ['POST'])
def postdata():
	global cursor
	if request.method == 'POST':
		try:
			data = request.get_json(force = True)
		except Exception as e:
			return"Enter correctly formatted json\n"
		if(check(data)):
			db.employee.insert_one(data)#insertion top mongodb
			id1=data["Id"]
			name=data["Name"]
			dept=data["Department"]
			des=data["Designation"]
			sal=data["Salary"]
			try:

				cursor.execute("insert into employee values(%s,%s,%s,%s,%s)",(id1,name,dept,sal,des,))
				connection.commit()
			except Exception as err:
				print(err)
				deldict = {}
				deldict["Id"] = id1
				db.employee.delete_one(deldict)
				return str(err)+"\n"
			return "Pushed Data succesfully\n"
		else:
			return "Enter data related to the employee collection\n"
@app.route('/help')
def help():
	string = "--------------------------------------------\n"
	string1 = "Use these templates to insert or update\n--------------------------------------------\n"

	string2 = "For Insterting into the collection use this json format:-\n"
	string3 = "{\n  \"Name\":\"Your Name\",\n  \"Id\":your Id in numerals,\n  \"Salary\":your salary in numerals,\n  \"Designation\":\"Your Designation\",\n  \"Department\":\"Your Department\"\n}\n"
	string4 = "For Updating a document in the collection use this format:-\n"
	string5 = "[{\n  \"Id\": the id you want to edit or any other condition},\n  {\n    \"$set\": {\n      \"Name\":\"Your Name\",\n      \"Id\":your Id in numerals,\n      \"Salary\":your salary in numerals,\n      \"Designation\":\"Your Designation\",\n      \"Department\":\"Your Department\"\n    }\n  }]\n"

	return string+string1+string2+string3+string4+string5

@app.route('/getall')
def getalldata():
	global db
	returnString="---------------------------------------------------------------------------------\n"
	for row in db.employee.find():
		string = createReturnString(row)
		returnString = returnString+string
	return returnString

@app.route('/get',methods = ['POST'])
def getdata():
	global db
	returnString="---------------------------------------------------------------------------------\n"
	if request.method=='POST':
		data = request.get_json(force = True)
		for row in db.employee.find(data):
			string = createReturnString(row)
			returnString = returnString+string

	return returnString

@app.route('/', methods = ['GET','POST'])
def query():
	global rows
	global queryinput
	global cursor 
	global field_names
	cursor.execute("select Sno from history order by Sno desc limit 1;")
	m = cursor.fetchall()
	try:
		sno = int(m[0][0])
	except:
		sno=0

	if request.method =='POST':	
		queryinput = request.form['query']
		flaginsup=0
		if queryinput!='':	 
			try:
				print(queryinput.split())
				if "history;" in queryinput.split() or "history" in queryinput.split():
					return redirect('/history')

				if "update" in queryinput.lower().split():
					flaginsup=1
					chkforinsupd = "upd"

				if "insert" in queryinput.lower().split():
					flaginsup=1
					chkforinsupd = "ins"
					if queryinput.lower().split()[2] == "employee":
						print("Mai kya karu raam mera prgram ni chal ra")
						return redirect('/insert')
						print("fuck off")
				cursor.execute(queryinput)
				if(flaginsup==0):
					num_fields = len(cursor.description)
					field_names = [i[0].lower() for i in cursor.description]
					rows = cursor.fetchall()
				else:
					rows=None
					field_names = None
				x = datetime.datetime.now()
				x1 = x.strftime("%Y-%m-%d %H:%M:%S")
				print(x1)
				sno = sno+1
				print(queryinput)
				print("____________________________done__________________________________________")
				cursor.execute("select Sno from history where query = %s",(queryinput,))
				print("++++++++++++++++++++++++++++done++++++++++++++++++++++++++++++++++++++++++")
				querylist = cursor.fetchall()
				try:
					print(querylist[0][0])
					print("update history SET date = "+"STR_TO_DATE('"+str(x1)+"','%Y-%m-%d %H:%i:%s') where Sno = "+str(querylist[0][0])+";")
					cursor.execute("update history SET date = "+"STR_TO_DATE('"+str(x1)+"','%Y-%m-%d %H:%i:%s') where Sno = "+str(querylist[0][0])+";")
				except Exception as err:
					#queryhis = "insert into history values(?,?,?)",(str(sno),x1,queryinput)
					print("*****************************************done*********************************************")
					print(cursor.execute("insert into history values(%s,%s,%s)",(sno,x1,queryinput,)))
					print("*****************************************done*********************************************")
				connection.commit()
				if "dual;" in queryinput.split() or "dual" in queryinput.split():
					showbutton = False
				else:
					showbutton = True

				if(rows!=None):
					return render_template('index.html',rows = rows, names=field_names,default=queryinput, showbutton= showbutton)
				else:
					if(chkforinsupd=="upd"):
						return render_template('index.html',error ="DataBase Updated")
					if(chkforinsupd=="ins"):
						return render_template('index.html',error="Data Inserted into Table")
			except Exception as e:
				return render_template('index.html',error = e, default = queryinput)
	return render_template('index.html',error = 'Data not available to display, run a query')	

@app.route('/history',methods = ['GET','POST'])
def history():
	global rows
	global field_names
	cursor = connection.cursor();
	cursor.execute("select Sno, date, query from history order by date desc ;")
	num_fields = len(cursor.description)
	field_names = [i[0].lower() for i in cursor.description]
	rows = cursor.fetchall()
	return render_template('index.html',rowshis = rows, name=field_names, DisHistory = "History")
	if request.method =='POST':
		print("Entred")
		queryinput = request.form['query']
		retval = queryresult()
		if retval == 1:
			return render_template('index.html',rows = rows, names=field_names,default=queryinput)
		else:
			return render_template('index.html', error = e, default = queryinput)	


@app.route('/history/<int:Sno>')
def delete(Sno):
	global rows
	global field_names
	global queryinput
	insertupdatechk=1
	x = datetime.datetime.now()
	x1 = x.strftime("%Y-%m-%d %H:%M:%S")
	cursor = connection.cursor();
	cursor.execute("select Query from history where Sno = "+str(Sno)+";")
	hisQuery = cursor.fetchall()
	print(hisQuery)
	queryinput = hisQuery[0][0]
	if "history;" in queryinput.split() or "history" in queryinput.split():
		return redirect('/history')
	if "update" in queryinput.lower().split() or "insert" in queryinput.lower().split():
		insertupdatechk=0
	cursor.execute(queryinput)
	if(insertupdatechk==1):
		rows = cursor.fetchall()
		num_fields = len(cursor.description)
		field_names = [i[0].lower() for i in cursor.description]

	if "dual;" in queryinput.split() or "dual" in queryinput.split():
		showbutton= False
	else:
		showbutton= True
	
	cursor.execute("select Sno from history where query = \""+hisQuery[0][0]+"\"")
	querylist = cursor.fetchall()
	cursor.execute("update history SET date = "+"STR_TO_DATE('"+str(x1)+"','%Y-%m-%d %H:%i:%s') where Sno = "+str(querylist[0][0])+";")
	if(insertupdatechk==1):
		return render_template('index.html',rows = rows, names=field_names, default = hisQuery[0][0], showbutton= showbutton)
	else:
		return render_template('index.html',error="Done")

@app.route('/history/edit/<int:Sno>')
def edit(Sno):
	cursor = connection.cursor();
	cursor.execute("select Query from history where Sno = "+str(Sno)+";")
	hisQuery = cursor.fetchall()
	return render_template('index.html', default = hisQuery[0][0])

@app.route('/insert', methods=['POST','GET'])
def insert():
	global cursor
	global connection
	if request.method =='POST':	
		Id = request.form['Id']
		Name = request.form['Name']
		Salary = request.form['Salary']
		Department = request.form['Department']
		Designation = request.form['Designation']
		errmsg = ""
		flagofnumericchk=0
		Id = re.sub(' +', ' ', Id)
		Name = re.sub(' +', ' ', Name)
		Salary = re.sub(' +', ' ', Salary)
		Designation = re.sub(' +', ' ', Designation)
		Department = re.sub(' +', ' ', Department)
		if(Id=="" or Id==" "):
			return render_template('index.html',error ="Id cannot be empty")
		if(Id.isnumeric()== False):
			flagofnumericchk = 1
			errmsg = "Id Must be numeric and "
		if(Salary.isnumeric()==False and (Salary!="" or Salary!=" ")):
			if(Salary!=""):
				flagofnumericchk =1
				errmsg = errmsg+"Salary must be numeric and "



		if(flagofnumericchk==1):
			errmsg = errmsg[:-4]
			return render_template('index.html',error = errmsg)
		
		

		QueryInsert1 = "Insert into employee ( Id"
		QueryInsert2 = ") Values("+str(Id)
		if(Name!="" and Name!=" "):
			QueryInsert1 = QueryInsert1+",Name "
			QueryInsert2 = QueryInsert2+", \""+Name+"\""
		if(Salary!="" and Salary!=" "):
			QueryInsert1 = QueryInsert1+",Salary "
			QueryInsert2 = QueryInsert2+", "+Salary
		if(Designation!="" and Designation!=" "):
			QueryInsert1 = QueryInsert1+",Designation "
			QueryInsert2 = QueryInsert2+", \""+Designation+"\""
		if(Department!="" and Department!=" "):
			QueryInsert1 = QueryInsert1+",Department "
			QueryInsert2 = QueryInsert2+", \""+Department+"\"" 

		QueryInsert =  QueryInsert1+QueryInsert2+")"


		Data = "{\"Id\": "+Id+",\"Name\": \""+Name+"\",\"Department\": \""+Department+"\",\"Salary\":"+Salary+",\"Designation\": \""+Designation+"\"}"
		print(Data)
		try:
			cursor.execute(QueryInsert)
		except Exception as e:
			return render_template('index.html',error = e)
		try:
			db.employee.insert_one(json.loads(Data))
		except Exception as e:
			return render_template('index.html',error = e)
		connection.commit()


		

		print(Id,Name,Salary,Department,Designation)
		return render_template('index.html',error = "Data has been Inserted")
	return render_template('index.html',insertbutton=True)
	

@app.route('/update', methods = ['GET','POST'])
def update():
	global queryinput
	global rows
	global cursor
	global field_names
	i = 0
	newtable=[]
	flag=0
	iflag=0
	newtable=list(newtable)
	oldtable =[]
	oldtable = list(oldtable)
	if request.method=='POST':
		length = len(rows)*len(rows[0])
		for data in rows:
			newrow = []
			newrow = list(newrow)
			oldrow = []
			oldrow = list(newrow)
			for j in data:
				updateData = request.form['update['+str(i)+']']
				newrow.append(updateData)
				oldrow.append(str(j))
				if(str(j)!=str(updateData)):
					flag = 1
					iflag = 1
				i=i+1
			if(iflag==1):
				newtable.append(newrow)
				oldtable.append(oldrow)
			iflag = 0

		if(flag==1):
			flagofemployee=False
			#print("false")
			queryinput = queryinput.lower()
			litable = queryinput.split(" ")
			print("litable ="+str( litable))
			for i in range(len(litable)):
				if litable[i]=="from":
					tablename = litable[i+1]
			if tablename[len(tablename)-1]==";":
				tablename = tablename[:-1]
			print("Table Name = "+tablename)
			if(tablename.lower()=="employee"):
				print(";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;")
				flagofemployee=True
			print(flagofemployee)
			print(";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;")
			cursor.execute("SELECT GROUP_CONCAT(COLUMN_NAME)FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA = 'employee' AND CONSTRAINT_NAME='PRIMARY'AND TABLE_NAME = '"+tablename+"'GROUP BY TABLE_NAME;")
			pk = cursor.fetchall()
			if len(pk[0])>1:
				return render_template('index.html',error = 'Not capable of updating database with multiple primary key')
			primarykey = pk[0][0]
			dtypequery = "SELECT COLUMN_NAME,DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = '"+tablename+"' AND COLUMN_NAME IN ("
			for jk in field_names:
				dtypequery = dtypequery+"\""+jk+"\","
			dtypequery = dtypequery[:-1]
			# print(dtypequery+");")
			cursor.execute(dtypequery+");")
			datatype = cursor.fetchall()
			# print(datatype)
			stringdata=[]
			intdata=[]
			datedata = []
			for kl in datatype:
			    if kl[1].decode("utf-8") in StringDataTypes:
			        stringdata.append(kl[0].lower())
			    if kl[1].decode("utf-8") in NumericDataTypes:
			        intdata.append(kl[0].lower())
			    if kl[1].decode("utf-8") in DateDataTypes:
			        datedata.append(kl[0].lower())


			
			if primarykey.lower() in field_names:
				for line,oldline in zip(newtable,oldtable):
					queryupdate = "UPDATE "+tablename+" SET "
					dpk = {}
					duitems={}
					for COLUMN_NAME,data1 in zip(field_names,line):
						if "\"" in data1:
							return render_template('index.html',error="My sql doesnot excepts double quotes (\")")
						if COLUMN_NAME in stringdata:
							queryupdate = queryupdate+COLUMN_NAME+" = \""+data1+"\","
							if(flagofemployee):
								duitems[COLUMN_NAME.capitalize()]=data1
							#queryupdatemdb = queryupdatemdb+"\""+COLUMN_NAME.capitalize()+"\":\""+data1+"\","
						if COLUMN_NAME in intdata:
							queryupdate = queryupdate+COLUMN_NAME+" = "+data1+","
							if(flagofemployee):
								duitems[COLUMN_NAME.capitalize()]=int(data1)
							#queryupdatemdb = queryupdatemdb+"\""+COLUMN_NAME.capitalize()+"\":"+data1+","
						if COLUMN_NAME in datedata:
							queryupdate = queryupdate+COLUMN_NAME+" = STR_TO_DATE('"+data1+"','%Y-%m-%d %H:%i:%s'),"
					queryupdate = queryupdate[:-1]
					UpdateQuery = queryupdate+" WHERE "+primarykey+" = "+oldline[field_names.index(primarykey.lower())]+";"
					#updatepkmdb = "{\""+primarykey+"\":"+oldline[field_names.index(primarykey.lower())]+"}"
					if(flagofemployee):
						dpk[primarykey] = int(oldline[field_names.index(primarykey.lower())])
						updateitemsd={}
						updateitemsd["$set"] = duitems
					#print(updatepkmdb,queryupdatemdb+"}")
					#print(UpdateQuery.split(" "))
					#print(queryupdate+" WHERE "+primarykey+" = "+oldline[field_names.index(primarykey.lower())]+";")
					try:
						print(intdata, primarykey)
						print(flagofemployee)
						if primarykey.lower() in intdata:
							print("Inside int data")
							cursor.execute(queryupdate+" WHERE "+primarykey+" = "+oldline[field_names.index(primarykey.lower())]+";")
						if primarykey.lower() in stringdata:
							print("Inside String data")
							cursor.execute(queryupdate+" WHERE "+primarykey+" = \""+oldline[field_names.index(primarykey.lower())]+"\";")
						
					except Exception as e:
						return render_template('index.html',error= e)
					if(flagofemployee):	
						try:
							print(dpk,updateitemsd)
							xreturn = db.employee.update_many(dpk,updateitemsd)
							print("Updated both places")
							print(xreturn)
							connection.commit()
						except Exception as e:
							return render_template('index.html',error=e)
					else:
						connection.commit()


			else:
				return render_template('index.html',error = 'Not capable of updating database without primary key')

				
		else:
			print("True")
		if(flag == 1):

			return render_template('index.html',error = 'Data Base Updated')
		else:
			return render_template('index.html',error = 'Nothing to Upadte')

	return render_template('index.html', error = 'Run a query')

@app.route('/updatebymongo',methods = ['POST','GET'])
def updatebymongo():
	global db
	global cursor
	global connection
	if request.method == 'POST':
		print("Data requested")
		data = request.get_json(force = True)
		print("Inititated data receive")
		print(data)
		try:
			for i in data[0]:
				wherestring = " where "+str(i)+" = "+str(data[0][i])
				#print(wherestring)

			setstring = "Update employee set "
			print("_________________________")
			for i in data[1]["$set"]:

				if(type(data[1]["$set"][i])==type("abc")):
					setstring = setstring + str(i)+" = \""+str(data[1]["$set"][i])+"\", "
				if(type(data[1]["$set"][i])==type(1)):
					setstring = setstring + str(i)+" = "+str(data[1]["$set"][i])+", "
				print("*************************")

			print("Setstring = "+setstring)
			setstring = setstring[:-2]
			Query = setstring+" "+wherestring
			print(Query)
			cursor.execute(Query)
			connection.commit()
			print(data[0],data[1])
			db.employee.update_many(data[0],data[1])
			return "Collection Employee Updated.\n"
		except Exception as e:
			print(e)
			return"Failed to update Collection Employee.\n"


if __name__ == '__main__':
	app.run(debug=True)