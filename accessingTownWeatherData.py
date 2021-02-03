#!/usr/bin/python3

# import modules
import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import threading

class CurlWeaData:

    # initiate variables
    def __init__(self, town_id, ):
        # url of weather webpage
        self.url = "http://forecast.weather.com.cn/town/weather1dn/{}.shtml#input".format(town_id)
        self.file_addr = "/root/Documents/py/accessingWeaData/"
        self.page = None  # weather webpage
        self.soup = None  # weather soup
        self.title = None  # waether title
        self.script = None  # waether script
        self.date_time = None  # present date
        self.result_dic = {
            # data: None,
            "DATETIME": None, "DESCRIPTION": None, "TEMP(C)": None, 
            "HUMITITY": None, "WIND": None, "WINDLEVEL": None, 
        }  # temporary dictionary
        # elements of data
        self.elements = [
            # [name, tag, attrs, attrs_value, is1ormore, seq, list_seq, ]
            ["DESCRIPTION", "div", "class", "weather dis", 0, None, None, ], 
            ["TEMP(C)", "span", "class", "temp", 0, None, None, ], 
            ["HUMITITY", "p", "span", None, 1, 1, 1, ], 
            ["WIND", "p", "span", None, 1, 0, 0, ], 
            ["WINDLEVEL", "p", "span", None, 1, 0, 1, ], 
        ]
        # log of program
        self.log = {
            "TIME": None,
            "ACTION": None,
        }

    # define a method for making request and soup
    def make_request_and_soup(self):
        # make the request
        count = 1
        while count < 3:
            try:
                print(">     trying making request...")
                self.page = requests.get(self.url)
                break
            except ConnectionError:
                count += 1
                continue
        if count < 3:
            # make the soup
            self.soup = BeautifulSoup(self.page.content, "html.parser")
            # get the title of url webpage
            self.title = self.soup.title.contents[0].split("】")[0][1:]
            return True
        else:
            return False
    
    def get_target_script(self):
        # get data block from soup 
        self.script = self.soup.find_all("div", attrs={"class": "todayLeft"}, )
        
    def get_target_data(self, name, tag, attrs, attrs_value, is1ormore, seq, list_seq):
        for item_i in self.script:
            # get data according to different item
            if is1ormore:
                # print(item_i.find_all(tag)[seq].find(attrs).text.split(" ")[list_seq])
                self.result_dic[name] = item_i.find_all(tag)[seq].find(attrs).text.split(" ")[list_seq]
            else:
                # print(item_i.find(tag, attrs={attrs: attrs_value}).text)
                self.result_dic[name] = item_i.find(tag, attrs={attrs: attrs_value}).text
    
    def write_csv(self, content, target_file, ):
        # try reading csv from original csv file as original data
        target = "{}{}".format(self.file_addr, target_file)
        try:
            ori_data = pd.read_csv(target, dtype="str", )
        except FileNotFoundError:
            ori_data = pd.DataFrame([])
        # combine original data and current data
        cur_data = pd.concat([content, ori_data], ignore_index=True, )
        # write data into csv file
        cur_data.to_csv(target, index=False, )
    
    def main(self):
        print("\n> GO...")
        # get present date and time
        date_n_time = str(datetime.datetime.now()).split()
        self.date_time = date_n_time[0].replace("-", "") + date_n_time[1].split(".")[0].replace(":", "")
        self.log["TIME"] = self.date_time
        # go on if curl webpage succeeded, 
        # or set log as filed
        if self.make_request_and_soup():
            self.log["ACTION"] = "ACCESSING SUCCEEDED"
            self.get_target_script()
            self.result_dic['DATETIME'] = self.date_time
            for item_j in self.elements:
                self.get_target_data(
                    # using [*] to set all of list elements as function arguments
                    *item_j
                )
                # uncomment following statement to enable "Press any key to continue..."
                # temp = input("Press any key to continue...")
            # Write data
            print(">     writing data to csv file...")
            self.write_csv(
                pd.DataFrame(self.result_dic, index=[0], ),
                "{}_DATA.csv".format(self.title),
            )
        else:
            self.log["ACTION"] = "ACCESSING FAILED"
        # Write log
        self.write_csv(
            pd.DataFrame(self.log, index=[0], ),
            "{}_LOG.csv".format(self.title),
        )
        print("> {} {}!!!".format(self.title, self.log["ACTION"]))

# Start with town id
town_ids = [
    # Adding city id here, and add comments right after it
    # id        ,  # Detailed Address
    101131204003,  # Qianshan, Yiwu, Xijiang
    101240210009,  # Duobao, Jiujiang, Jiangxi
    101110101014,  # WenyiRoad, Beilin, Xi'an, Shaanxi
]

def start_curling(town_id):
    run = CurlWeaData(town_id)
    run.main()

for town_id_i in town_ids:
    threading.Thread(target = start_curling, args = (town_id_i, )).start()
