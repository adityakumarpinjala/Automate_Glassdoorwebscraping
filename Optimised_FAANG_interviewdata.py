# Importing Necessary Libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlalchemy, pymysql
from sqlalchemy import create_engine
import mysql.connector
from mysql.connector import Error
import configparser
import os

# Database Connection
def fetch_variables():
    thisfolder = os.path.dirname(os.path.abspath(__file__))
    initfile = os.path.join(thisfolder, 'test.env')
    config = configparser.ConfigParser()
    config.read(initfile)
    global host1, user1, passwd1,max_page
    host1 = config.get('DB', 'DB_HOST')
    user1 = config.get('DB', 'DB_USERNAME')
    passwd1 = config.get('DB', 'DB_PASSWORD')
    max_page=config.get('DB','MAX_PAGENATION')

def db_connect_extraction():
    mydb1 = mysql.connector.connect(host=host1, user=user1, passwd=passwd1)
    mycursor = mydb1.cursor()
    try:
        mycursor.execute("Create database Glassdoor_Interviews")
    except Error as e:
        print("Database Created already!")
    FAANG_Companies = [{('Amazon', "E6036", 'amazon_interviewdetails')},{('Facebook', 'E40772', 'facebook_interviewdetails')},{('apple', 'E1138', 'apple_interviewdetails')},{('Netflix', 'E11891', 'netflix_interviewdetails')},{('Google', 'E9079', 'google_interviewdetails')}]
    for i in FAANG_Companies:
        List = []
        mydb1 = mysql.connector.connect(host=host1, user=user1, passwd=passwd1,database="Glassdoor_Interviews")
        engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}".format(user=user1, pw=passwd1, host=host1,db="glassdoor_interviews"))
        mycursor = mydb1.cursor()
        for Company, ID, j in i:
            table_name = j
            _SQL = """SHOW TABLES"""
            mycursor.execute("show tables")
            results = mycursor.fetchall()
            results_list = [item[0] for item in results]

            if table_name not in results_list:
                print("Table",table_name, 'was not found! in the DB')
                for i in range(1, int(max_page)):
                    URL = 'https://www.glassdoor.co.in/Interview/' + Company + "-Interview-Questions-" + ID + '_P' + str(i) + '.htm?sort.sortType=RD&sort.ascending=false'
                    headers = {'User-Agent': "Mozilla/5.0 (FAANG_Companies1; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"}
                    response = requests.get(URL, headers=headers)
                    data = BeautifulSoup(response.text, 'lxml')
                    containers = data.findAll("li", class_="empReview cf")
                    for container in containers:
                        Applied_Dgn = container.find('span', class_="reviewer").text
                        Applied_Dt = container.find('time', class_='date subtle small').text
                        Applied_Dt = pd.to_datetime(Applied_Dt)
                        Interview_Result = container.findAll("span", class_="middle")[0].text
                        try:
                            Interview_Exp = container.findAll("span", class_="middle")[1].text
                        except:
                            Interview_Exp = "NA"
                        try:
                            Interview_Type = container.findAll("span", class_="middle")[2].text
                        except IndexError:
                            Interview_Type = "NA"
                        try:
                            Applied_loc = container.find('span', class_='authorLocation').text
                        except AttributeError:
                            Applied_loc = "NA"
                        Interview_Details = container.find("p",class_="interviewDetails continueReading interviewContent mb-xsm").text
                        List.append([Company, Applied_Dgn, Applied_Dt, Interview_Result, Interview_Exp, Interview_Type,Applied_loc,Interview_Details])
                FAANG_Interviews = pd.DataFrame(List, columns=['Company', 'Applied_Dgn', 'Applied_Dt', 'Interview_Result','Interview_Exp', 'Interview_Type', 'Applied_loc','Interview_Details'])
                FAANG_Interviews.to_sql(j,con=engine, if_exists='fail', chunksize=1000, index=False)

            else:
                print(table_name, 'was found!')
                Max_date = pd.read_sql('select max(Applied_Dt) from (%s)'%(j), con=mydb1)
                Database_MaxDate = Max_date['max(Applied_Dt)'][0]
                print(Database_MaxDate)
                List = []
                count=1
                while(count>0):
                    for i in range(count):
                        URL = 'https://www.glassdoor.co.in/Interview/' + Company + "-Interview-Questions-" + ID + '_P' + str(i) + '.htm?sort.sortType=RD&sort.ascending=false'
                        headers = {'User-Agent': "Mozilla/5.0 (FAANG_Companies1; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"}
                        response = requests.get(URL, headers=headers)
                        data = BeautifulSoup(response.text, 'lxml')
                        containers = data.findAll("li", class_="empReview cf")
                        for container in containers:
                            Applied_Dgn = container.find('span', class_="reviewer").text
                            Applied_Dt = container.find('time', class_='date subtle small').text
                            Applied_Dt = pd.to_datetime(Applied_Dt)
                            Interview_Result = container.findAll("span", class_="middle")[0].text
                            try:
                                Interview_Exp = container.findAll("span", class_="middle")[1].text
                            except IndexError:
                                Interview_Exp = "NA"
                            try:
                                Interview_Type = container.findAll("span", class_="middle")[2].text
                            except IndexError:
                                Interview_Type = "NA"
                            try:
                                Applied_loc = container.find('span', class_='authorLocation').text
                            except AttributeError:
                                Applied_loc = "NA"
                            Interview_Details = container.find("p",class_="interviewDetails continueReading interviewContent mb-xsm").text
                            if Applied_Dt > Database_MaxDate:
                                List.append([Company, Applied_Dgn, Applied_Dt, Interview_Result, Interview_Exp, Interview_Type,Applied_loc,Interview_Details])
                                count+=1
                            else:
                                count=-1
                FAANG_Interviews = pd.DataFrame(List, columns=['Company', 'Applied_Dgn', 'Applied_Dt', 'Interview_Result','Interview_Exp', 'Interview_Type', 'Applied_loc','Interview_Details'])
                FAANG_Interviews.to_sql(j, con=engine, if_exists='append', chunksize=1000, index=False)

if __name__ == "__main__":
    fetch_variables()
    db_connect_extraction()

    


