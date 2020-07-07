# string = {"Id": 1,
#     "Name": "Ravi Kumar Singh",
#     "Department": "Data Insights",
#     "Salary": 600000,
#     "Designation": "Project Trainee"
# }
#string = {"Name":"Ravi Kumar Singh","Id":1,"Salary":600000,"Designation":"Project Te","Department":"Dara"}
fixedarr = ["Id","Name","Department","Salary","Designation"]
def check(data):
	chkarr=[]
	for i,j in zip(data,fixedarr):
		chkarr.append(i)
	
	chkarr.sort()
	fixedarr.sort()
	
	if("Id" not in chkarr):
		return False

	flag = False
	if(all(x in fixedarr for x in chkarr)):
		flag = True
	
	a=b=c=d=e=False
	if(flag):
		a=type(data["Id"])==type(1)
		b=type(data["Name"])==type("abc")
		c=type(data["Department"])==type("abc")
		d=type(data["Designation"])==type("abc")
		e=type(data["Salary"])==type(1)

	if(a and b and c and d and e and flag):
		return True
	else:
		return False


def createReturnString(data):
	string = "------------------------------------------------\n"
	for column in data:
		if(column!='_id'):
			string = string+str(column)+" = "+str(data[column])+"\n"
	string = string+"------------------------------------------------\n"
	return string

#print(check(string))