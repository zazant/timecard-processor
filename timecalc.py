# truncate all hours between 8:30am and 5:00pm
# lunch has to be 30min if worked > 6hours

import sys
import csv
from datetime import *
from copy import deepcopy
from PyQt5.QtWidgets import (QFileDialog, QApplication, QWidget,
	 QPushButton, QVBoxLayout, QMessageBox, QInputDialog)
from PyQt5.QtGui import QIcon

class Employee:
	day_dict = {
		0: "Thursday",
		1: "Friday",
		2: "Saturday",
		3: "Sunday",
		4: "Monday",
		5: "Tuesday",
		6: "Wednesday"
	}

	def __init__(self, init_array):
		# set initial values
		self.times = [[], [], [], [], [], [], []]
		self.time_duos = [[], [], [], [], [], [], []]

		self.overtime = timedelta(0)
		self.vacation_time = timedelta(0)
		self.sick_time = timedelta(0)

		# format name
		self.name = init_array[1][0].replace("  -  ", "").replace("   ", ", ").title()
		
		# convert csv clock times to python datetime arrays
		for row in init_array[1:13]:
			for index, element in enumerate(row[2:]):
				if element != '':
					fixed_date = element.replace("*", "")
					self.times[index].append(datetime.strptime(fixed_date, '%I:%M %p'))

		# if amount of clocks in day is odd, fix the day with user input
		times_copy = self.times.copy()
		for day_index, day in enumerate(times_copy):
			if len(day) % 2 == 1:
				self.fix_day(day_index)

		# sort clocks into lists of 2 dimensional duos (clock in, out)
		for day_index, day in enumerate(self.times):
			for clock_index, clock in enumerate(day):
				if clock_index % 2 == 0:
					time_duo = [day[clock_index], day[clock_index + 1]]
					# print(self.name, " ", day_index, " ", time_duo)
					self.time_duos[day_index].append(time_duo)

		# create copy of duos matrix to delete excess duos
		time_duos_copy = deepcopy(self.time_duos)

		# delete excess duos
		for day_index, day in enumerate(time_duos_copy):
			for time_duo_index, time_duo in enumerate(day):
				# get rid of duos that start and end before 8:30
				if time_duo[1] < datetime(hour=8, minute=30, year=1900, month=1, day=1):
					self.time_duos[day_index].remove(time_duo)

				# get rid of duos that start and end after 5 and add to overtime
				if time_duo[0] > datetime(hour=17, minute=0, year=1900, month=1, day=1):
					self.overtime += Employee.calc_length(time_duo)
					self.time_duos[day_index].remove(time_duo)
		
		# truncate duos
		for day in self.time_duos:
			for time_duo in day:
				# set first clock to 8:30am if before
				if time_duo[0] < datetime(hour=8, minute=30, year=1900, month=1, day=1):
					time_duo[0] = datetime(hour=8, minute=30, year=1900, month=1, day=1)
				
				# set last duo to end at 5pm if after and add to overtime
				if time_duo[1] > datetime(hour=17, minute=0, year=1900, month=1, day=1):
					self.overtime += \
						time_duo[1] - datetime(hour=17, minute=0, year=1900, month=1, day=1)
					time_duo[1] = datetime(hour=17, minute=0, year=1900, month=1, day=1)

		# calculate total hours and add 30min lunch if worked more than 6hours
		self.workedtime = timedelta(0);
		for index, day in enumerate(self.time_duos):
			daily_total = timedelta(0)
			for time_duo in day:
				daily_total += Employee.calc_length(time_duo)
			if daily_total >= timedelta(hours=8, minutes=0):
				daily_total = timedelta(hours=8, minutes=30)
			elif daily_total > timedelta(hours=6):
				daily_total += timedelta(minutes=30)
			self.workedtime += daily_total

		# set other hours
		for row in init_array:
			if row[0] == "Sick Leave":
				self.sicktime = timedelta(hours=int(row[1]), minutes=int(row[2]))
			elif row[0] == "Vacation":
				self.vacationtime = timedelta(hours=int(row[1]), minutes=int(row[2]))

		self.totaltime = self.workedtime + self.vacationtime + self.sicktime

	def list_time(self):
		print("**************************************")
		print(self.name)
		print("-----------------")
		print("worked time: ", self.workedtime)
		print("sick time: ", self.sicktime)
		print("vacation time: ", self.vacationtime)
		print("overtime: ", self.overtime)
		print("-----------------")
		for index, date in enumerate(self.time_duos):
			if date:
				print(self.day_dict[index])
				for time in date:
					print(time)
				print("-----------------")

	def fix_day(self, day_index):
		input_validation = False

		# print(self.day_dict[day_index], "for employee ", self.name, " has an odd number of entries!")
		# print("The last entry is at ", self.times[day_index][-1].time(), ".")
		# print("Enter a time to clock this employee out. (note: Should be after the previous entry. Use format 15:23.)")

		while input_validation == False:
			# input_time = str(input("# "))
			text, ok = QInputDialog.getText(None, 'Input Dialog', self.day_dict[day_index] + ' for employee ' + self.name \
				+ " has an odd number of entries! \nThe last entry is at " + str(self.times[day_index][-1].time()) + \
				 ". \nEnter a time to clock this employee out. (note: Should be after the previous entry. Use format 15:23.)")
			input_time = str(text)
			try:
				converted_time = datetime.strptime(input_time, '%H:%M');
				if converted_time > self.times[day_index][-1]:
					input_validation = True
			except:
				QMessageBox.warning(None, "Warning", "Invalid input. Try again.")
		
		self.times[day_index].append(converted_time)

	@staticmethod
	def calc_length(time_duo):
		return time_duo[1] - time_duo[0]

class App(QWidget):
	def __init__(self):
		super().__init__()
		
		self.initUI()

		self.employees_raw = []
		self.employee_current = []
		self.employees = []

		self.current_file = ""
		self.current_folder = ""
		
	def initUI(self):
		self.layout = QVBoxLayout()
		
		self.setGeometry(300, 300, 160, 130)
		self.setWindowTitle('Timecard Processor')
		self.setWindowIcon(QIcon('web.png'))   

		file_button = QPushButton("Select input file", self)
		file_button.clicked.connect(self.show_file_dialog)

		folder_button = QPushButton("Select output folder", self)
		folder_button.clicked.connect(self.show_folder_dialog)

		self.convert_button = QPushButton("Convert", self)
		self.convert_button.setEnabled(False)
		self.convert_button.clicked.connect(self.convert)

		self.layout.addWidget(file_button)
		self.layout.addWidget(folder_button)
		self.layout.addWidget(self.convert_button)

		self.setLayout(self.layout)
	
		self.show()

	def convert(self):
		self.convert_button.setText("Working...")

		with open(self.current_file) as csvfile:
			csvreader = csv.reader(csvfile, skipinitialspace=True, \
				delimiter=",", quoting=csv.QUOTE_NONE)
			for row in csvreader:
				if any(field.strip() for field in row):
					if row[0] == "-----------------------------------------":
						self.employees_raw.append(self.employee_current)
						self.employee_current = []
					else:
						self.employee_current.append(row)

		for employee_data in self.employees_raw:
			self.employees.append(Employee(employee_data))

		# for employee in self.employees:
			# employee.list_time()

		self.write_csv()

		self.convert_button.setText("Done!")

		self.current_file = ""
		self.current_folder = ""

		self.employees_raw = []
		self.employee_current = []
		self.employees = []

		self.convert_button.setEnabled(False)

	def show_file_dialog(self):
		fname = QFileDialog.getOpenFileName(None, 'Open file', '/home', "csv(*.csv)")
		self.current_file = fname[0]
		if self.current_file and self.current_folder:
			self.convert_button.setEnabled(True)
			self.convert_button.setText("Convert")

	def show_folder_dialog(self):
		fname = QFileDialog.getExistingDirectory(None, 'Select directory')
		self.current_folder = fname
		if self.current_file and self.current_folder:
			self.convert_button.setEnabled(True)
			self.convert_button.setText("Convert")

	def write_csv(self):
		with open(self.current_folder + '/output.csv', mode='w') as outputfile:
			csvwriter = csv.writer(outputfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			csvwriter.writerow(["", "Employee's name", "Hours", "Minutes", "CyberPay", "Holiday", "Sick", "Vacation", "Overtime", "Total"])

			totals = ["Totals", "", 0, 0, 0, 0, 0, 0, 0, 0]

			for index, employee in enumerate(self.employees):
				worked_seconds = employee.workedtime.seconds;

				hours = employee.workedtime.days * 24 + employee.workedtime.seconds // 3600
				minutes = (employee.workedtime.seconds // 60) % 60

				# calculate row
				calc = [index + 1, \
						employee.name, \
						hours, \
					 	minutes , \
					 	hours + round(minutes / 60, 2), \
					 	0, \
					 	round(employee.sicktime.days * 24 + employee.sicktime.seconds / 3600, 2), \
					 	round(employee.vacationtime.days * 24 + employee.vacationtime.seconds / 3600, 2), \
					 	round(employee.overtime.days * 24 + employee.overtime.seconds / 3600, 2), \
					 	round(employee.totaltime.days * 24 + employee.totaltime.seconds / 3600, 2)]

				csvwriter.writerow(calc)

				# add row to totals						
				totals[2] += calc[2]
				totals[3] += calc[3]
				totals[4] += calc[4]
				totals[5] += calc[5]
				totals[6] += calc[6]
				totals[7] += calc[7]
				totals[8] += calc[8]
				totals[9] += calc[9]

			strings = ["Totals", ""]

			# truncate totals
			for index, i in enumerate(totals[2:]):
				strings.append("%.2f" % i)

			csvwriter.writerow(strings)
		
if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = App()
	sys.exit(app.exec_())