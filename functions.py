import sqlite3 as sql
import re, random, datetime, os

try:
	db = sql.connect("bulkmail.db")
	cursor = db.cursor()
except:
	messagebox.showerror("Error In Connection", "Unable to create Connection to the database")
	sys.exit(0)

capital_letters = ('A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z')
small_letters = ('a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z')
digits = (0,1,2,3,4,5,6,7,8,9)


# (F-1) this function checks whether there is any password in the app_password table or not
def password_exists():
	q = "SELECT PASSWORD FROM APP_PASSWORD"
	cursor.execute(q)
	pass_val_tuple = cursor.fetchone()
	if pass_val_tuple[0] == "NULL":
		return False
	return True


# (F-2) This Function Checks and Validates The Password While Creating The Password For The App
def pass_check(password):
    password = password.strip()
    if len(password) >= 6 and len(password) <= 20:
        if password != "NULL" or password != "null":
            return True
    else:
        return False


# (F-3) This Function Fetches the password from app_password table
def pass_fetch():
	q = "SELECT password FROM app_password"
	cursor.execute(q)
	password_data = cursor.fetchone()
	password = password_data[0]
	return password


# (F-4) This function fetches the entire data of the sender_details table
def fetch_sender_data():
	q = "SELECT * FROM sender_details"
	cursor.execute(q)
	sender_details_data = cursor.fetchall()
	return sender_details_data


# (F-5) This function checks whether the email inputted in valid or not
regex = "^\\w+([\\.-]?\\w+)*@\\w+([\\.-]?\\w+)*(\\.\\w{2,3})+$"
def valid_email(email):
	email = email.replace(" ","")
	if(re.search(regex,email)): 
		return True
	else: 
		return False


# (F-6) This function cheks whether the email exists in the sender_details table or not
def email_exists(email):
	query = "SELECT email_address FROM sender_details"
	cursor.execute(query)
	data = cursor.fetchall()
	for row in data:
		if row[0] == email.strip().replace(" ",""):
			return True
	return False


# (F-7) This function checks whether the list name by the user entered exists or not (spaces included)
def list_name_exists(list_name):
	list_name = list_name.strip().lower()
	q = "SELECT * FROM list_details"
	cursor.execute(q)
	data = cursor.fetchall()
	for i in data:
		if i[1].strip().lower() == list_name:
			return True
	return False


# (F-8) This function generates an unique random list-id for the list_details, list_emails tables
def generate_list_id():
	next_turn = 0
	def new_id():
		if next_turn == 0:
			cap = random.choice(capital_letters)
			small = random.choice(small_letters)
			letter_selected = random.choice((cap, small))
			digit_selected = random.choice(digits)
			number_selected = random.randint(digit_selected, digit_selected + random.randint(15,100))
			list_id = str(letter_selected) + str(number_selected)
			return list_id
		else:
			cap = random.choice(capital_letters)
			small = random.choice(small_letters)
			letter_selected = random.choice((cap, small))
			digit_selected = random.choice(digits)
			number_selected = random.randint(digit_selected, digit_selected + random.randint(15,100))
			number_selected += 1
			list_id = str(letter_selected) + str(number_selected)
			return list_id
	id_generated = new_id()
	q = "SELECT list_id FROM list_details"
	cursor.execute(q)
	list_id_data = cursor.fetchall()
	for row in list_id_data:
		if row[0] == id_generated:
			next_turn += 1
			id_generated = new_id()
			continue
	return id_generated


# (F-9) This Function Will Delete All The Rows From The temp_list_emails table
def delete_temp_data():
	q = "DELETE FROM temp_list_emails"
	cursor.execute(q)
	db.commit()


# (F-10) This Function Checks Whether The temp_list_emails table is empty or not
def is_temp_empty():
	q = "SELECT * FROM temp_list_emails"
	cursor.execute(q)
	data = cursor.fetchall()
	if len(data) == 0:
		return True
	return False


# (F-11) This Function Returns The ID Of The Email List By Taking The Name Of The Email List
def get_list_id(list_name):
	list_id = str()
	list_name = list_name.strip()
	q = "SELECT * FROM list_details"
	cursor.execute(q)
	email_list_data = cursor.fetchall()
	for row in email_list_data:
		if row[1] == list_name:
			list_id = row[0]
	return list_id


# (F-12) This function will get all the list names which have emails, i.e this is a filter function for OptionMenu
def get_me_list_names():
	block_list_ids = []
	q = "SELECT list_id FROM list_details"
	cursor.execute(q)
	list_ids_data = cursor.fetchall()
	for i in list_ids_data:
		q1 = "SELECT * FROM list_emails WHERE list_id = '{}'".format(i[0])
		cursor.execute(q1)
		email_data = cursor.fetchall()
		if len(email_data) == 0:
			block_list_ids.append(i[0])
	not_empty_list_names = []
	q2 = "SELECT list_id, list_name FROM list_details"
	cursor.execute(q2)
	data = cursor.fetchall()
	for i in data:
		if i[0] in block_list_ids:
			num = 0 
		else:
			not_empty_list_names.append(i[1])			
	return not_empty_list_names

# (F-13) This function checks whether any email list with emails in it exists or not in the database
def yes_email_list():
	q = "SELECT list_id FROM list_details"
	cursor.execute(q)
	data = cursor.fetchall()
	if len(data) == 0:
		return False
	for i in data:
		q = "SELECT email_address FROM list_emails WHERE list_id = '{}'".format(i[0])
		cursor.execute(q)
		email_data = cursor.fetchall()
		if len(email_data) > 0:
			return True
	return False

# (F-14) This function will return a list all the sender emails created by the user
def get_me_sender_emails():
	sender_emails = []
	q = "SELECT email_address FROM sender_details"
	cursor.execute(q)
	sender_emails_data = cursor.fetchall()
	for i in sender_emails_data:
		sender_emails.append(i[0])
	return sender_emails

# (F-15) This function will check whether or not the user has set up any sender email or not
def yes_sender_email():
	q = "SELECT * FROM sender_details"
	cursor.execute(q)
	sender_data = cursor.fetchall()
	if len(sender_data) == 0:
		return False
	return True

# (F-16) This function will generate an unique mail_id for every new DRAFT
def unique_mail_id_generator():
	next_turn = 0
	def new_id():
		if next_turn == 0:
			cap = random.choice(capital_letters)
			small = random.choice(small_letters)
			letter_selected = random.choice((cap, small))
			digit_selected = random.choice(digits)
			number_selected = random.randint(digit_selected, digit_selected + random.randint(15,100))
			mail_id = str(number_selected) + str(letter_selected) 
			return mail_id
		else:
			cap = random.choice(capital_letters)
			small = random.choice(small_letters)
			letter_selected = random.choice((cap, small))
			digit_selected = random.choice(digits)
			number_selected = random.randint(digit_selected, digit_selected + random.randint(15,100))
			number_selected += 1
			mail_id = str(number_selected) + str(letter_selected) 
			return mail_id
	id_generated = new_id()
	q = "SELECT mail_id FROM mail_details"
	cursor.execute(q)
	list_id_data = cursor.fetchall()
	for row in list_id_data:
		if row[0] == id_generated:
			next_turn += 1
			id_generated = new_id()
			continue
	return id_generated


# (F-17) This function takes the sender email and returns the password of that sender email
def get_email_password(sender_email):
	sender_email_password = str()
	q = "SELECT email_address, email_password FROM sender_details"
	cursor.execute(q)
	data = cursor.fetchall()
	for row in data:
		if sender_email == row[0]:
			sender_email_password = row[1]
	return sender_email_password

# (F-18) This function takes the sender email and returns the smtp address of that sender email
def get_email_smtp_address(sender_email):
	sender_email_smtp_address = str()
	q = "SELECT email_address, smtp_address FROM sender_details"
	cursor.execute(q)
	data = cursor.fetchall()
	for row in data:
		if sender_email == row[0]:
			sender_email_smtp_address = row[1]
	return sender_email_smtp_address

# (F-19) This function takes the sender email and returns the port number of that sender email
def get_email_port_number(sender_email):
	sender_email_port_number = str()
	q = "SELECT email_address, port_number FROM sender_details"
	cursor.execute(q)
	data = cursor.fetchall()
	for row in data:
		if sender_email == row[0]:
			sender_email_port_number = row[1]
	return sender_email_port_number

# (F-20) This function takes the list_id and returns the "list of emails" of that list_id
def get_list_of_emails(list_id):
	q = "SELECT email_address FROM list_emails WHERE list_id='{}'".format(list_id)
	cursor.execute(q)
	data = cursor.fetchall()
	return [i[0] for i in data]

# (F-21) This function returns the current date in the sql format to be inserted into a table
def get_curdate():
	date = datetime.datetime.now()
	day, month, year = date.day, date.month, date.year
	if len(str(day).strip()) == 1:
		day = "0"+str(day)
	if len(str(month).strip()) == 1:
		month = "0"+str(month)
	curdate = f"{year}/{month}/{day}"
	return curdate

# (F-22) This function returns an unique name for the text file in which the message contents is going to be stored
def unique_msg_loc_maker():
	default_name = "msg.txt"
	i = 1
	while True:
		if os.path.exists(f"C:\\BulkMail\\drafts\\msg{i}.txt") == True:
			i += 1
		else:
			open(f"C:\\BulkMail\\drafts\\msg{i}.txt", "a").close()
			filename = f"msg{i}.txt"
			break
	return filename

# # (F-23) This function checks whether the software have created the BulkMail\drafts or Not FROM a temp table
# def created():
# 	q = "SELECT field FROM temp"
# 	cursor.execute(q)
# 	data = cursor.fetchall()
# 	if len(data) == 0:
# 		return False

# # (F-24) This function inserts TRUE into the temp table, after the software has created its own Directory Structure
# def create():
# 	q = "INSERT INTO temp VALUES('{}')".format("TRUE")
# 	cursor.execute(q)
# 	db.commit()

# (F-23) This function will take mail_id and will return their respective Subject Line
def get_subject_line_to_edit(mail_id):
	subject_line_to_edit = str()
	q = "SELECT mail_id, subject_line FROM mail_details"
	cursor.execute(q)
	data = cursor.fetchall()
	for row in data:
		if row[0] == mail_id:
			subject_line_to_edit = row[1]
	return subject_line_to_edit

# (F-24) This function will take mail_id and will return their respective Message Location
def get_msg_loc_to_edit(mail_id):
	msg_loc_to_edit = str()
	q = "SELECT mail_id, msg_loc FROM mail_details"
	cursor.execute(q)
	data = cursor.fetchall()
	for row in data:
		if row[0] == mail_id:
			msg_loc_to_edit = row[1]
	return msg_loc_to_edit

db.commit()
