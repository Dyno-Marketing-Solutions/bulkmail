from tkinter import *
from tkinter import messagebox
import os, sys, smtplib, shutil 
import sqlite3 as sql
from email.message import EmailMessage
import functions as func

## LOG-LINE
## BulkMail V1 is a simple lightweight software for sending HTML Emails in BULK

NAME = "[name]" ## Will Work On It In V2
CSV = "Uploading CSV Based Email Lists" ## Will Work On It In V2

### Pre Validation Code Starts Here (STILL REMAINING) ###
try:
	if os.path.exists("C:\\"):
		print("GO")
except:
	messagebox.showerror("Unsupported System", "This Appliaction Is Unsupported For Your System")
	sys.exit(0)
if os.path.exists("C:\\BulkMail\\drafts") == True:
	print("MADE")
else:
	try:
		os.makedirs("C:\\BulkMail\\drafts")
	except:
		messagebox.showerror("Folder Error", "Please Delete The Folder Named BulkMail In Your C Drive")
		sys.exit(0)
try:
	with open("bulkmail.db", "rb") as f:
		f.read()
except:
	messagebox.showerror("Error In Connection", "Unable to create Connection to the database")
	sys.exit(0)		 
try:
	db = sql.connect("bulkmail.db")
	cursor = db.cursor()
except:
	messagebox.showerror("Error In Connection", "Unable to create Connection to the database")
	sys.exit(0)
func.delete_temp_data()
### Pre Validation Code Ends Here ###


## This function is responsible for filtering whether to send emails singly or in bulk
def send_emails_home(mail_id):
	if func.yes_email_list() == False:
		messagebox.showinfo("No Email List", "You Do Not Have Any Email List With Emails")
		return
	if func.yes_sender_email() == False:
		messagebox.showinfo("No Sender Email", "Please Set Up A Sender Email To Start Sending Emails")
		return

	## This function will save Email Data in the mail_details table as a Draft
	def save_as_draft(mail_id=None):
		if mail_id == None:
			try:
				msg_content = msg_box_text.get("1.0", END)
				subject_line = subject_line_entry.get()
				if subject_line.strip() == "":
					messagebox.showinfo("Subject Line Empty", "The Draft Cannot Be Saved With An Empty Subject Line")
					return
				if msg_content.strip() == "":
					messagebox.showinfo("Message Box Empty", "The Draft Cannot Be Saved For An Empty Message Box")
					return
				date_edited = func.get_curdate()
				mail_id = func.unique_mail_id_generator()
				list_id = func.get_list_id(list_name_to_send.get())
				sender_email = sender_email_to_send.get()
				msg_filename = func.unique_msg_loc_maker()
				with open(f"C:\\BulkMail\\drafts\\{msg_filename}", "w") as f:
					f.write(msg_content)
				msg_loc = f"C:\\BulkMail\\drafts\\{msg_filename}"
				q = "INSERT INTO mail_details VALUES('{}','{}','{}','{}','{}','{}')".format(date_edited, mail_id, list_id, subject_line, sender_email, msg_loc)
				cursor.execute(q)
				db.commit()
				subject_line_entry.delete(0, END)
				msg_box_text.delete("1.0", END)
				messagebox.showinfo("Draft Saved", "The Email Data Have Been Successfully Saved As A Draft")
				return
			except:
				messagebox.showerror("Draft Error", "Unable To Save The Email As A Draft")
				return
		else:
			try:
				msg_loc_to_edit = func.get_msg_loc_to_edit(mail_id_to_edit)
				subject_line = draft_subject_line_entry.get().strip()
				new_msg_content = draft_msg_box_text.get("1.0",END)
				with open(msg_loc_to_edit, "w") as f:
					f.write(new_msg_content)
				q = "UPDATE mail_details SET subject_line='{}' WHERE mail_id='{}'".format(subject_line, mail_id_to_edit)
				cursor.execute(q)
				db.commit()
				draft_send_emails_root.destroy()
				drafted_emails_layout()
				return
			except:
				messagebox.showinfo("Draft Error", "Unable To Save The Message As A Draft")
				return

	## This function will send the mail, both for NON-DRAFT and DRAFT mails
	## After a DRAFT mail is sent this function is also responsible for deleting the associated data for that DRAFT
	def send_mail(mail_id=None):
		if mail_id == None:
			sender_email = sender_email_to_send.get()
			sender_email_password = func.get_email_password(sender_email)
			sender_email_smtp_address = func.get_email_smtp_address(sender_email)
			sender_email_port_number = func.get_email_port_number(sender_email)
			list_of_emails = func.get_list_of_emails(func.get_list_id(list_name_to_send.get()))
			subject_line = subject_line_entry.get().strip()
			msg_content = msg_box_text.get("1.0",END)
			msg_html = f"""
				<html>
					<body>
						{msg_content}
					</body>
				</html>
			"""
			for email in list_of_emails:
				try:				
					with smtplib.SMTP(sender_email_smtp_address, sender_email_port_number) as smtp:
						smtp.ehlo()
						smtp.starttls()
						smtp.ehlo()
						smtp.login(sender_email, sender_email_password)
						msg = EmailMessage()
						msg["Subject"] = subject_line
						msg["From"] = sender_email
						msg["To"] = email
						msg.add_alternative(msg_html, subtype='html')
						smtp.send_message(msg)
				except:
					messagebox.showerror("Email Send Error", "There Is A Error In Sending The Emails")
					return
			subject_line_entry.delete(0, END)
			msg_box_text.delete("1.0", END)
			messagebox.showinfo("Emails Sent", "All Emails Have Been Sent Successfully")
			return
		else:
			sender_email = draft_sender_email_to_send.get()
			sender_email_password = func.get_email_password(sender_email)
			sender_email_smtp_address = func.get_email_smtp_address(sender_email)
			sender_email_port_number = func.get_email_port_number(sender_email)
			list_of_emails = func.get_list_of_emails(func.get_list_id(draft_list_name_to_send.get()))
			subject_line = draft_subject_line_entry.get().strip()
			msg_content = draft_msg_box_text.get("1.0",END)
			msg_html = f"""
				<html>
					<body>
						{msg_content}
					</body>
				</html>
			"""
			for email in list_of_emails:
				try:				
					with smtplib.SMTP(sender_email_smtp_address, sender_email_port_number) as smtp:
						smtp.ehlo()
						smtp.starttls()
						smtp.ehlo()
						smtp.login(sender_email, sender_email_password)
						msg = EmailMessage()
						msg["Subject"] = subject_line
						msg["From"] = sender_email
						msg["To"] = email
						msg.add_alternative(msg_html, subtype='html')
						smtp.send_message(msg)
				except:
					messagebox.showerror("Email Send Error", "There Is A Error In Sending The Emails")
					return
			q = "DELETE FROM mail_details WHERE mail_id='{}'".format(mail_id_to_edit)
			cursor.execute(q)
			db.commit()
			draft_subject_line_entry.delete(0, END)
			draft_msg_box_text.delete("1.0", END)
			messagebox.showinfo("Emails Sent", "All Emails Have Been Sent Successfully")
			draft_send_emails_root.destroy()
			drafted_emails_layout()
			return

	email_list_names = func.get_me_list_names()
	sender_emails = func.get_me_sender_emails()

	try:
		root.destroy()
	except:
		pass
	try:
		email_lists_root.destroy()
	except:
		pass
	try:
		drafted_emails_root.destroy()
	except:
		pass

	if mail_id == None:
		global send_emails_root
		send_emails_root = Tk()
		send_emails_root.geometry("905x620")
		send_emails_root.resizable(0,0)
		send_emails_root.title("SEND EMAILS")
		send_emails_root.iconbitmap("./icons/ico-files/icon-16.ico")
		send_emails_root.configure(background="#D1FFFF")
		menubar = Menu(send_emails_root)
		send_emails_root.config(menu=menubar)
		submenu1 = Menu(menubar, tearoff=0)
		menubar.add_cascade(label="Navigate", menu=submenu1)
		submenu1.add_command(label="Email Lists", command=email_lists_layout)
		submenu1.add_command(label="Drafted Emails", command=drafted_emails_layout)
		back_btn = Button(send_emails_root, text="<<", border=5, font="comicsansms 12 bold", fg='black', bg='pink', command=home_layout)
		back_btn.place(x=5,y=5)
		Label(send_emails_root, text="SEND EMAILS", font="comicsansms 20 bold", bg="#D1FFFF").place(x=350, y=0)
		Label(send_emails_root, text="SELECT LIST : ", font="comicsansms 18 bold", bg="#D1FFFF").place(x=20, y=60)
		Label(send_emails_root, text="SELECT SENDER EMAIL : ", font="comicsansms 18 bold", bg="#D1FFFF").place(x=20, y=105)
		
		global list_name_to_send
		list_name_to_send = StringVar(send_emails_root)
		list_name_to_send.set(email_list_names[0]) ## setting a default to avoid any error
		options = OptionMenu(send_emails_root, list_name_to_send, *email_list_names).place(x=200, y=60)

		global sender_email_to_send 
		sender_email_to_send = StringVar(send_emails_root)
		sender_email_to_send.set(sender_emails[0]) ## setting a default to avoid any error
		options = OptionMenu(send_emails_root, sender_email_to_send, *sender_emails).place(x=330, y=105)

		global subject_line_entry
		subject_line_entry = Entry(send_emails_root, font="comicsansms 18 bold", width=66, border=4)
		subject_line_entry.place(x=20, y=150)
		subject_line_entry.insert(0, " ENTER YOUR SUBJECT LINE HERE ")

		global msg_box_text
		msg_box_text = Text(send_emails_root, font="comicsansms 15 bold", height=12, width=78, border=4)
		msg_box_text.place(x=20, y=200)
		msg_box_text.insert(END, " TYPE YOUR EMAIL MESSAGE HERE")

		send_email_btn = Button(send_emails_root, text="SEND EMAIL", border=10, font="comicsansms 18 bold", fg='black', bg='pink', padx=20, command=send_mail)
		send_email_btn.place(x=120, y=516)
		save_as_draft_btn = Button(send_emails_root, text="SAVE AS DRAFT", border=10, font="comicsansms 18 bold", fg='black', bg='pink', command=save_as_draft).place(x=550, y=516)
		
		send_emails_root.mainloop()
	
	else:
		try:
			subject_line_to_edit = func.get_subject_line_to_edit(mail_id_to_edit)
			msg_loc_to_edit = func.get_msg_loc_to_edit(mail_id_to_edit)
			with open(msg_loc_to_edit, "r") as f:
				msg_content_to_edit = f.read()
			global draft_send_emails_root
			draft_send_emails_root = Tk()
			draft_send_emails_root.geometry("905x620")
			draft_send_emails_root.resizable(0,0)
			draft_send_emails_root.title("SEND EMAILS")
			draft_send_emails_root.iconbitmap("./icons/ico-files/icon-16.ico")
			draft_send_emails_root.configure(background="#D1FFFF")

			back_btn = Button(draft_send_emails_root, text="<<", border=5, font="comicsansms 12 bold", fg='black', bg='pink', command=drafted_emails_layout)
			back_btn.place(x=5,y=5)

			Label(draft_send_emails_root, text="SEND EMAILS", font="comicsansms 20 bold", bg="#D1FFFF").place(x=350, y=0)
			Label(draft_send_emails_root, text="SELECT LIST : ", font="comicsansms 18 bold", bg="#D1FFFF").place(x=20, y=60)
			Label(draft_send_emails_root, text="SELECT SENDER EMAIL : ", font="comicsansms 18 bold", bg="#D1FFFF").place(x=20, y=105)

			global draft_list_name_to_send
			draft_list_name_to_send = StringVar(draft_send_emails_root)
			draft_list_name_to_send.set(email_list_names[0]) 
			options = OptionMenu(draft_send_emails_root, draft_list_name_to_send, *email_list_names).place(x=200, y=60)

			global draft_sender_email_to_send 
			draft_sender_email_to_send = StringVar(draft_send_emails_root)
			draft_sender_email_to_send.set(sender_emails[0]) 
			options = OptionMenu(draft_send_emails_root, draft_sender_email_to_send, *sender_emails).place(x=330, y=105)

			global draft_subject_line_entry
			draft_subject_line_entry = Entry(draft_send_emails_root, font="comicsansms 18 bold", width=66, border=4)
			draft_subject_line_entry.place(x=20, y=150)
			draft_subject_line_entry.insert(0, subject_line_to_edit)

			global draft_msg_box_text
			draft_msg_box_text = Text(draft_send_emails_root, font="comicsansms 15 bold", height=12, width=78, border=4)
			draft_msg_box_text.place(x=20, y=200)
			draft_msg_box_text.insert(END, msg_content_to_edit)

			send_email_btn = Button(draft_send_emails_root, text="SEND EMAIL", border=10, font="comicsansms 18 bold", fg='black', bg='pink', padx=20, command=lambda: send_mail(mail_id_to_edit))
			send_email_btn.place(x=120, y=516)
			save_as_draft_btn = Button(draft_send_emails_root, text="SAVE AS DRAFT", border=10, font="comicsansms 18 bold", fg='black', bg='pink', command=lambda :save_as_draft(mail_id_to_edit)).place(x=550, y=516)

			draft_send_emails_root.mainloop()

		except:
			messagebox.showerror("Edit Error", "Unable To Find The Draft Message")
			return


## This function is the layout function for the DRAFTED EMAILS
def drafted_emails_layout():
	try:
		root.destroy()
	except:
		pass
	try:
		send_emails_root.destroy()
	except:
		pass
	try:
		email_lists_root.destroy()
	except:
		pass
	try:
		draft_send_emails_root.destroy()
	except:
		pass
	## This function is the redirector function, which takes the selected data and passes it to the send_emails_home()
	def drafted_emails_edit():
		try:
			global mail_id_to_edit
			mail_id_to_edit = draft_selected_item[0]
			send_emails_home(mail_id_to_edit)
		except:
			messagebox.showinfo("Not Selected", "You Have Not Selected Any Entry To Delete")
			return

	## This function deletes the entire data selected from the "C:\\drafts" folder and "mail_details" table
	def drafted_emails_delete():
		try:
			mail_id_to_delete = draft_selected_item[0]
			delete_warning = messagebox.askquestion("Delete Warning", "Are You Sure You Want To Delete The Draft ?")
			if delete_warning == 'yes':
				q = "DELETE FROM mail_details WHERE mail_id='{}'".format(mail_id_to_delete)
				cursor.execute(q)
				db.commit()
				populate_draft_list()
				return
			else:
				return
		except:
			messagebox.showinfo("Not Selected", "You Have Not Selected Any Entry To Delete")
			return

	## This function selects the item from the DRAFTED EMAILS Listbox
	def draft_select_item(event):
		try:
			global draft_selected_item
			index = draft_list.curselection()[0]
			draft_selected_item = draft_list.get(index)
		except:
			pass

	## This function populates the DRAFTED EMAILS Listbox from the mail_details table (mail_id, date_edited, subject_line)
	def populate_draft_list():
		draft_list.delete(0, END)
		q = "SELECT mail_id, date_edited, subject_line FROM mail_details"
		cursor.execute(q)
		data = cursor.fetchall()
		for row in data:
			draft_list.insert(END, row)

	global drafted_emails_root
	drafted_emails_root = Tk()
	drafted_emails_root.title("DRAFTED EMAILS")
	drafted_emails_root.iconbitmap("./icons/ico-files/icon-16.ico")
	drafted_emails_root.geometry("650x550")
	drafted_emails_root.resizable(0,0)
	drafted_emails_root.configure(background="#D1FFFF")
	back_btn = Button(drafted_emails_root, text="<<", border=6, font="comicsansms 15 bold", bg="pink", command=home_layout).place(x=10, y=10)
	menubar = Menu(drafted_emails_root)
	drafted_emails_root.config(menu=menubar)
	submenu1 = Menu(menubar, tearoff=0)
	menubar.add_cascade(label="Navigate", menu=submenu1)
	submenu1.add_command(label="Email Lists", command=email_lists_layout)
	submenu1.add_command(label="Send Emails", command=lambda: send_emails_home(None))
	Label(drafted_emails_root, text="DRAFTED EMAILS", font="comicsansms 20 bold", bg="#D1FFFF").place(x=200,y=20)
	global draft_list  
	draft_list = Listbox(drafted_emails_root, border=3, height=10, width=55, font=("bold", 15)) 
	draft_list.place(x=5, y=120)
	scrollbary = Scrollbar(drafted_emails_root)
	scrollbary.place(x=623, y=120)
	scrollbarx = Scrollbar(drafted_emails_root, orient=HORIZONTAL)
	scrollbarx.place(x=10, y=375)
	draft_list.configure(yscrollcommand=scrollbary.set)
	draft_list.configure(xscrollcommand=scrollbarx.set)
	scrollbary.configure(command=draft_list.yview)
	scrollbarx.configure(command=draft_list.xview)
	draft_list.bind('<<ListboxSelect>>', draft_select_item)
	populate_draft_list()
	edit_btn = Button(drafted_emails_root, text="EDIT", font="comicsansms 18 bold", border=8, bg="pink", padx=20, command=drafted_emails_edit).place(x=100, y=415)
	delete_btn = Button(drafted_emails_root, text="DELETE", font="comicsansms 18 bold", border=8, bg="pink", command=drafted_emails_delete).place(x=400, y=415)
	drafted_emails_root.mainloop()

## This function is the "LIST MANAGER EDITOR" -- > For The "SEE EXISTING LISTS" Button
def list_manager_editor_layout():
	try:
		existing_lists.destroy()
	except:
		pass

	## This function Populates the listbox with the temp_list_emails
	def editor_populate_email_list_data():
		editor_email_data_list.delete(0, END)
		q = "SELECT name, email_address FROM list_emails WHERE list_id = '{}'".format(list_id_to_be_edited)
		cursor.execute(q)
		data = cursor.fetchall()
		for row in data:
			editor_email_data_list.insert(END, row)

	## This function selects the item to be edited from the editor_email_data_list
	def select_editor_email_listbox_item(event):
		try:
			index = editor_email_data_list.curselection()[0]
			global editor_selected 
			editor_selected = editor_email_data_list.get(index)
			editor_sub_name_entry.delete(0, END)
			editor_sub_name_entry.insert(END, editor_selected[0])
			editor_sub_email_entry.delete(0, END)
			editor_sub_email_entry.insert(END, editor_selected[1])
		except:
			pass

	## This function adds the data to the list_emails and then calls the populate function
	def editor_add():
		sub_name, sub_email = editor_sub_name_entry.get().strip(), editor_sub_email_entry.get().lower().replace(" ", "")
		if sub_name == "":
			sub_name = "NULL"
		if sub_email == "":
			messagebox.showinfo("Field Empty", "The Email Field Cannot Be Empty")
			return
		if func.valid_email(sub_email) == False:
			messagebox.showerror("Invalid", "The Subscriber Email Address Is Invalid")
			return
		if len(sub_email) > 255:
			messagebox.showerror("Invalid", "Length Of Email Cannot Exceed 255 Characters")
			return
		if len(sub_name) > 255:
			messagebox.showerror("Invalid", "Length Of Subscriber's Name Should Not Exceeed 255 Characters")
			return
		q = "SELECT email_address FROM list_emails WHERE list_id='{}'".format(list_id_to_be_edited)
		cursor.execute(q)
		data = cursor.fetchall()
		for i in data:
			if sub_email == i[0]:
				messagebox.showinfo("Email Taken", "The Email Address Have Already Been Taken Into The Box")
				return
		q = "INSERT INTO list_emails VALUES('{}','{}','{}')".format(list_id_to_be_edited, sub_email, sub_name)
		cursor.execute(q)
		db.commit()
		editor_populate_email_list_data()
		editor_sub_name_entry.delete(0, END)
		editor_sub_email_entry.delete(0,END)

	## This function updates the data in the list_emails and then calls the populate function (PROBLEM)
	def editor_update():
		try:
			sub_name, sub_email = editor_selected[0], editor_selected[1]
			sub_name_new, sub_email_new = editor_sub_name_entry.get().strip(), editor_sub_email_entry.get().lower().replace(" ","")
			if sub_name_new == "":
				sub_name_new = "NULL"
			if sub_email_new == "":
				messagebox.showinfo("Email Field Empty", "The Email Field Cannot Be Empty")
				return
			if func.valid_email(sub_email_new) == False:
				messagebox.showerror("Invalid Email", "The Email You Want To Update Is Invalid")
				return
			q = "SELECT email_address FROM list_emails WHERE list_id='{}'".format(list_id_to_be_edited)
			cursor.execute(q)
			data = cursor.fetchall()
			for i in data:
				if sub_email_new == i[0]:
					messagebox.showinfo("Email Taken", "The Email Address Have Already Been Taken Into The Box")
					return
			update_warning = messagebox.askquestion("Update Warning", f"Are You Sure You Want To Update {sub_email} EMAIL DATA")
			if update_warning == 'yes':
				q1 = "UPDATE list_emails SET name='{}' WHERE email_address='{}' AND list_id='{}'".format(sub_name_new, sub_email, list_id_to_be_edited)
				q2 = "UPDATE list_emails SET email_address='{}' WHERE email_address='{}' AND list_id='{}'".format(sub_email_new, sub_email, list_id_to_be_edited)
				cursor.execute(q1)
				cursor.execute(q2)
				db.commit()
				editor_populate_email_list_data()
				editor_sub_name_entry.delete(0, END)
				editor_sub_email_entry.delete(0, END)
			else:
				return
		except:
			return

	## This function deletes the data from the list_emails and then calls the populate function
	def editor_delete():
		try:
			delete_warning = messagebox.askquestion("Delete Warning", f"Are You Sure You Want To Delete {editor_selected[1]} EMAIL DATA")
			if delete_warning == 'yes':
				q = "DELETE FROM list_emails WHERE list_id='{}' AND email_address='{}'".format(list_id_to_be_edited, editor_selected[1])
				cursor.execute(q)
				db.commit()
				editor_sub_name_entry.delete(0, END)
				editor_sub_email_entry.delete(0, END)
			editor_populate_email_list_data()
		except:
			messagebox.showinfo("Not Selected", "You Have Not Selected Anything To Delete")
			return

	list_name_to_be_edited = existing_selected[0]
	global list_id_to_be_edited
	list_id_to_be_edited = func.get_list_id(list_name_to_be_edited)
	global list_manager_editor
	list_manager_editor = Tk()
	list_manager_editor.title("List Manager -- Edit Your Email List")
	list_manager_editor.geometry("800x650")
	list_manager_editor.configure(background="#D1FFFF")
	list_manager_editor.iconbitmap("./icons/ico-files/icon-16.ico")
	list_manager_editor.resizable(0,0)
	Label(list_manager_editor, text="Name : ", font="comicsansms 18 bold", bg="#D1FFFF").place(x=100, y=20)
	Label(list_manager_editor, text=f"{list_name_to_be_edited}", font="comicsansms 18 bold", bg="#D1FFFF").place(x=200, y=20)
	Label(list_manager_editor, text="Subscriber Name : ", font="comicsansms 18 bold", bg="#D1FFFF").place(x=10, y=80)
	Label(list_manager_editor, text="Subscriber Email : ", font="comicsansms 18 bold", bg="#D1FFFF").place(x=10, y=135)
	back_btn = Button(list_manager_editor, text="<<", font="comicsansms 15 bold", bg="pink", border=6, command=email_lists_layout).place(x=10, y=10)
	global editor_sub_name_entry, editor_sub_email_entry
	editor_sub_name_entry = Entry(list_manager_editor, font="comicsansms 18 bold", width=30)
	editor_sub_name_entry.place(x=300, y=80)
	editor_sub_email_entry = Entry(list_manager_editor, font="comicsansms 18 bold", width=30)
	editor_sub_email_entry.place(x=300, y=135)
	add_btn = Button(list_manager_editor, text="ADD", font="comicsansms 15 bold", border=6, bg="pink", padx=22, command=editor_add).place(x=100, y=210)
	update_btn = Button(list_manager_editor, text="UPDATE", font="comicsansms 15 bold", border=6, bg="pink", padx=4, command=editor_update).place(x=340, y=210)
	delete_btn = Button(list_manager_editor, text="DELETE", font="comicsansms 15 bold", border=6, bg="pink", padx=4, command=editor_delete).place(x=600, y=210)
	global editor_email_data_list  
	editor_email_data_list = Listbox(list_manager_editor, border=3, height=10, width=55, font=("bold", 15)) 
	editor_email_data_list.place(x=70, y=300)
	scrollbary = Scrollbar(list_manager_editor)
	scrollbary.place(x=720, y=302)
	scrollbarx = Scrollbar(list_manager_editor, orient=HORIZONTAL)
	scrollbarx.place(x=70, y=580)
	editor_email_data_list.configure(yscrollcommand=scrollbary.set)
	editor_email_data_list.configure(xscrollcommand=scrollbarx.set)
	scrollbary.configure(command=editor_email_data_list.yview)
	scrollbarx.configure(command=editor_email_data_list.xview)
	editor_email_data_list.bind('<<ListboxSelect>>', select_editor_email_listbox_item)
	editor_populate_email_list_data()
	list_manager_editor.mainloop()

## This function is the layout and display page for the existing email lists
def see_existing_lists_layout():
	try:
		email_lists_root.destroy()
	except:
		pass

	## This function is for the edit_btn, which filters the existing_selected for the list_manager_editor 
	def edit_existing_list():
		try:
			list_name_selected = existing_selected[0]
			list_manager_editor_layout()
		except:
			messagebox.showinfo("Not Selected", "You Have Not Selected Any EMAIL LIST")
			return

	## This function will delete an existing email list from the list_details and list_emails tables
	def delete_existing_list():
		try:
			warning = messagebox.askquestion("Delete Warning", f"Are You Sure You Want To Delete {existing_selected} EMAIL DATA")
			if warning == 'yes':
				list_id_to_be_deleted = func.get_list_id(existing_selected[0])
				q1 = "DELETE FROM list_emails WHERE  list_id = '{}'".format(list_id_to_be_deleted)
				q2 = "DELETE FROM list_details WHERE list_id = '{}'".format(list_id_to_be_deleted)
				cursor.execute(q1)
				cursor.execute(q2)
				db.commit()
				populate_existing_list_data()
			else:
				return
		except:
			messagebox.showinfo("Not Selected", "You Have Not Selected Any Email List")
			return

	## This function will populate the data in the "EXISTING EMAILS" listbox from the list_details table
	def populate_existing_list_data():
		existing_data_list.delete(0, END)
		q = "SELECT  list_name FROM list_details"
		cursor.execute(q)
		list_name_data = cursor.fetchall()
		for row in list_name_data:
			existing_data_list.insert(END, row)

	## This function will help getting the selected values to EDIT and DELETE the email lists
	def select_existing_listbox_item(event):
		try:
			global existing_selected
			index = existing_data_list.curselection()[0]
			existing_selected = existing_data_list.get(index)
		except:
			pass

	global existing_lists
	existing_lists = Tk()
	existing_lists.title("Existing Email Lists")
	existing_lists.geometry("700x550")
	existing_lists.resizable(0,0)
	existing_lists.configure(background="#D1FFFF")
	existing_lists.iconbitmap("./icons/ico-files/icon-16.ico")
	back_btn = Button(existing_lists, text="<<", font="comicsansms 15 bold", bg="pink", border=6, command=email_lists_layout).place(x=10, y=10)
	global existing_data_list  
	existing_data_list = Listbox(existing_lists, border=3, height=10, width=55, font=("bold", 15)) 
	existing_data_list.place(x=40, y=100)
	scrollbary = Scrollbar(existing_lists)
	scrollbary.place(x=667, y=100)
	scrollbarx = Scrollbar(existing_lists, orient=HORIZONTAL)
	scrollbarx.place(x=40, y=360)
	existing_data_list.configure(yscrollcommand=scrollbary.set)
	existing_data_list.configure(xscrollcommand=scrollbarx.set)
	scrollbary.configure(command=existing_data_list.yview)
	scrollbarx.configure(command=existing_data_list.xview)
	existing_data_list.bind('<<ListboxSelect>>', select_existing_listbox_item)
	populate_existing_list_data()
	Label(existing_lists, text="Existing Email Lists", font="comicsansms 20 bold", bg="#D1FFFF").place(x=220, y=20)
	edit_btn = Button(existing_lists, text="EDIT", font="comicsansms 15 bold", bg="pink", border=8, command=edit_existing_list, padx=20, pady=5).place(x=180, y=430)
	delete_btn = Button(existing_lists, text="DELETE", font="comicsansms 15 bold", bg="pink", border=8, pady=5, padx=2, command=delete_existing_list).place(x=400, y=430)
	existing_lists.mainloop()


## This function is layout for the "LIST MANAGER" --> For The "CREATE NEW LIST" Button
def list_manager_layout():
	try:
		name_of_list.destroy()
	except:
		pass
	## This Internal Function Will Take The "Email Listbox Data" With The Saved Data in Tables and Return "EMAIL LIST HOME"
	def save_email_listbox_data():
		if func.is_temp_empty() == True:
			messagebox.showinfo("No Emails Entered", "You Cannot Create An Empty Email List")
			return
		fresh_list_id = func.generate_list_id()
		fresh_list_name = new_list_name
		q = "INSERT INTO list_details VALUES ('{}','{}')".format(fresh_list_id, fresh_list_name)
		cursor.execute(q)
		q = "SELECT name, email_address FROM temp_list_emails"
		cursor.execute(q)
		temp_data = cursor.fetchall()
		for row in temp_data:
			q = "INSERT INTO list_emails VALUES ('{}','{}','{}')".format(fresh_list_id, row[1], row[0])
			cursor.execute(q)
		db.commit()
		func.delete_temp_data()
		email_lists_layout()

	## This Internal Function Will Populate the Listbox Data With The Temporary "NAME-EMAIL DATA"
	def populate_email_list_data():
		email_data_list.delete(0, END)
		q = "SELECT * FROM temp_list_emails"
		cursor.execute(q)
		data = cursor.fetchall()
		for row in data:
			email_data_list.insert(END, row)

	## This Internal Function Will Help In Selecting and Populating The "Email Listbox Data" to the Entry Fields
	def select_email_listbox_item(event):
		try:
			index = email_data_list.curselection()[0]
			global selected 
			selected = email_data_list.get(index)
			sub_name_entry.delete(0, END)
			sub_name_entry.insert(END, selected[0])
			sub_email_entry.delete(0, END)
			sub_email_entry.insert(END, selected[1])
		except:
			pass
	## This Internal Function Will Add The Data Into The Listbox
	def add_email_listbox():
		sub_name, sub_email = sub_name_entry.get().strip(), sub_email_entry.get().lower().replace(" ", "")
		if sub_name == "":
			sub_name = "NULL"
		if sub_email == "":
			messagebox.showinfo("Field Empty", "The Email Field Cannot Be Empty")
			return
		if func.valid_email(sub_email) == False:
			messagebox.showerror("Invalid", "The Subscriber Email Address Is Invalid")
			return
		if len(sub_email) > 255:
			messagebox.showerror("Invalid", "Length Of Email Cannot Exceed 255 Characters")
			return
		if len(sub_name) > 255:
			messagebox.showerror("Invalid", "Length Of Subscriber's Name Should Not Exceeed 255 Characters")
			return
		q = "SELECT email_address FROM temp_list_emails"
		cursor.execute(q)
		data = cursor.fetchall()
		for i in data:
			if sub_email == i[0]:
				messagebox.showinfo("Email Taken", "The Email Address Have Already Been Taken Into The Box")
				return
		q = "INSERT INTO temp_list_emails VALUES ('{}','{}')".format(sub_name, sub_email)
		cursor.execute(q)
		db.commit()
		populate_email_list_data()
		sub_name_entry.delete(0, END)
		sub_email_entry.delete(0,END)

	## This Internal Function Will Update The Data Into The Listbox
	def update_email_listbox():
		try:
			sub_name, sub_email = selected[0], selected[1]
			sub_name_new, sub_email_new = sub_name_entry.get().strip(), sub_email_entry.get().lower().replace(" ","")
			if sub_name_new == "":
				sub_name_new = "NULL"
			if sub_email_new == "":
				messagebox.showinfo("Email Field Empty", "The Email Field Cannot Be Empty")
				return
			if func.valid_email(sub_email_new) == False:
				messagebox.showerror("Invalid Email", "The Email You Want To Update Is Invalid")
				return
			q1 = "UPDATE temp_list_emails SET name='{}' WHERE email_address='{}'".format(sub_name_new, sub_email)
			q2 = "UPDATE temp_list_emails SET email_address='{}' WHERE email_address='{}'".format(sub_email_new, sub_email)
			cursor.execute(q1)
			cursor.execute(q2)
			db.commit()
			populate_email_list_data()
			sub_name_entry.delete(0, END)
			sub_email_entry.delete(0, END)
		except:
			return

	## This Internal Function Will Delete The Data From The Listbox
	def delete_email_listbox():
		try:
			delete_warning = messagebox.askquestion ('Delete Warning', f'Do you want to delete {selected[1]} EMAIL DATA', icon='warning')
			if delete_warning == 'yes':
				q = "DELETE FROM temp_list_emails WHERE email_address='{}'".format(selected[1])
				cursor.execute(q)
				db.commit()
				populate_email_list_data()
				sub_name_entry.delete(0, END)
				sub_email_entry.delete(0,END)
				return
			else:
				return
		except:
			messagebox.showinfo("Not Selected", "You Have Not Selected Any Entry")
			return

	global list_manager
	list_manager = Tk()
	add_btn = Button().place()
	list_manager.title("List Manager -- Create New Email List")
	list_manager.geometry("800x650")
	list_manager.configure(background="#D1FFFF")
	list_manager.iconbitmap("./icons/ico-files/icon-16.ico")
	list_manager.resizable(0,0)
	back_btn = Button(list_manager, text="<<", font="comicsansms 15 bold", bg="pink", border=6, command=email_lists_layout).place(x=10, y=10)
	Label(list_manager, text="Name : ", font="comicsansms 18 bold", bg="#D1FFFF").place(x=100, y=20)
	Label(list_manager, text=f"{new_list_name}", font="comicsansms 18 bold", bg="#D1FFFF").place(x=200, y=20)
	Label(list_manager, text="Subscriber Name : ", font="comicsansms 18 bold", bg="#D1FFFF").place(x=10, y=80)
	Label(list_manager, text="Subscriber Email : ", font="comicsansms 18 bold", bg="#D1FFFF").place(x=10, y=135)
	global sub_name_entry, sub_email_entry
	sub_name_entry = Entry(list_manager, font="comicsansms 18 bold", width=30)
	sub_name_entry.place(x=300, y=80)
	sub_email_entry = Entry(list_manager, font="comicsansms 18 bold", width=30)
	sub_email_entry.place(x=300, y=135)
	add_btn = Button(list_manager, text="ADD", font="comicsansms 15 bold", border=6, bg="pink", padx=22, command=add_email_listbox).place(x=100, y=210)
	update_btn = Button(list_manager, text="UPDATE", font="comicsansms 15 bold", border=6, bg="pink", padx=4, command=update_email_listbox).place(x=340, y=210)
	delete_btn = Button(list_manager, text="DELETE", font="comicsansms 15 bold", border=6, bg="pink", padx=4, command=delete_email_listbox).place(x=600, y=210)
	global email_data_list  
	email_data_list = Listbox(list_manager, border=3, height=10, width=55, font=("bold", 15)) 
	email_data_list.place(x=70, y=300)
	scrollbary = Scrollbar(list_manager)
	scrollbary.place(x=720, y=302)
	scrollbarx = Scrollbar(list_manager, orient=HORIZONTAL)
	scrollbarx.place(x=70, y=580)
	email_data_list.configure(yscrollcommand=scrollbary.set)
	email_data_list.configure(xscrollcommand=scrollbarx.set)
	scrollbary.configure(command=email_data_list.yview)
	scrollbarx.configure(command=email_data_list.xview)
	email_data_list.bind('<<ListboxSelect>>', select_email_listbox_item)
	populate_email_list_data()
	save_btn = Button(list_manager, text="SAVE", font="comicsansms 15 bold", border=8, padx=20, bg="pink", command=save_email_listbox_data)
	save_btn.place(x=660, y=570)
	list_manager.mainloop()


## This is the validation funcion for the name_of _the_list(), after clicking the "PROCEED >>" Button
def proceed_validation():
	global new_list_name
	new_list_name = name_of_list_entry.get().strip().lower()
	if new_list_name.strip() == "":
		messagebox.showinfo("Empty", "Name Field Cannot Be Empty")
		return
	if len(new_list_name) > 50:
		messagebox.showinfo("Length Exceeded", "Email List Name Cannot Exceed 50 Characters")
		return
	if func.list_name_exists(new_list_name) == True:
		messagebox.showinfo("Email List Exists", "An Email List With That Name Already Exists")
		return
	list_manager_layout()


## This function is the layout function for getting the name of the list to the "LIST MANAGER"
def name_of_list_layout():
	try:
		email_lists_root.destroy()
	except:
		pass
	global name_of_list
	name_of_list = Tk()
	name_of_list.title("Choose A Name Of Your New List")
	name_of_list.geometry("600x300")
	name_of_list.resizable(0,0)
	name_of_list.configure(background="#D1FFFF")
	name_of_list.iconbitmap("./icons/ico-files/icon-16.ico")
	back_btn = Button(name_of_list, text="<<", font="comicsansms 15 bold", bg="pink", border=6, command=email_lists_layout).place(x=10, y=10)
	Label(name_of_list, text="ENTER NAME OF YOUR LIST >>", background="#D1FFFF", font="comicsansms 18 bold").place(x=120,y=50)
	global name_of_list_entry
	name_of_list_entry = Entry(name_of_list, font="comicsansms 20 bold")
	name_of_list_entry.place(x=135, y=110)
	proceed_btn = Button(name_of_list, text="PROCEED >>", font="comicsansms 15 bold", border=6, bg="pink", command=proceed_validation).place(x=215, y=200)
	name_of_list.mainloop()


## This function in the layout page for the EMAIL LISTS Home Page
def email_lists_layout():
	try:
		root.destroy()
	except:
		pass
	try:
		list_manager.destroy()
	except:
		pass
	try:
		name_of_list.destroy()
	except:
		pass
	try:
		existing_lists.destroy()
	except:
		pass
	try:
		list_manager_editor.destroy()
	except:
		pass
	try:
		send_emails_root.destroy()
	except:
		pass
	try:
		drafted_emails_root.destroy()
	except:
		pass
	global email_lists_root
	email_lists_root = Tk()
	back_btn = Button(email_lists_root, text="<<", border=5, font="comicsansms 12 bold", fg='black', bg='pink', command=home_layout)
	back_btn.place(x=5,y=5)
	email_lists_root.title("EMAIL LISTS")
	email_lists_root.geometry("600x350")
	email_lists_root.resizable(0,0)
	email_lists_root.configure(background="#D1FFFF")
	email_lists_root.iconbitmap("./icons/ico-files/icon-16.ico")
	menubar = Menu(email_lists_root)
	email_lists_root.config(menu=menubar)
	submenu1 = Menu(menubar, tearoff=0)
	menubar.add_cascade(label="Navigate", menu=submenu1)
	submenu1.add_command(label="Send Emails", command=lambda: send_emails_home(None))
	submenu1.add_command(label="Drafted Emails", command=drafted_emails_layout)
	create_list_btn = Button(email_lists_root, text="CREATE NEW LIST", font="comicsansms 18 bold", bg="pink", border=6, padx=12, command=name_of_list_layout).place(x=165,y=70)
	see_existing_lists_btn = Button(email_lists_root, text="SEE EXISTING LISTS", font="comicsansms 18 bold", bg="pink", border=6, command=see_existing_lists_layout).place(x=165,y=150)
	email_lists_root.mainloop()

## This function is responsible for clearing the text in the entry boxes in sender_email_layout() window
def clear():
	smtp_address_entry.delete(0,END)
	port_number_entry.delete(0,END)
	email_address_entry.delete(0,END)
	email_password_entry.delete(0, END)

## This function is responsible for logging-in and adding an email entry in sender_details table
def login_and_add():
	smtp, port, email, password = smtp_address_entry.get().strip().lower(), port_number_entry.get().strip().lower(), email_address_entry.get().strip().lower(), email_password_entry.get().strip()
	if smtp.strip() == "" or port.strip() == "" or email.strip() == "" or password.strip() == "":
		messagebox.showwarning("Fields Empty", "No Field Should Be Empty")
		return
	if func.valid_email(email) == False:
		messagebox.showwarning("Invalid", "The Email Address is Invalid")
		return
	if func.email_exists(email) == True:
		messagebox.showinfo("Email Exists", "The Email Address Already Exists in the database")
		return
	try:
		with smtplib.SMTP(smtp, int(port)) as s:
			s.ehlo()
			s.starttls()
			s.ehlo()
			s.login(email, password)
			q = "INSERT INTO sender_details VALUES ('{}','{}','{}','{}')".format(smtp, port, email, password)
			cursor.execute(q)
			db.commit()
			clear()
			populate_sender_data()
			messagebox.showinfo("Successfully Added", "Email Data Added Successfully")
			return
	except:
		messagebox.showerror("Login Error", "Unable To Login To The SMTP Server")
		return

## This function is responsible for logging-in and updating an email entry selected in the sender_details table
def login_and_update():
	smtp, port, email, password = selected_item[0], selected_item[1], selected_item[2], selected_item[3]
	smtp_new, port_new, email_new, password_new = smtp_address_entry.get().strip().lower(), port_number_entry.get().strip().lower(), email_address_entry.get().strip().lower(), email_password_entry.get().strip()
	if smtp_new.strip() == "" or port_new.strip() == "" or email_new.strip() == "" or password_new.strip() == "":
		messagebox.showwarning("Fields Empty", "No Field Should Be Empty")
		return
	if func.valid_email(email_new) == False:
		messagebox.showwarning("Invalid", "The Email Address is Invalid")
		return
	if func.email_exists(email_new) == True:
		messagebox.showinfo("Email Exists", "The Email Address Already Exists in the database")
		return
	try:
		with smtplib.SMTP(smtp_new, int(port_new)) as s:
			s.ehlo()
			s.starttls()
			s.ehlo()
			s.login(email_new, password_new)
			q1 = "UPDATE sender_details SET smtp_address='{}' WHERE email_address='{}'".format(smtp_new, email)
			q2 = "UPDATE sender_details SET port_number='{}' WHERE email_address='{}'".format(port_new, email)
			q3 = "UPDATE sender_details SET email_address='{}' WHERE email_address='{}'".format(email_new, email)
			q4 = "UPDATE sender_details SET email_password='{}' WHERE email_address='{}'".format(password_new, email)
			cursor.execute(q1)
			cursor.execute(q2)
			cursor.execute(q3)
			cursor.execute(q4)
			db.commit()
			clear()
			populate_sender_data()
			messagebox.showinfo("Successfully Updated", "Email Data Updated Successfully")
			return
	except:
		messagebox.showerror("Login Error", "Unable To Login To The SMTP Server")
		return

## This function is responsible for deleting the email entry selected in the sender_details table
def delete_entry():
	try:
		delete_warning = messagebox.askquestion ('Delete Warning', f'Do you want to delete {selected_item[2]} EMAIL DATA', icon='warning')
		if delete_warning == 'yes':
			q = "DELETE FROM sender_details WHERE email_address='{}'".format(selected_item[2])
			cursor.execute(q)
			db.commit()
			clear()
			populate_sender_data()
			return
		else:
			return
	except:
		messagebox.showinfo("Not Selected", "You Have Not Selected Any Entry")
		return

## This funcion is responsible for fetching data and filling the listbox from the sender_details table
def populate_sender_data():
	data_list.delete(0, END)
	for row in func.fetch_sender_data():
		data_list.insert(END, row)


## This Function Will select the Record in the Listbox which the user selects and then populates the entries
def select_item(event):
	try:
		global selected_item
		index = data_list.curselection()[0]
		selected_item = data_list.get(index)
		smtp_address_entry.delete(0, END)
		smtp_address_entry.insert(END, selected_item[0])
		port_number_entry.delete(0, END)
		port_number_entry.insert(END, selected_item[1])
		email_address_entry.delete(0, END)
		email_address_entry.insert(END, selected_item[2])
		email_password_entry.delete(0, END)
		email_password_entry.insert(END, selected_item[3])
	except:
		pass


## This is the SENDER EMAILS LAYOUT page for the "Settings > Sender Emails" submenu
def sender_email_layout():
	try:
		root.destroy()
	except:
		pass
	global sender_root
	sender_root = Tk()
	back_btn = Button(sender_root, text="<<", border=5, font="comicsansms 12 bold", fg='black', bg='pink', command=home_layout)
	back_btn.place(x=5,y=5)
	sender_root.title("Sender Emails")
	sender_root.geometry("700x650")
	sender_root.resizable(0,0)
	sender_root.configure(background="#D1FFFF")
	sender_root.iconbitmap("./icons/ico-files/icon-16.ico")
	global data_list  
	data_list = Listbox(sender_root, border=3, height=10, width=55, font=("bold", 15)) 
	data_list.place(x=30, y=350)
	scrollbary = Scrollbar(sender_root)
	scrollbary.place(x=660, y=350)
	scrollbarx = Scrollbar(sender_root, orient=HORIZONTAL)
	scrollbarx.place(x=32, y=610)
	data_list.configure(yscrollcommand=scrollbary.set)
	data_list.configure(xscrollcommand=scrollbarx.set)
	scrollbary.configure(command=data_list.yview)
	scrollbarx.configure(command=data_list.xview)
	data_list.bind('<<ListboxSelect>>', select_item)
	populate_sender_data()
	start_label = Label(sender_root, text="SENDER EMAILS", font="comicsansms 20 bold", bg="#D1FFFF")
	start_label.place(x=230, y=10)
	smtp_address_label = Label(sender_root, text="SMTP ADDRESS -->", font="comicsansms 15 bold", bg="#D1FFFF")
	smtp_address_label.place(x=20, y=65)
	port_number_label = Label(sender_root, text="PORT NUMBER -->", font="comicsansms 15 bold", bg="#D1FFFF")
	port_number_label.place(x=20, y=115)
	email_address_label = Label(sender_root, text="EMAIL ADDRESS -->", font="comicsansms 15 bold", bg="#D1FFFF")
	email_address_label.place(x=20, y=165)
	email_password_label = Label(sender_root, text="EMAIL PASSWORD -->", font="comicsansms 15 bold", bg="#D1FFFF")
	email_password_label.place(x=20, y=215)
	global smtp_address_entry
	smtp_address_entry = Entry(sender_root, font="comicsansms 15 bold")
	smtp_address_entry.place(x=330, y=75)
	global port_number_entry
	port_number_entry = Entry(sender_root, font="comicsansms 15 bold")
	port_number_entry.place(x=330, y=115)
	global email_address_entry
	email_address_entry = Entry(sender_root, font="comicsansms 15 bold")
	email_address_entry.place(x=330, y=165)
	global email_password_entry
	email_password_entry = Entry(sender_root, font="comicsansms 15 bold")
	email_password_entry.place(x=330, y=215)
	login_and_add_btn = Button(sender_root, text="LOGIN & ADD", font="comicsansms 15 bold", border=6, fg="black", bg="pink", command=login_and_add)
	login_and_add_btn.place(x=50, y=280) 
	login_and_update_btn = Button(sender_root, text="LOGIN & UPDATE", font="comicsansms 15 bold", border=6, fg="black", bg="pink", command=login_and_update)
	login_and_update_btn.place(x=230, y=280)
	delete_btn = Button(sender_root, text="DELETE ENTRY", font="comicsansms 15 bold", border=6, fg="black", bg="pink", command=delete_entry)
	delete_btn.place(x=450, y=280)
	sender_root.mainloop()

## This is the Validation function for Deleting the App Password after clicking the DELETE PASSWORD Button
def delete_password():
	q = "UPDATE app_password SET password = '{}'".format("NULL")
	cursor.execute(q)
	db.commit() 
	delete_root.destroy()
	home_layout()


## This is the DELETE PASSWORD LAYOUT page for the "Security > App Password" submenu
def delete_password_layout():
	try:
		root.destroy()
	except:
		pass
	global delete_root
	delete_root = Tk()
	back_btn = Button(delete_root, text="<<", border=5, font="comicsansms 12 bold", fg='black', bg='pink', command=home_layout)
	back_btn.place(x=5,y=5)
	delete_root.title("App Password - Delete")
	delete_root.geometry("600x280")
	delete_root.resizable(0,0)
	delete_root.configure(background="#D1FFFF")
	delete_root.iconbitmap("./icons/ico-files/icon-16.ico")
	Label(delete_root, text="YOUR PASSWORD IS -->", font="comicsansms 15 bold", bg="#D1FFFF").place(x=100, y=60)
	Label(delete_root, text=f"{func.pass_fetch()}", font="comicsansms 18 bold", bg="#D1FFFF", fg="red").place(x=200, y=100)
	delete_btn = Button(delete_root,  text="DELETE PASSWORD", border=6, font="comicsansms 15 bold", fg='black', bg='pink', command=delete_password)
	delete_btn.place(x=190, y=180)
	delete_root.mainloop()


## This is the Validation function for Creating and Storing the App Password after clicking the CREATE PASSWORD Button
def create_password():
	if password_text.get().strip() == "" or confirm_password_text.get().strip() == "":
		messagebox.showinfo("Empty", "Fields Cannot Be Empty")
		return
	if password_text.get().strip() != confirm_password_text.get().strip():
		messagebox.showinfo("Do Not Match", "Passwords Do Not Match")
		return
	if func.pass_check(password_text.get().strip()) == False:	
		messagebox.showinfo("Wrong Input", "The Password Should Be Between 6 to 20 Characters")
		return
	q = "UPDATE app_password SET password = '{}'".format(password_text.get().strip())
	cursor.execute(q)
	db.commit() 
	create_root.destroy()
	home_layout()


## This is the CREATE PASSWORD LAYOUT page for the "Security > App Password" submenu
def create_password_layout():
	try:
		root.destroy()
	except:
		pass
	global create_root
	create_root = Tk()
	create_root.title("App Password - Create")
	create_root.geometry("600x280")
	create_root.resizable(0,0)
	create_root.configure(background="#D1FFFF")
	create_root.iconbitmap("./icons/ico-files/icon-16.ico")
	back_btn = Button(create_root, text="<<", border=5, font="comicsansms 12 bold", fg='black', bg='pink', command=home_layout)
	back_btn.place(x=5,y=5)
	global password_text, confirm_password_text
	password_text = StringVar()
	confirm_password_text = StringVar()
	Label(create_root, text="PASSWORD:", font="comicsansms 15 bold", bg="#D1FFFF").place(x=10, y=70)
	Label(create_root, text="CONFIRM PASSWORD:", font="comicsansms 15 bold", bg="#D1FFFF").place(x=10, y=120)
	pass_entry = Entry(create_root, font="comicsansms 14 bold", text=password_text)
	pass_entry.place(x=280, y=70)
	pass_entry.configure(show="*")
	confirm_pass_entry = Entry(create_root, font="comicsansms 14 bold", text=confirm_password_text)
	confirm_pass_entry.place(x=280, y=120)
	confirm_pass_entry.configure(show="*")
	create_btn = Button(create_root,  text="CREATE PASSWORD", border=6, font="comicsansms 15 bold", fg='black', bg='pink', command=create_password)
	create_btn.place(x=180,y=185)
	create_root.mainloop()


## This is the Filter function for the "Security > App Password" submenu, and to differentiate between Password Created and Not Created
def app_password_filter():
	if func.password_exists() == True:
		delete_password_layout()
	else:
		create_password_layout()


## This is the HOME Page layout of BulkMail and the starting point of the application
def home_layout():
	try:
		login_root.destroy()
	except:
		pass
	try:
		create_root.destroy()
	except:
		pass
	try:
		delete_root.destroy()
	except:
		pass
	try:
		sender_root.destroy()
	except:
		pass
	try:
		email_lists_root.destroy()
	except:
		pass
	try:
		send_emails_root.destroy()
	except:
		pass
	try:
		drafted_emails_root.destroy()
	except:
		pass
	global root
	root = Tk()
	root.title("BulkMail HOME")
	root.geometry("600x350")
	root.resizable(0,0)
	root.configure(background="#D1FFFF")
	root.iconbitmap("./icons/ico-files/icon-16.ico")
	menubar = Menu(root)
	root.config(menu=menubar)
	submenu1 = Menu(menubar, tearoff=0)
	menubar.add_cascade(label="Settings", menu=submenu1)
	submenu1.add_command(label="Sender Emails", command=sender_email_layout) 
	submenu2 = Menu(menubar, tearoff=0)
	menubar.add_cascade(label="Security", menu=submenu2)
	submenu2.add_command(label="App Password", command=app_password_filter)
	email_list_btn = Button(text="EMAIL LISTS", font="comicsansms 16 bold", padx=31, bg="#FF0071", fg="white", border=8, command=email_lists_layout)
	email_list_btn.place(x=178,y=50)
	send_email_btn = Button(text="SEND EMAILS", font="comicsansms 16 bold", padx=25, bg="#FF0071", fg="white", border=8, command=lambda: send_emails_home(None))
	send_email_btn.place(x=178,y=130)
	drafted_emails_btn = Button(text="DRAFTED EMAILS", font="comicsansms 16 bold", bg="#FF0071", fg="white", border=8, padx=4, command=drafted_emails_layout)
	drafted_emails_btn.place(x=178,y=210)
	root.mainloop()


## This is the Login-Layout Validation Function, for logging the user in
def app_login_validation():
	q = "SELECT PASSWORD FROM app_password"
	cursor.execute(q)
	data = cursor.fetchall()
	password = pass_entered.get()
	password = password.strip()
	for i in data:
		if i[0] == password:
			home_layout()
		else:
			messagebox.showinfo("Error", "Passwords Don't Match")


## This function is the Log-In Layout For the App
def app_login_layout():
	global login_root
	login_root = Tk()
	login_root.title("BulkMail App Login")
	login_root.geometry("500x250")
	login_root.resizable(0,0)
	login_root.configure(background="#D1FFFF")
	login_root.iconbitmap("./icons/ico-files/icon-16.ico")
	global pass_entered
	pass_entered = StringVar()
	Label(login_root, text="Enter App Password", font="comicsansms 20 bold", fg="black", bg="#D1FFFF").place(x=118, y=30)
	pass_entry = Entry(login_root, text=pass_entered, font="comicsansms 18 bold")
	pass_entry.place(x=123, y=80)
	pass_entry.configure(show="*")
	open_app = Button(login_root,  text="OPEN APP", border=6, font="comicsansms 15 bold", fg='black', bg='pink', command=app_login_validation)
	open_app.place(x=190,y=150)
	login_root.mainloop()


## This is the starting point of the application
if func.password_exists() == True:
	app_login_layout()
else:
	home_layout()


db.commit()
db.close()

