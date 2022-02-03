import json
import tkinter as tk
from datetime import datetime

class Management_System():
    def __init__(self, file, font):
        self.font = font
        self.file = file
        self.students = []
        self.days = []
        self.presences = []
        self.current_day = datetime.now().date()
        self.read()
    
    def read(self):
        with open(self.file, "r") as f:
            json_string = json.load(f)
        for student in json_string["students"]:
            self.students.append(Student(student))
        for day in json_string["days"]:
            self.days.append(Day(day))
        for presence in json_string["presences"]:
            self.presences.append(Presence(presence))
        self.check_days()
    
    def write(self):
        temp_dict = {"students":[], "days":[], "presences":[]}
        student_dict = temp_dict["students"]
        for student in self.students:
            student_dict.append({})
            student_dict[-1]["id"] = student.id
            student_dict[-1]["last_name"] = student.last_name
            student_dict[-1]["first_name"] = student.first_name
            student_dict[-1]["class"] = student.school_class

        day_dict = temp_dict["days"]
        for day in self.days:
            day_dict.append({})
            day_dict[-1]["week"] = day.week
            day_dict[-1]["week_day"] = day.week_day
            day_dict[-1]["date"] = day.date
        
        presence_dict = temp_dict["presences"]
        for presence in self.presences:
            presence_dict.append({})
            presence_dict[-1]["student_id"] = presence.student_id
            presence_dict[-1]["date"] = presence.date
            presence_dict[-1]["status"] = presence.status
            presence_dict[-1]["start_time"] = presence.start_time
            presence_dict[-1]["end_time"] = presence.end_time
        
        with open(self.file, "w") as f:
            f.write(json.dumps(temp_dict))

    def check_days(self):
        today_in_days = False
        for day in self.days:
            if day.date == str(self.current_day):
                today_in_days = True
        if not today_in_days:
            self.days.append(Day({"week":str(self.current_day.isocalendar()[1]), "week_day":int(self.current_day.isocalendar()[2]), "date":str(self.current_day)}))
            for student in self.students:
                self.presences.append(Presence({"student_id":student.id, "date":self.days[-1].date, "status":"Pending", "start_time":"", "end_time":""}))

    def show(self):
        window = GUI(self.students, self.days, self.presences, self.current_day, self.font)
        self.write()

    def __str__(self):
        return ', '.join([str(s) for s in self.students])

class GUI():
    def __init__(self, students, days, presences, current_day, font):
        self.students = students
        self.days = days
        self.presences = presences
        self.current_day = str(current_day)
        self.font = font
        self.pending_sorting_mode = "class"

        self.week_days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

        self.current_presences = [p for p in self.presences if p.date == self.current_day]

        self.window = tk.Tk()
        self.window.title("Student Management Program")

        self.list_and_action_frames = tk.Frame(master=self.window)

        self.pending_offset = 0
        self.pending_size = 10

        self.pending_student_labels = []
        self.pending_student_label_button_frames = []
        self.pending_student_actions = []
        self.pending_student_scroll_buttons = []

        self.pending_frame = tk.Frame(master=self.list_and_action_frames)
        self.pending_students_list_frame = tk.Frame(master=self.pending_frame)
        self.pending_students_scroll_frame = tk.Frame(master=self.pending_students_list_frame)
        self.pending_students_scroll_page = tk.Label(self.pending_students_scroll_frame, text="", anchor="center")
        self.pending_students_scroll_page.config(font=(self.font, 10))
        self.pending_students_scroll_page.pack(side=tk.RIGHT)
        self.pending_student_title = tk.Label(self.pending_frame,text="", anchor="center")
        self.pending_student_title.config(font=(self.font, 16))
        self.pending_student_title.pack(pady=10)
        self.pending_students_list_frame.pack(side=tk.LEFT, expand=True)
        self.pending_frame.pack(padx=10, pady=20, expand=True, anchor="ne")

        self.update_pending_students()

        self.all_sort_mode = "class"

        self.all_offset = 0
        self.all_size = 10

        self.all_students_labels = []
        self.all_students_scroll_buttons = []

        self.all_students_frame = tk.Frame(master=self.list_and_action_frames)
        self.all_students_title = tk.Label(self.all_students_frame, text="", anchor="center")
        self.all_students_title.config(font=(self.font, 16))
        self.all_students_title.pack(pady=10)
        self.all_students_scroll_frame = tk.Frame(master=self.all_students_frame)
        self.all_students_scroll_page = tk.Label(self.all_students_scroll_frame, text="", anchor="center")
        self.all_students_scroll_page.config(font=(self.font, 10))
        self.all_students_scroll_page.pack(side=tk.RIGHT)
        self.all_students_frame.pack()

        self.update_all_students()

        self.selected_student_presences_labels = []
        self.selected_student_info_frames = []
        self.selected_student_status = []
        self.selected_student_end_time_entry = []
        self.selected_student_end_time_button = []

        self.selected_student_frame = tk.Frame(master=self.window)
        self.selected_student_title = tk.Label(self.selected_student_frame, text=f"", anchor="center")
        self.selected_student_title.pack(pady=10)
        self.selected_student_frame.pack(padx=10, pady=30, side=tk.RIGHT, expand=True, anchor="nw")

        self.list_and_action_frames.pack(padx=10, pady=10, side=tk.LEFT, expand=True, anchor="ne")

        self.window.mainloop()

    def select_student(self, student):
        self.selected_student = student
        self.update_selected_student_frame()
    
    def update_selected_student_frame(self):
        self.selected_student_title.config(font=(self.font, 16), text=f"Selected Student: {self.selected_student.last_name} {self.selected_student.first_name}")
        for i in range(len(self.selected_student_presences_labels), 0, -1):
            self.selected_student_presences_labels[i-1].destroy()
        self.selected_student_presences_labels = []
        for i in range(len(self.selected_student_status), 0, -1):
            self.selected_student_status[i-1].destroy()
        self.selected_student_status = []
        for i in range(len(self.selected_student_end_time_entry), 0, -1):
            self.selected_student_end_time_entry[i-1].destroy()
        self.selected_student_end_time_entry = []
        for i in range(len(self.selected_student_end_time_button), 0, -1):
            self.selected_student_end_time_button[i-1].destroy()
        self.selected_student_end_time_button = []
        for i in range(len(self.selected_student_info_frames), 0, -1):
            self.selected_student_info_frames[i-1].destroy()
        self.selected_student_info_frames = []
        amount_of_correct_presences = 0
        self.selected_student_info_frames.append(tk.Frame(master=self.selected_student_frame))
        self.selected_student_presences_labels.append(tk.Label(self.selected_student_info_frames[-1], text="Overview", height=3, width=15))
        self.selected_student_status.append(tk.Label(self.selected_student_info_frames[-1], text="Status"))
        self.selected_student_end_time_entry.append(tk.Label(self.selected_student_info_frames[-1], text="End Time"))
        self.selected_student_end_time_button.append(tk.Label(self.selected_student_info_frames[-1], text=""))
        for i in range(len(self.presences), 0, -1):
            if amount_of_correct_presences == 10:
                break
            if self.presences[i-1].student_id == self.selected_student.id:
                amount_of_correct_presences += 1
                day = None
                for d in self.days:
                    if d.date == self.presences[i-1].date:
                        day = d
                self.selected_student_info_frames.append(tk.Frame(master=self.selected_student_frame))
                self.selected_student_presences_labels.append(tk.Label(self.selected_student_info_frames[-1], text=f"{self.week_days[day.week_day]}\n({day.date})", height=3, width=15))
                self.selected_student_status.append(tk.Label(self.selected_student_info_frames[-1], text=f"{self.presences[i-1].status}"))
                if self.presences[i-1].status == "Present" and self.presences[i-1].end_time == "":
                    self.selected_student_end_time_entry.append(tk.Entry(self.selected_student_info_frames[-1]))
                    self.selected_student_end_time_button.append(tk.Button(self.selected_student_info_frames[-1], text="Confirm", command=lambda presence=self.presences[i-1], end_time=self.selected_student_end_time_entry[-1]: self.set_end_time(presence, end_time)))
                else:
                    self.selected_student_end_time_entry.append(tk.Label(self.selected_student_info_frames[-1], text=f"{self.presences[i-1].end_time}"))
                    self.selected_student_end_time_button.append(tk.Label(self.selected_student_info_frames[-1], text=""))
        for sspl in self.selected_student_presences_labels:
            sspl.config(font=(self.font, 14))
            sspl.pack()
        for sss in self.selected_student_status:
            sss.config(font=(self.font, 12))
            sss.pack(anchor="w")
        for ssete in self.selected_student_end_time_entry:
            ssete.config(font=(self.font, 12))
            ssete.pack(anchor="w")
        for ssetb in self.selected_student_end_time_button:
            ssetb.config(font=(self.font, 12))
            ssetb.pack(anchor="w")
        for i, ssif in enumerate(self.selected_student_info_frames):
            if i == 0:
                ssif.pack(side=tk.LEFT)
                continue
            ssif.pack(side=tk.RIGHT)

    def set_end_time(self, presence, end_time_entry):
        end_time = end_time_entry.get()
        if end_time:
            presence.end_time = end_time
        else:
            current_time = datetime.now().time()
            presence.end_time = f"{'0' if current_time.hour < 10 else ''}{current_time.hour}:{'0' if current_time.minute < 10 else ''}{current_time.minute}"
        self.update_selected_student_frame()

    def update_pending_students(self):
        self.pending_students_scroll_frame.pack_forget()
        self.pending_students = []
        for p in self.current_presences:
            if p.status.lower() == "pending":
                for student in self.students:
                    if student.id == p.student_id:
                        self.pending_students.append(student)
                        break
        if self.pending_sorting_mode == "name":
            self.pending_students.sort(key=lambda x: x.last_name)
        self.pending_student_title.config(text=f"Pending - {len(self.pending_students)} Student{'s' if len(self.pending_students) != 1 else ''} remaining")
        for i in range(len(self.pending_student_labels), 0, -1):
            self.pending_student_labels[i-1].destroy()
        for i in range(len(self.pending_student_actions), 0, -1):
            self.pending_student_actions[i-1].destroy()
        for i in range(len(self.pending_student_label_button_frames), 0, -1):
            self.pending_student_label_button_frames[i-1].destroy()
        self.pending_student_label_button_frames = []
        self.pending_student_labels = []
        for i in range(self.pending_size*self.pending_offset, len(self.pending_students)):
            if i == self.pending_size*(self.pending_offset+1):
                break
            pending_student = self.pending_students[i]
            self.pending_student_label_button_frames.append(tk.Frame(self.pending_students_list_frame))
            self.pending_student_labels.append(tk.Label(self.pending_student_label_button_frames[-1], text=f"{str(pending_student)}", anchor="w", width=30, height=1))
        for i, psl in enumerate(self.pending_student_labels):
            psl.config(font=(self.font, 12))
            psl.bind('<Button-1>', lambda event, student=self.pending_students[i+self.pending_offset*self.pending_size]: self.select_student(student))
            psl.pack(side=tk.LEFT)

        self.pending_student_actions = []
        for i in range(self.pending_size*self.pending_offset, len(self.pending_students)):
            if i == self.pending_size*(self.pending_offset+1):
                break
            frame = self.pending_student_label_button_frames[i - self.pending_size*self.pending_offset]
            self.pending_student_actions.append(tk.Button(frame, text=f"Present", command=lambda student_id=pending_student.id, date=str(self.current_day), status="Present":self.update_status(student_id, date, status), height=1))
            self.pending_student_actions.append(tk.Button(frame, text=f"Not Present", command=lambda student_id=pending_student.id, date=str(self.current_day), status="Not Present":self.update_status(student_id, date, status), height=1))
        for i, psa in enumerate(self.pending_student_actions):
            psa.config(font=(self.font, 12))
            psa.pack(side=tk.LEFT)
        for pslbf in self.pending_student_label_button_frames:
            pslbf.pack()

        for i in range(len(self.pending_student_scroll_buttons), 0, -1):
            self.pending_student_scroll_buttons[i-1].destroy()
        self.pending_student_scroll_buttons = []
        if (self.pending_offset - 1) * self.pending_size >= 0:
            self.pending_student_scroll_buttons.append(tk.Button(self.pending_students_scroll_frame, text=f"Scroll Up", command=lambda increase=False: self.update_pending_offset(increase)))
        if (self.pending_offset + 1) * self.pending_size < len(self.pending_students):
            self.pending_student_scroll_buttons.append(tk.Button(self.pending_students_scroll_frame, text=f"Scroll Down", command=lambda increase=True: self.update_pending_offset(increase)))
        self.pending_students_scroll_page.config(text=f"Page {self.pending_offset+1}/{int(20/len(self.pending_students))+1}")
        for pssb in self.pending_student_scroll_buttons:
            pssb.pack(side=tk.LEFT)
        self.pending_students_scroll_frame.pack()

    def update_pending_offset(self, increase):
        if increase:
            self.pending_offset += 1
        else:
            self.pending_offset -= 1
        self.update_pending_students()
    
    def update_status(self, student_id, date, status):
        if date != str(self.current_day):
            for i in range(len(self.presences)):
                if self.presences[i].date == date and self.current_presences[i].student_id == student_id:
                    self.presences[i].status = status
                    break
        else:
            for i in range(len(self.current_presences)):
                if self.current_presences[i].student_id == student_id:
                    self.current_presences[i].status = status
                    break
        self.update_pending_students()
    
    def update_all_students(self):
        self.all_students_title.config(text=f"All - {len(self.students)} Student{'s' if len(self.students) != 1 else ''} remaining")
        self.all_students_scroll_frame.pack_forget()
        for i in range(len(self.all_students_labels), 0, -1):
            self.all_students_labels[i-1].destroy()
        self.all_students_labels = []
        if self.all_sort_mode == "class":
            self.students.sort(key=str)
        for i in range(self.all_size*self.all_offset, len(self.students)):
            if i == self.all_size*(self.all_offset+1):
                break
            self.all_students_labels.append(tk.Label(self.all_students_frame, text=f"{self.students[i]}"))
        for i, asl in enumerate(self.all_students_labels):
            asl.config(font=(self.font, 12))
            asl.bind('<Button-1>', lambda event, student=self.students[i+self.all_offset*self.all_size]: self.select_student(student))
            asl.pack()
        for i in range(len(self.all_students_scroll_buttons), 0, -1):
            self.all_students_scroll_buttons[i-1].destroy()
        self.all_students_scroll_buttons = []
        if (self.all_offset - 1) * self.all_size >= 0:
            self.all_students_scroll_buttons.append(tk.Button(self.all_students_scroll_frame, text=f"Scroll Up", command=lambda increase=False: self.update_all_offset(increase)))
        if (self.all_offset + 1) * self.all_size < len(self.students):
            self.all_students_scroll_buttons.append(tk.Button(self.all_students_scroll_frame, text=f"Scroll Down", command=lambda increase=True: self.update_all_offset(increase)))
        self.all_students_scroll_page.config(text=f"Page {self.all_offset+1}/{int(20/len(self.students))+1}")
        for pssb in self.all_students_scroll_buttons:
            pssb.pack(side=tk.LEFT)
        self.all_students_scroll_frame.pack()

    def update_all_offset(self, increase):
        if increase:
            self.all_offset += 1
        else:
            self.all_offset -= 1
        self.update_all_students()

class Student():
    def __init__(self, student_dict):
        self.id = student_dict["id"]
        self.first_name = student_dict["first_name"]
        self.last_name = student_dict["last_name"]
        self.school_class = student_dict["class"]

    def __str__(self):
        return f"{self.school_class}     {self.last_name} {self.first_name}"

class Day():
    def __init__(self, day_dict):
        self.week = day_dict["week"]
        self.week_day = day_dict["week_day"]
        self.date = day_dict["date"]
    
    def __str__(self):
        return f"Date: {self.date}, Week: {self.week}, Weekday: {self.week_day}"

class Presence():
    def __init__(self, presence_dict):
        self.student_id = presence_dict["student_id"]
        self.date = presence_dict["date"]
        self.status = presence_dict["status"]
        self.start_time = presence_dict["start_time"]
        self.end_time = presence_dict["end_time"]

m = Management_System("./students.json", "Arial")
m.show()