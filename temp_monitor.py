# -*- coding: utf-8 -*-
from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from email.mime.text import MIMEText
from apiclient import errors
from threading import Thread
from thread import start_new_thread
import mimetypes
import base64
import socket
import sys
import csv
import datetime
import paramiko
import webbrowser
#import numpy
import pandas as pd
import matplotlib.pyplot as plt

def main():
	print('Running Temp Monitor')
	authenticate()
	make_log()
	open_browser()
	run_socket()

def authenticate():
# Authenticate user  with Google OAuth
	SCOPES = 'https://www.googleapis.com/auth/gmail.send'
	store = file.Storage('token.json')
	creds = store.get()
# Prompts for user login if no credentials present
	if not creds or creds.invalid:
		flow = client.flow_from_clientsecrets('credentials.json', SCOPES)  # credentials.json downloaded from google dev cloud
		creds = tools.run_flow(flow, store, http=Http(disable_ssl_certificate_validation=True))  # no ssl check because booz allen breaks everything

def alert():
# send emails and texts to all emails in $contacts
# atkinsondaniel123@gmail.com
# 2108628219@gmail.com
# shaukat_rameez@bah.com
# morales_mateo@bah.com
	store = file.Storage('token.json')
	creds = store.get()
	service = build('gmail', 'v1', http=creds.authorize(Http(disable_ssl_certificate_validation=True)))  # no ssl check because booz allen breaks everything
	contacts = ['atkinsondaniel123@gmail.com','2108628219@txt.att.net','2105748926@mymetropcs.com','shaukat_rameez@bah.com','morales_mateo@bah.com']
	for person in contacts:
		msg = create_message("me",person,'GIP Warning','GIP temp to high')  # 'me' refers to currently authenticated user
		send_message(service,"me",msg)

def create_message(sender, to, subject, message_text):
# creates email msg as b64 encoded string
	message = MIMEText(message_text)
	message['to'] = to
	message['from'] = sender
	message['subject'] = subject
	return {'raw': base64.urlsafe_b64encode(message.as_string())}

def send_message(service, user_id, message):
# end message created in create_message
	try:
		message = (service.users().messages().send(userId=user_id, body=message)
			.execute())
		return message
	except errors.HttpError, error:
		print(error)

def make_log():
# formats csv for logging/graphing
	header = ["datetime","temp"]
	with open('temp.csv', 'a') as csvWrite:
                writer = csv.writer(csvWrite, delimiter=',', quotechar='|',lineterminator='\n')
                writer.writerow(header)

def run_socket():
# opens socket to listen to pi, as well as monitoring temp and writting to csv
	socket_thread = Thread(target=run_pi_socket)  # runs socket in bg

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.bind( ("0.0.0.0", 8000) )
	sock.listen(1)
	print("Waiting for Pi Connection")
#	socket_thread.start()
	connection, client_address = sock.accept()
	print("Connected received ", client_address)

	row = []
	tempHigh = False  # keeps from constantly sending emails
	counter = 0
	timer = 180
	while True:
		counter += 1
		timer += 1
		temp_c = connection.recv(5).strip()  # 5 numbers + newline char
		print(str(counter) + "!" + temp_c + "!" + str(timer))
		if temp_c != "":
			temp_f = float(temp_c)/1000 * 9/5 + 32  # convert to fahrenheit
			if float(temp_f) > 79.0 and not tempHigh and timer > 180:
				print('oh god oh jeez')
#				start_new_thread(alert,())
				alert()
				tempHigh = True  # threshold exceeded
				timer = 0
			elif float(temp_f) < 79.0:
				tempHigh = False  # threshold not exceeded
			time1 = datetime.datetime.now()
			row.append(time1)
			row.append(temp_f)

			with open('temp.csv', 'a') as csvWrite:
				logWriter = csv.writer(csvWrite, delimiter=',', quotechar='|',lineterminator='\n')
				logWriter.writerow(row)
			graph()
			del row[0]
			del row[0]
		else:
			print("empty socket response")
			break
def graph():
#plot last 25 entries
	df = pd.read_csv("temp.csv", parse_dates=['datetime'], index_col="datetime")
	filter = df.tail(25)  # only graph recent entries
	filter.plot()
	plt.ylim([60,100])
	plt.annotate('%0.2f' % filter['temp'][filter.index[-1]], xy=(1, filter['temp'][filter.index[-1]]), xytext=(8, 0), 
             xycoords=('axes fraction', 'data'), textcoords='offset points')  # write last entry along right side
	plt.axhline(y=79, color='red')
	plt.savefig("graph.png")
	plt.close('all')  # saves ram

def run_pi_socket():
# ssh into pi and run socket script
	host="raspi2"
	user="pi"
	client = paramiko.SSHClient()
	client.load_system_host_keys()
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # booz allen messes everything up pt. 200012
	client.connect(host, username=user)
	stdin, stdout, stderr = client.exec_command('python socket_test.py')

def open_browser():
# open web browser to monitor site
	url = "file:///home/gipmonitor/temp_monitor/index.html"
	webbrowser.open(url)

main()

