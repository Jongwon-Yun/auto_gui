# coding=<utf-8>
# 당면했던 문제들 : tk.frame의 범위 바깥의 영역에서 발생하는 마우스 클릭 이벤트를 처리하고 싶었음 -> tk.bind => frame안에서 발생하는 것만 처리
# => 모니터 화면 크기를 가진 tk.frame을 새로 하나 더 만들어 그 frame안에서 동작하는 것을 확인하였으나 프로그램이 깔끔하지 못하다는 점에서 다른 방향으로 해결하고자 하였다.
# => pynput의 패키지 안에 있는 mouse 모듈을 활용하기로 결정 -> 이벤트 리스너 종료를 선언하지 않으면 오류가 발생하였다.
# file read, write를 사용하면 기존에 지정했던 데이터 타입이 str로 바뀌어 다시 형변환을 해야한다는 문제가 있었다.
# => json모듈을 활용하였다. pickle이란 모듈도 있었지만 추후 확장성을 생각해서 json을 이용하기로 하였다.
# pynput v.1.7.2와 pyinstaller는 호환성(?)문제로 오류를 일으킨다. => pynput v.1.6.8로 다운그레이드해서 오류를 해결하였다.(또한 exit함수가 먹히지 않았다.)

# 기본값 설정 후 파일 실행 시 self.added_list가 0으로 초기화 되어 저장된 값들이 새롭게 추가되는 값들보다 뒤늦게 실행되는 논리 오류 발생

# 자동으로 무한 반복을 하게 되면 메모리 스택에 과부하가 생겨 오류가 발생하는 듯하다. 스택에서 실행되어 없어지는 것과 쌓이는 속도가 밸런스가 맞아야 제대로 동작할 것이라 생각된다.

import json
import time
import tkinter as tk
from tkinter import filedialog as fd
import tkinter.ttk as ttk
from tkinter import *
from queue import Queue
import sys
sys.path.append('C:/Users/JONGWON YUN/AppData/Local/Programs/Python/Python37/Lib/site-packages')
sys.path.append('C:/Users/JONGWON YUN/AppData/Roaming/Python/Python37/site-packages')
import pyautogui as ag
from pynput import mouse

queue = Queue()
def on_click(x, y, button, pressed):
    if pressed == True:
        queue.put((x,y))                                                    # 큐에 마우스 좌표 넣어줌
    else:                                                                   # listener가 종료되는 경우를 명시 안하면 계속 event가 실행되기 때문에 오류 발생
        return False

function_list = ["click", "double click", "auto_typing"]                    # 기능 리스트
order_dict = dict()                                                         # 명령어를 담는 딕셔너리

"""
pack과 grid는 같은 window안에서 사용할 수 없었음.
"""


# def get_point():
#     print(ag.position().x,ag.position().y)

def click_func(tuple_type):
    if tuple_type[3]:
        while True:
            ag.click(tuple_type[1])
    else:
        for i in range(int(tuple_type[2])):
            ag.click(tuple_type[1])

def dc_func(tuple_type):
    if tuple_type[3]:
        while True:
            ag.doubleClick(tuple_type[1])
    else:
        for i in range(int(tuple_type[2])):
            ag.doubleClick(tuple_type[1])

class Application(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.grid()
        self.create_widgets()
        self.added_list = 0                                                                         # 명령 추가 횟수
        self.default_load()                                                                         # default setting 가져오는 함수 실행
        if self.de_set != '':
            with open(self.de_set, "r") as file:
                    loaded_data = json.load(file)
                    self.added_list = len(loaded_data)
                    for i in loaded_data:
                        self.check_box.insert(loaded_data.index(i), i)
                        self.check_box.grid(row=2, column=1, columnspan=2,sticky="W")

    def create_widgets(self):

        self.func_label = tk.Label(self, text="기능")
        self.func_label.grid(row=0,column=0)

        self.auto_or_not = ttk.Checkbutton(self, text = "auto", variable = auto_check, onvalue=1, offvalue=0)                      # 자동반복 기능 여부를 확인하는 check_button
        self.auto_or_not.grid(row = 0, column = 4)


        self.specific_click_number_label = tk.Label(self, text= "반복횟수")
        self.specific_click_number_label.grid(row=1,column=0)
        
        self.specific_click_number = tk.Spinbox(self, from_ = 1, to = 1000)                                 # 반복횟수 지정 칸
        self.specific_click_number.grid(row = 1, column = 2)

        self.del_button_selected  = tk.Button(self, text="삭제", command = self.delete_selected)
        self.del_button_selected.grid(column=4, sticky="W")

        self.function_list = ttk.Combobox(self, height=5, width=17,values=function_list, state="readonly")  # 루틴 리스트   readonly를 사용하여 읽기 전용으로 하였음
        self.function_list.grid(row=0, column=1, columnspan=2,sticky="W")

        self.add_routine = tk.Button(self, text="Routine 추가", command = self.add)   # 루틴 추가하는 버튼
        self.add_routine.grid(row=0, column=3, sticky="W")

        self.text_label = tk.Label(self, text="타이핑")
        self.text_label.grid(row=2, column=0)

        self.text_box = tk.Text(self, width=20,height =10)                          # 루틴 작성 텍스트 상자
        self.text_box.grid(row=2, column=1, columnspan=2, sticky="W")

        self.save_routine = tk.Button(self, text="저장", command=self.save)           # 루틴 저장 버튼
        self.save_routine.grid(row=2, column=3,sticky="SW")

        self.execute = tk.Button(self, text="실행", command=self.excution)            # 루틴 실행 버튼
        self.execute.grid(row=3, column=3, sticky="SW")

        self.default_set = tk.Button(self, text="기본값 설정", command=self.default_setting)     # 기본 파일 설정
        self.default_set.grid()

        self.check_label = tk.Label(self,text="루틴 목록")
        self.check_label.grid(row=2, column=0)

        self.check_box = tk.Listbox(self, selectmode="extended", height=10)            # 루틴 확인 리스트

        # self.guide1 = tk.Label(self, text="※필독_사용방법※")
        # self.guide2 = tk.Label(self, text="1. 프로그램 실행 시 최초로 default.txt가 생성됩니다.")
        # self.guide3 = tk.Label(self, text="2. 실행 원하는 기능을 선택하시고 routine추가를 클릭해주세요.")
        # self.guide4 = tk.Label(self, text="3. click, double_click의 경우, routine추가를 클릭하고 나서 자동으로 클릭되길 원하는 지점을 클릭해주세요.")
        # self.guide5 = tk.Label(self, text="4. auto_typing의 경우, auto_typing을 선택하시고 공란에 typing되길 원하는 글자를 입력하신 후 routine추가를 클릭해주세요.")
        # self.guide6 = tk.Label(self, text="5. 자동 반복되길 원하는 순서대로 routine을 추가한 뒤, 실행버튼을 누르시면 실행이 됩니다.")
        # self.guide7 = tk.Label(self, text="6. 저장을 할 때에는 확장자 명을 json으로 해주세요.(중요!!!) 그리고 기본값 설정으로 저장된 json 타입의 파일을 이용해서 설정해두었던 기능을 유지할 수 있습니다.")
        # self.guide1.grid(sticky="w", row=4,columnspan=5)
        # self.guide2.grid(sticky="w", row=5,columnspan=5)
        # self.guide3.grid(sticky="w", row=6,columnspan=6)
        # self.guide4.grid(sticky="w", columnspan=5)
        # self.guide5.grid(sticky="w", columnspan=5)
        # self.guide6.grid(sticky="w", columnspan=5)
        # self.guide7.grid(sticky="w")

    def default_load(self):                                                            # 지정한 default setting 함수 불러오는 기능 최초에 한 번 default.txt가 없으므로 오류가 발생한다.
        # with open('default.txt', 'r') as file:                                       # 그래서 FileNotFoundError를 처리하기 위해 예외를 두어 오류를 해결하였다.
        #     self.de_set = file.read()
        try:
            with open('default.txt', 'r') as file:
                self.de_set = file.read()
        except FileNotFoundError:
            with open('default.txt', 'w') as file:
                file.write('')
                self.de_set = ''

    def delete_selected(self):
        self.check_box.delete(tk.ANCHOR)


    def add(self):                                                                      # routine을 추가하는 함수
        """
        함수 실행 시 비어 있는 확인 리스트에 선택한 루틴 리스트를 추가한다.
        """
        if "click" in self.function_list.get():
            # get_point()
            # win.bind("<Button-1>", get_point)
            with mouse.Listener(on_click=on_click) as listener:
                listener.join()
            value = queue.get()
            order_dict[self.added_list]=value
        else:
            value = self.text_box.get("1.0","end")
            order_dict[self.added_list]=value

        self.check_box.insert(self.added_list, (self.function_list.get(), value, self.specific_click_number.get(), auto_check.get()))
        self.check_box.grid(row=2, column=1, columnspan=2,sticky="W")
        self.added_list += 1

    def save(self):                                                 # 파일을 저장하는 기능
        print(type(self.check_box))
        x = fd.asksaveasfile(mode="w")                              # 다른이름으로 저장
        with open(x.name,"w") as file:
            json.dump(self.check_box.get(0,"end"),file)

    def load(self):                                                 # 파일을 불러오는 기능
        x = fd.askopenfile(mode="r")                                # 파일 불러오는 창
        with open(x.name,"r") as file:
            loaded_data = json.load(file)
            for i in loaded_data:
                self.check_box.insert(loaded_data.index(i),i)
                self.check_box.grid()

    def default_setting(self):                                      # default set을 위한 setting하는 기능
        x = fd.askopenfile(mode="r")
        with open("default.txt", 'w') as file:
            file.write(x.name)

    def excution(self):                                             # 실행하는 기능
        for i in self.check_box.get(0,"end"):
            if i[0] == "click":
                click_func(i)
            elif i[0] == "double click":
                dc_func(i)
            else:
                ag.typewrite(i[1])                                          # enter가 자동으로 쳐짐
            time.sleep(1)

root = tk.Tk()
auto_check = IntVar()
root.title("auto_login_system")
root.geometry("400x800")
app = Application(master=root)
menubar = tk.Menu(root)
filemenu = tk.Menu(menubar)
filemenu.add_command(label="Open", command=app.load)
filemenu.add_command(label="Save", command=app.save)
# filemenu.add_command(label="Exit", command=exit)
menubar.add_cascade(label="File", menu=filemenu)
root.config(menu=menubar)
app.mainloop()