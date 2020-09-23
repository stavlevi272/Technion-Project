import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import csv
from collections import Counter

data = pd.read_csv('data.csv')

new_data = data[['Anon Student Id', 'Problem Name', 'Correct Step Duration (sec)', 'Error Step Duration (sec)','Correct First Attempt']]
Student_Id = new_data['Anon Student Id']
student_dic = {i: [] for i in Student_Id}
first_attempt_dict = {i: [] for i in Student_Id}
for i in range(new_data.shape[0]):
    stu_id = new_data.iloc[i]['Anon Student Id']
    student_dic[stu_id].append(new_data.iloc[i]['Problem Name'])
    first_attempt_dict[stu_id].append({new_data.iloc[i]['Problem Name']:new_data.iloc[i]['Correct First Attempt']})


def histogram(student_dic):
    max_answer_question = 73
    hist = {i: 0 for i in range(max_answer_question)}
    for key, value in student_dic.items():
        hist[len(value)] += 1
    for i in range(max_answer_question):
        if hist[i] == 0:
            del hist[i]
    objects = hist.keys()
    y_pos = np.arange(len(objects))
    performance = hist.values()
    plt.bar(y_pos, performance, align='center', alpha=0.5, width=0.5)
    plt.xticks(np.arange(0, 1, step=0.6))
    plt.xticks(y_pos, objects)
    plt.xlabel('num_of_questions')
    plt.ylabel('num_of_student')
    plt.title('histogram of data')
    plt.show()
histogram(student_dic)


# making data frame from csv file
data_df = pd.read_csv("data.csv")
data_df.columns = [c.replace(' ', '_') for c in data_df.columns]
data_df.columns = [c.replace('(', '') for c in data_df.columns]
data_df.columns = [c.replace(')', '') for c in data_df.columns]

def create_rank(data_df, student_dic):
    rank_dic = {i: 0 for i in student_dic.keys()}
    for (idx, row) in data_df.iterrows():
        student_id = row.Anon_Student_Id
        if row.Correct_First_Attempt == 1:
            rank_dic[student_id] += 1
            time = row.Correct_Step_Duration_sec
        else:
            time = row.Error_Step_Duration_sec
        if time != 0:
            rank_dic[student_id] += 1/time
    sum = 0
    for key, value in student_dic.items():
        if rank_dic[key] < 0:
            rank_dic[key] = 0
        else:
            if np.isnan(rank_dic[key]):
                rank_dic[key] = 0
            rank_dic[key] = rank_dic[key] / len(value)
            sum += rank_dic[key]
    for key, value in student_dic.items():
        rank_dic[key] = rank_dic[key] / sum
    return rank_dic


rank = create_rank(data_df, student_dic)


## find the most closest students
def find_most_close(rank):
    list_closest = list()
    s1 = []
    for i in range(0, 51):
        list_closest.append(1000)
        s1.append('')
    closest_dic = {i: s1 for i in rank.keys()}
    students_list = list(rank.keys())
    rank_list = list(rank.values())
    list_len = len(rank_list)
    sum = 0
    for i in range(list_len):
        list_closest =[]
        for k in range(0, 51):
            list_closest.append(1000)
        for j in range(list_len):
            sum = 0
            if i != j:
                sum = abs(rank_list[i] - rank_list[j])
                curr_max = max(list_closest)
                if sum < curr_max:
                    index = list_closest.index(max(list_closest))
                    list_closest[index] = sum
                    closest_dic[students_list[i]][index] = students_list[j]
            else:
                continue
    return closest_dic
closest_dic = find_most_close(rank)

def find_most_answered_question(closest_dic, stud_dic, first_attempt_dict):
    sum = 0
    count = 0
    stu_quest_dic = {i: [] for i in closest_dic.keys()}
    stu_friend_dic = {i : [] for i in closest_dic.keys()}
    for key, value in stud_dic.items():
        curr_max = 0
        max_quest = 0
        friend_list_max = []
        temp1 = first_attempt_dict[key]
        for i in range(len(value)):
            friend_list = []
            count = 0
            current_question = value[i]
            for t in temp1:
                if list(t.keys())[0] == current_question:
                    first_attempt = t[current_question]
            list_closest = closest_dic[key]
            for j in range(len(list_closest)):
                list_friend_question = stud_dic[list_closest[j]]
                if current_question in list_friend_question:
                    count += 1
                    friend_list.append(list_closest[j])
            if count > curr_max and first_attempt != 0:
                max_quest = current_question
                curr_max = count
                friend_list_max = friend_list
        if max_quest != 0:
            stu_quest_dic[key].append(max_quest)
            stu_quest_dic[key].append(curr_max)
            stu_friend_dic[key] = friend_list_max
    for key, value in stu_quest_dic.items():
        if value == 0:
            sum += 1
    return stu_quest_dic , stu_friend_dic

stu_quest_dic, stu_friend_dic = find_most_answered_question(closest_dic, student_dic, first_attempt_dict)

def remove_empty_students(stu_quest_dic, stu_friend_dic):
    stu_quest_dic_new = {}
    stu_friend_dic_new = {}
    for key, val in stu_quest_dic.items():
        if len(val) == 0 or val[1] == 1 or val[1] == 2 or val[1] == 3 or val[1] == 4:
            continue
        else:
            stu_quest_dic_new[key] = val
            stu_friend_dic_new[key] = stu_friend_dic[key]
    return stu_quest_dic_new , stu_friend_dic_new

stu_quest_dic , stu_friend_dic = remove_empty_students(stu_quest_dic , stu_friend_dic)

def create_new_column(data_df):
    data_df['Question_rank'] = data_df['Correct_First_Attempt'] + 1 / (data_df['Step_Duration_sec'])
create_new_column(data_df)


def avg_grade_for_popular_question(stu_quest_dic, stu_friend_dic, data_df):
    rank_question_dic = {i: [] for i in stu_quest_dic.keys()}
    for (idx, row) in data_df.iterrows():
        curr_student_id = row.Anon_Student_Id
        curr_question = row.Problem_Name
        curr_quest_rank = row.Question_rank
        l = [curr_question, curr_quest_rank]
        if curr_student_id in stu_quest_dic.keys():
            rank_question_dic[curr_student_id].append(l)
    result_dic = {i: {'my_rank' : 0,'friends_rank': 0} for i in stu_quest_dic.keys()}
    for key, value in stu_quest_dic.items():
        if len(value) == 0:
            continue
        stu_id = key
        question_num = value[0]
        friend_list = stu_friend_dic[stu_id]
        friend_quest_rank = 0
        my_quest_rank = 0
        # find my rank
        temp_list = rank_question_dic[stu_id]
        for i in temp_list:
            if i[0] == question_num:
                my_quest_rank = i[1]
        result_dic[stu_id]['my_rank'] = my_quest_rank
        for j in range(len(friend_list)):
            temp_list = rank_question_dic[friend_list[j]]
            for k in temp_list:
                if k[0] == question_num:
                    friend_quest_rank += k[1]
        result_dic[key]['friends_rank'] = friend_quest_rank / value[1]
    return result_dic

result_dic = avg_grade_for_popular_question(stu_quest_dic, stu_friend_dic, data_df)


def calcuate_estimate_error(result_dic):
    count = 0
    sum = 0
    for key, value in result_dic.items():
        count += 1
        d = value['friends_rank'] - value['my_rank']
        sum += d*d
    rmse = np.sqrt(sum/ (count))
    print('RMSE:', rmse)

calcuate_estimate_error(result_dic)


def recommend_result(closest_dic , stud_dic, result_dic):
    recommended_question = {i: [] for i in result_dic.keys()}
    for key in result_dic.keys():
        my_question_list = stud_dic[key]
        my_friends_list = closest_dic[key]
        for i in range(0 ,len(my_friends_list)):
            current_friend = my_friends_list[i]
            current_friend_questions = stud_dic[current_friend]
            for j in current_friend_questions:
                if j not in recommended_question[key] and j not in my_question_list and len(recommended_question[key]) < 10:
                    recommended_question[key].append(j)
    return recommended_question

reccomended_question = recommend_result(closest_dic, student_dic, result_dic)



def write_file_result(reccomended_question):
    """writing lists to a csv files"""
    filename = 'results.csv'
    with open(filename, 'w') as csv_file:
        writer = csv.writer(csv_file, lineterminator='\n')
        fieldnames2 = ['Student_Id','Q1','Q2','Q3','Q4','Q5','Q6','Q7','Q8','Q9','Q10']
        writer.writerow(fieldnames2)
        for key, value in reccomended_question.items():
            writer.writerow([key,value[0],value[1], value[2],value[3], value[4],value[5],value[6], value[7], value[8], value[9]])
write_file_result(reccomended_question)

def print_results():
    print('Enter your Id:')
    x = input()
    print('Hello, ' + x)
    if x in reccomended_question.keys():
        print("your recommended questions are: \n", reccomended_question[x])
        print("Trust yourself, you know more than you think you do :)")
    else:
        print("sorry , you are not in the list, please try another Id")

print_results()
