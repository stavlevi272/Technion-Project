import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import csv
import csv_reader


def initial_dictionary_by_keys(keys):
    return {key: [] for key in keys}

csv_file = csv_reader.CsvReader()
data = csv_file.read_all_csv('data')
partial_data = csv_file.read_partial_csv(data, ['Anon Student Id', 'Problem Name', 'Correct Step Duration (sec)', 'Error Step Duration (sec)', 'Correct First Attempt'])
student_ids = partial_data['Anon Student Id']
student_answerd_problems = initial_dictionary_by_keys(student_ids)
students_first_attempt = initial_dictionary_by_keys(student_ids)
for row_index in range(partial_data.shape[0]):
    student_id = partial_data.iloc[row_index]['Anon Student Id']
    student_answerd_problems[student_id].append(partial_data.iloc[row_index]['Problem Name'])
    students_first_attempt[student_id].append({partial_data.iloc[row_index]['Problem Name']:partial_data.iloc[row_index]['Correct First Attempt']})
data_df = csv_file.read_all_csv('data')
data_df.columns = [c.replace(' ', '_') for c in data_df.columns]
data_df.columns = [c.replace('(', '') for c in data_df.columns]
data_df.columns = [c.replace(')', '') for c in data_df.columns]


def calculate_students_problems_rank(data_df, student_answerd_problems):
    students_problems_rank = {i: 0 for i in student_answerd_problems.keys()}
    for (idx, row) in data_df.iterrows():
        student_id = row.Anon_Student_Id
        if row.Correct_First_Attempt == 1:
            students_problems_rank[student_id] += 1
            time = row.Correct_Step_Duration_sec
        else:
            time = row.Error_Step_Duration_sec
        if time != 0:
            students_problems_rank[student_id] += 1/time
    sum = 0
    for key, value in student_answerd_problems.items():
        if students_problems_rank[key] < 0:
            students_problems_rank[key] = 0
        else:
            if np.isnan(students_problems_rank[key]):
                students_problems_rank[key] = 0
            students_problems_rank[key] = students_problems_rank[key] / len(value)
            sum += students_problems_rank[key]
    for key, value in student_answerd_problems.items():
        students_problems_rank[key] = students_problems_rank[key] / sum
    return students_problems_rank


students_problems_rank = calculate_students_problems_rank(data_df, student_answerd_problems)


def find_the_most_closest_friends_by_rank(students_problems_rank):
    closest_friends = list()
    initial_list = []
    for max_location in range(0, 51):
        closest_friends.append(1000)
        initial_list.append('')
    students_closest_friends = {student_id: initial_list for student_id in students_problems_rank.keys()}
    students = list(students_problems_rank.keys())
    problems_rank = list(students_problems_rank.values())
    num_of_students = len(students)
    for i in range(num_of_students):
        closest_friends = []
        for k in range(0, 51):
            closest_friends.append(1000)
        for j in range(num_of_students):
            if i != j:
                distance = abs(problems_rank[i] - problems_rank[j])
                current_max = max(closest_friends) 
                if distance < current_max:
                    max_location = closest_friends.index(max(closest_friends))
                    closest_friends[max_location] = distance
                    students_closest_friends[students[i]][max_location] = students[j]
            else:
                continue
    return students_closest_friends
students_closest_friends = find_the_most_closest_friends_by_rank(students_problems_rank)

def find_most_answered_problem(students_closest_friends, student_answerd_problems, students_first_attempt):
    sum = 0
    count = 0
    student_problems = initial_dictionary_by_keys(students_closest_friends.keys())
    student_friends = initial_dictionary_by_keys(students_closest_friends.keys())
    for key, value in student_answerd_problems.items():
        current_max = 0
        max_problem = 0
        friend_list_max = []
        temp1 = students_first_attempt[key]
        for i in range(len(value)):
            friend_list = []
            count = 0
            current_question = value[i]
            for t in temp1:
                if list(t.keys())[0] == current_question:
                    first_attempt = t[current_question]
            list_closest = students_closest_friends[key]
            for j in range(len(list_closest)):
                list_friend_question = student_answerd_problems[list_closest[j]]
                if current_question in list_friend_question:
                    count += 1
                    friend_list.append(list_closest[j])
            if count > current_max and first_attempt != 0:
                max_problem = current_question
                current_max = count
                friend_list_max = friend_list
        if max_problem != 0:
            student_problems[key].append(max_problem)
            student_problems[key].append(current_max)
            student_friends[key] = friend_list_max
    for key, value in student_problems.items():
        if value == 0:
            sum += 1
    return student_problems , student_friends

student_problems , student_friends = find_most_answered_problem(students_closest_friends, student_answerd_problems, students_first_attempt)

def remove_students_with_lass_than_5_friends(student_problems , student_friends):
    student_problems_new = {}
    student_friends_new = {}
    for key, val in student_problems.items():
        if len(val) == 0 or val[1] == 1 or val[1] == 2 or val[1] == 3 or val[1] == 4:
            continue
        else:
            student_problems_new[key] = val
            student_friends_new[key] = student_friends[key]
    return student_problems_new , student_friends_new


student_problems , student_friends = remove_students_with_lass_than_5_friends(student_problems , student_friends)


def create_new_column(data_df):
    data_df['Problem_rank'] = data_df['Correct_First_Attempt'] + 1 / (data_df['Step_Duration_sec'])


create_new_column(data_df)


def calculate_avg_rank_for_most_answerd_problem(student_problems, student_friends, data_df):
    student_rank_problem = initial_dictionary_by_keys(student_problems.keys)
    for (idx, row) in data_df.iterrows():
        curr_student_id = row.Anon_Student_Id
        curr_problem = row.Problem_Name
        curr_problem_rank = row.Problem_rank
        #l = [curr_problem, curr_problem_rank]
        if curr_student_id in student_problems.keys():
            student_rank_problem[curr_student_id].append([curr_problem, curr_problem_rank])
    result = {i: {'my_rank' : 0,'friends_rank': 0} for i in student_problems.keys()}
    for key, value in student_problems.items():
        if len(value) == 0:
            continue
        student_id = key
        problem_num = value[0]
        friend_list = student_friends[student_id]
        friend_problem_rank = 0
        my_problem_rank = 0
        # find my rank
        temp_list = student_rank_problem[student_id]
        for i in temp_list:
            if i[0] == problem_num:
                my_problem_rank = i[1]
        result[student_id]['my_rank'] = my_problem_rank
        for j in range(len(friend_list)):
            temp_list = student_rank_problem[friend_list[j]]
            for k in temp_list:
                if k[0] == problem_num:
                    friend_problem_rank += k[1]
        result[key]['friends_rank'] = friend_problem_rank / value[1]
    return result


result = calculate_avg_rank_for_most_answerd_problem(student_problems, student_friends, data_df)


def calcuate_estimate_error(result_dic):
    count = 0
    sum = 0
    for key, value in result_dic.items():
        count += 1
        distance = value['friends_rank'] - value['my_rank']
        sum += distance*distance
    rmse = np.sqrt(sum / (count))
    print('RMSE:', rmse)


calcuate_estimate_error(result)


def recommend_result(students_closest_friends, student_answerd_problems, result):
    recommended_problem = initial_dictionary_by_keys(result.keys)
    for key in result.keys():
        my_problem = student_answerd_problems[key]
        my_friends_list = students_closest_friends[key]
        for index in range(0 ,len(my_friends_list)):
            current_friend = my_friends_list[index]
            current_friend_problems = student_answerd_problems[current_friend]
            for problem in current_friend_problems:
                if problem not in recommended_problem[key] and problem not in my_problem and len(recommended_problem[key]) < 10:
                    recommended_problem[key].append(problem)
    return recommended_problem


recommended_question = recommend_result(students_closest_friends, student_answerd_problems, result)


def write_file_result(recommended_question):
    """writing lists to a csv files"""
    filename = 'results.csv'
    with open(filename, 'w') as csv_file:
        writer = csv.writer(csv_file, lineterminator='\n')
        fieldnames2 = ['Student_Id','Q1','Q2','Q3','Q4','Q5','Q6','Q7','Q8','Q9','Q10']
        writer.writerow(fieldnames2)
        for key, value in recommended_question.items():
            writer.writerow([key,value[0],value[1], value[2],value[3], value[4],value[5],value[6], value[7], value[8], value[9]])
write_file_result(recommended_question)

def print_results():
    print('Enter your Id:')
    x = input()
    print('Hello, ' + x)
    if x in recommended_question.keys():
        print("your recommended questions are: \n", recommended_question[x])
        print("Trust yourself, you know more than you think you do :)")
    else:
        print("sorry , you are not in the list, please try another Id")

print_results()

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
histogram(student_answerd_problems)
