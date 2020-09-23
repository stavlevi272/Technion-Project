import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import csv
from collections import Counter
from itertools import chain
from sklearn.model_selection import train_test_split

data = pd.read_csv('data.csv')
# making data frame from csv file
data_df = pd.read_csv("data.csv")
data_df.columns = [c.replace(' ', '_') for c in data_df.columns]
data_df.columns = [c.replace('(', '') for c in data_df.columns]
data_df.columns = [c.replace(')', '') for c in data_df.columns]
print('data_df', data_df)

new_data = data[['Anon Student Id', 'Problem Name', 'Correct Step Duration (sec)', 'Error Step Duration (sec)','Correct First Attempt']]
Student_Id = new_data['Anon Student Id']
stud_dic = {i: [] for i in Student_Id}
print('stud_dic',stud_dic)
for i in range(new_data.shape[0]):
    stu_id = new_data.iloc[i]['Anon Student Id']
    stud_dic[stu_id].append(new_data.iloc[i]['Problem Name'])

def creat_data_dict(data_df, stud_dic):
    data_dict = {i: {'question': 0, 'first_attempt': 0} for i in stud_dic.keys()}
    for id, row in data_df.iterrows():
        stu_id = row.Anon_Student_Id
        question = row.Problem_Name
        first_attempt = row.Correct_First_Attempt
        data_dict[stu_id]['question'] = question
        data_dict[stu_id]['first_attempt'] = first_attempt
    return data_dict

data_dict = creat_data_dict(data_df, stud_dic)


res = list(set(val for dic in stud_dic.values() for val in dic))
print('res', len(res))
def delete_empty_rows(data_df):
    for i, row in data_df.iterrows():
        #print('row.Step_Duration_sec', row.Step_Duration_sec)
        #print()
        if i == 129 :
            print('type',type(row.Step_Duration_sec))
            print('find', row.Step_Duration_sec)
        if row.Step_Duration_sec == 'nan':
            data_df.drop(data_df.index[i])
            print('find' ,row.Step_Duration_sec)
delete_empty_rows(data_df)

def histograma(stud_dic):
    his ={ i : 0 for i in range(73)}
    for key, value in stud_dic.items():
        his[len(value)] += 1
    print(his)
    for i in range(73):
        if his[i]==0:
            del his[i]
    objects = his.keys()
    y_pos = np.arange(len(objects))
    performance = his.values()
    plt.bar(y_pos, performance, align='center', alpha=0.5, width=0.5)
    plt.xticks(np.arange(0, 1, step=0.6))
    plt.xticks(y_pos, objects)
    #plt.xlim(0,80)
    plt.xlabel('num_of_questions')
    plt.ylabel('num_of_student')
    plt.title('histogram of data')
    plt.show()
histograma(stud_dic)

def creat_rank(data_df, stud_dic):
    rank_dic ={i : 0 for i in stud_dic.keys()}
    for (idx, row) in data_df.iterrows():
        student_id = row.Anon_Student_Id
        if row.Correct_First_Attempt == 1:
            rank_dic[student_id] += 1
            time = row.Correct_Step_Duration_sec
        else:
            time = row.Error_Step_Duration_sec
        if time != 0:
            rank_dic[student_id] += 1/time
        else:
            print('student_id', student_id)
    sum = 0
    for key, value in stud_dic.items():
        if rank_dic[key] < 0:
            rank_dic[key] = 0
        else:
            if np.isnan(rank_dic[key]):
                rank_dic[key] = 0
            rank_dic[key] = rank_dic[key] / len(value)
            sum += rank_dic[key]
    print('sum', sum)
    for key, value in stud_dic.items():
        rank_dic[key] = rank_dic[key] / sum
    return rank_dic
rank = creat_rank(data_df, stud_dic)
print('rank' , rank)

def find_most_close_friends(rank):
    list_closest = list()
    s1 =[]
    for i in range(0, 51):
        list_closest.append(1000)
        s1.append('')
    closest_dic = {i: s1 for i in rank.keys()}
    students_list = list(rank.keys())
    rank_list = list(rank.values())
    list_len = len(rank_list)
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
closest_dic = find_most_close_friends(rank)
print('closest_dic ', closest_dic)

def find_most_answered_question(closest_dic, stud_dic, data_dict):
    sum = 0
    count = 0
    print('stud_dic', stud_dic)
    stu_quest_dic = {i: [] for i in closest_dic.keys()}
    stu_friend_dic = {i : [] for i in closest_dic.keys()}
    for key, value in stud_dic.items():
        curr_max = 0
        max_quest = 0
        friend_list_max = []
        for i in range(len(value)):
            friend_list = []
            count = 0
            current_question = value[i]
            list_closest = closest_dic[key]
            for j in range(len(list_closest)):
                list_friend_question = stud_dic[list_closest[j]]
                # print('list_train_question',list_train_question)
                if current_question in list_friend_question:
                    count += 1
                    friend_list.append(list_closest[j])
            if count > curr_max:
                max_quest = current_question
                curr_max = count
                friend_list_max = friend_list
        if max_quest != 0:
            stu_quest_dic[key].append(max_quest)
            stu_quest_dic[key].append(curr_max)
            stu_friend_dic[key] = friend_list_max
            if data_dict[key]['question'] == max_quest and data_dict[key]['first_attempt'] == 0:
                count += 1
    for key, value in stu_quest_dic.items():
        if value == 0:
            sum += 1
    print('sum', sum)
    print('count',count)
    return stu_quest_dic , stu_friend_dic

stu_quest_dic, stu_friend_dic = find_most_answered_question( closest_dic, stud_dic, data_dict)


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
print('stu_quest_dic', stu_quest_dic)
print('stu_friend_dic', stu_friend_dic)
print('len', len(stu_quest_dic.keys()))


def create_column_question_rank(data_df):
    data_df['Question_rank'] = data_df['Correct_First_Attempt'] + 1 / (data_df['Step_Duration_sec'])

create_column_question_rank(data_df)


def avg_rank_for_most_answered_question(stu_quest_dic, stu_friend_dic, data_df):
    rank_question_dic = {i: [] for i in stu_quest_dic.keys()}
    for (idx, row) in data_df.iterrows():
        curr_student_id = row.Anon_Student_Id
        curr_question = row.Problem_Name
        curr_quest_rank = row.Question_rank
        if curr_quest_rank == 0:
            print ('zero rank',curr_student_id )
        l = [curr_question, curr_quest_rank]
        if curr_student_id in stu_quest_dic.keys():
            rank_question_dic[curr_student_id].append(l)

    print('rank_question_dic', rank_question_dic)
    result_dic = {i: {'my_rank' : 0,'friends_rank': 0} for i in stu_quest_dic.keys()}
    for key, value in stu_quest_dic.items():
        if len(value) == 0:
            continue
        stu_id = key
        question_num = value[0]
        friend_list = stu_friend_dic[stu_id]
        friend_quest_rank = 0
        my_quest_rank = 0
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
        if key == 'nA15DeLBE1':
            print('11 friend_quest_rank' , friend_quest_rank)
            print('value[1]', value[1])
        result_dic[key]['friends_rank'] = friend_quest_rank / value[1]
    return result_dic
result_dic = avg_rank_for_most_answered_question(stu_quest_dic, stu_friend_dic, data_df)
print('result_dic', result_dic)

def calcuate_estimate_error(result_dic):
    count = 0
    sum = 0
    for key, value in result_dic.items():
        count += 1
        d = value['friends_rank'] - value['my_rank']
        sum += d*d
    print('sum', sum)
    print('count', count)
    rmse = np.sqrt(sum/ (count))
    print('rmse', rmse)
calcuate_estimate_error(result_dic)

def recommend_result(closest_dic, stud_dic, result_dic):
    reccomended_question = {i: [] for i in result_dic.keys()}
    for key in result_dic.keys():
        my_question_list = stud_dic[key]
        my_friends_list = closest_dic[key]
        for i in range(0 , len(my_friends_list) -30):
            current_friend = my_friends_list[i]
            current_friend_questins = stud_dic[current_friend]
            for j in current_friend_questins:
                if j not in reccomended_question[key] and j not in my_question_list:
                    reccomended_question[key].append(j)
    return reccomended_question

reccomended_question = recommend_result(closest_dic, stud_dic, result_dic)
print('reccomended_question', reccomended_question)



