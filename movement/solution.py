import sys
import time
import threading
import os
import signal
import math

sys.setrecursionlimit(100000)

OFFICE_GOOD = 0
OFFICE_TOO_MANY = 1
OFFICE_TOO_LESS = -1

CONFLICT_NONE = 0
CONFLICT_MUCH = 1
CONFLICT_LESS = -1

FIND_OFFICE_CAN_MOVE_INTO = 0
FIND_OFFICE_CAN_MOVE_OUT = 1

FROM_OTHERS_TO_MY = 0
FROM_MY_TO_OTHERS = 1

best_path = []
result_printed = 0

class Office:
    def __init__(self):
        self.id = None
        self.min = 0         # min limitation
        self.max = 0       # max limitation
        self.people = 0       # num of people in this office
        self.ok = 0             # 0: good; 1: too many people; -1: too less people
        self.my_move_in_list = {}
        self.my_move_out_list = {}
        self.others_move_in_list = {}          # {from_office_id: count}
        self.others_move_out_list = {}         # {to_office_id: count}
        self.except_list = []           # will not move in office in list
        self.backward_last_search = None
        self.forward_last_search = None
        self.conflict_mark = CONFLICT_NONE      # CONFLICT_None, CONFLICT_MUCH, CONFLICT_LESS
        self.capacity_to_max = 0        # max - people
        self.capacity_to_min = 0        # people - min

    def update(self):
        self.capacity_to_max = self.max - self.people
        self.capacity_to_min = self.people - self.min
        people = self.get_candidate_people_count()
        if (people >= self.min and
            people <= self.max):
            self.ok = OFFICE_GOOD
        elif people < self.min:
            self.ok = OFFICE_TOO_LESS
        else:
            self.ok = OFFICE_TOO_MANY

    def people_change(self, num_of_people_change):
        self.people += num_of_people_change
        # self.update()

    def get_candidate_people_count(self):
        people_count = self.people
        if self.others_move_in_list != {}:
            for count in self.others_move_in_list.values():
                people_count += count
        if self.my_move_in_list != {}:
            for count in self.my_move_in_list.values():
                people_count += count
        if self.others_move_out_list != {}:
            for count in self.others_move_out_list.values():
                people_count -= count
        if self.my_move_out_list != {}:
            for count in self.my_move_out_list.values():
                people_count -= count
        return people_count

def get_input():
    office_number = int(input())
    office_limitation = []
    for i in range(office_number):
        office_limitation.append(input())
    return office_number, office_limitation

def init_all_office(office_list, office_number, office_limitation_list):
    for index in range(office_number):
        office_limit = office_limitation_list[index].rstrip(" ").split(" ")
        office_list[index].id = index
        office_list[index].min = int(office_limit[0])
        office_list[index].max = int(office_limit[1])
        office_list[index].people = int(office_limit[2])
        office_list[index].capacity_to_max = office_list[index].max - office_list[index].people
        office_list[index].capacity_to_min = office_list[index].people - office_list[index].min
        if (office_list[index].people >= office_list[index].min and
            office_list[index].people <= office_list[index].max):
            office_list[index].ok = OFFICE_GOOD
        elif office_list[index].people < office_list[index].min:
            office_list[index].ok = OFFICE_TOO_LESS
        else:
            office_list[index].ok = OFFICE_TOO_MANY

def find_nearest_available_office(office_list, office_index, mode, exception = []):
    office_list_temp = list(office_list)
    office_list_temp.extend(office_list_temp)
    search_length = len(office_list)

    if mode == FIND_OFFICE_CAN_MOVE_INTO:
        if office_list[office_index].ok != OFFICE_TOO_MANY:
            return None
        # forward search
        if office_list[office_index].forward_last_search == None:
            forward_nearest_office_index = office_index + 1
        else:
            forward_nearest_office_index = office_list[office_index].forward_last_search + 1
        has_found = False
        while(not has_found):
            if abs(forward_nearest_office_index - office_index) > math.ceil(search_length/2) + 1:
                forward_nearest_office_index = "out of boundary"
                break
            if (office_list_temp[forward_nearest_office_index].get_candidate_people_count() < office_list_temp[forward_nearest_office_index].max):
                if office_list_temp[forward_nearest_office_index].id not in exception:
                    has_found = True
                else:
                    forward_nearest_office_index += 1
            else:
                forward_nearest_office_index += 1

        # backward search
        if office_list[office_index].backward_last_search == None:
            backward_nearest_office_index = office_index - 1
        else:
            backward_nearest_office_index = office_list[office_index].backward_last_search - 1
        has_found = False
        while(not has_found):
            if abs(backward_nearest_office_index - office_index) > math.ceil(search_length/2) + 1:
                backward_nearest_office_index = "out of boundary"
                break
            if (office_list_temp[backward_nearest_office_index].get_candidate_people_count() < office_list_temp[backward_nearest_office_index].max):
                if office_list[backward_nearest_office_index].id not in exception:
                    has_found = True
                else:
                    backward_nearest_office_index -= 1
            else:
                backward_nearest_office_index -= 1

    elif mode == FIND_OFFICE_CAN_MOVE_OUT:
        if office_list[office_index].ok != OFFICE_TOO_LESS:
            return None
        # forward search
        if office_list[office_index].forward_last_search == None:
            forward_nearest_office_index = office_index + 1
        else:
            forward_nearest_office_index = office_list[office_index].forward_last_search + 1
        has_found = False
        while(not has_found):
            if abs(forward_nearest_office_index - office_index) > math.ceil(search_length/2) + 1:
                forward_nearest_office_index = "out of boundary"
                break
            if (office_list_temp[forward_nearest_office_index].get_candidate_people_count() > office_list_temp[forward_nearest_office_index].min):
                if office_list_temp[forward_nearest_office_index].id not in exception:
                    has_found = True
                else:
                    forward_nearest_office_index += 1
            else:
                forward_nearest_office_index += 1
        # backward search
        if office_list[office_index].backward_last_search == None:
            backward_nearest_office_index = office_index - 1
        else:
            backward_nearest_office_index = office_list[office_index].backward_last_search - 1
        has_found = False
        while(not has_found):
            if abs(backward_nearest_office_index - office_index) > math.ceil(search_length/2) + 1:
                backward_nearest_office_index = "out of boundary"
                break
            if (office_list_temp[backward_nearest_office_index].get_candidate_people_count() > office_list_temp[backward_nearest_office_index].min):
                if office_list[backward_nearest_office_index].id not in exception:
                    has_found = True
                else:
                    backward_nearest_office_index -= 1
            else:
                backward_nearest_office_index -= 1

    # compare and find the nearest
    if forward_nearest_office_index == "out of boundary" and backward_nearest_office_index == "out of boundary":
        return None
    elif forward_nearest_office_index == "out of boundary":
        office_list[office_index].backward_last_search = backward_nearest_office_index + 1
        return office_list_temp[backward_nearest_office_index].id
    elif backward_nearest_office_index == "out of boundary":
        office_list[office_index].forward_last_search = forward_nearest_office_index - 1
        return office_list_temp[forward_nearest_office_index].id
    else:
        if office_index - backward_nearest_office_index >= forward_nearest_office_index - office_index:
            office_list[office_index].forward_last_search = forward_nearest_office_index - 1
            return office_list_temp[forward_nearest_office_index].id
        else:
            office_list[office_index].backward_last_search = backward_nearest_office_index + 1
            return office_list_temp[backward_nearest_office_index].id

def move(from_office_index, to_office_index, office_list, move_ment_array, mode, direction = None):
    office_list_temp = list(office_list)
    office_list_temp.extend(office_list_temp)
    if direction == None:
        # calculate distance
        if mode == FROM_OTHERS_TO_MY:
            people_count = office_list[from_office_index].others_move_out_list[to_office_index]
        elif mode == FROM_MY_TO_OTHERS:
            people_count = office_list[from_office_index].my_move_out_list[to_office_index]
        distance = cal_distance(to_office_index, from_office_index, len(office_list))
        if distance > 0:
            step = 1
            movement_direction = "right"
            be_moved_in_direction = "left"
        else:
            step = -1
            movement_direction = "left"
            be_moved_in_direction = "right"
        current_office_index = from_office_index
        next_office_index = from_office_index + step
        while(office_list_temp[current_office_index].id != to_office_index):
            for i in range(people_count):
                move_ment_array[office_list_temp[current_office_index].id][movement_direction] -= 1
                move_ment_array[office_list_temp[next_office_index].id][be_moved_in_direction] += 1
            current_office_index += step
            next_office_index += step
        # office_list[from_office_index].people_change(-people_count)
        # office_list[to_office_index].people_change(people_count)
        # if mode == FROM_OTHERS_TO_MY:
        #     del office_list[to_office_index].my_move_in_list[from_office_index]
        # elif mode == FROM_MY_TO_OTHERS:
        #     del office_list[to_office_index].others_move_in_list[from_office_index]

# move_ment_array[{"left":left_count,"right":right_count},...]. >0 means input, <0 means output.
def init_movement_array(office_list_length):
    movement_array = []
    for i in range(office_list_length):
        array_template = dict({"left":0, "right":0})
        movement_array.append(array_template)
    return movement_array

def optimize_path(office_list, movement_array_list):
    office_list_temp = list(office_list)
    office_list_temp.extend(office_list_temp)
    index = 0
    while index < len(office_list):
        path_length = 0
        min_people_count_in_path = float("inf")
        right_index_temp = index
        path_member = []
        while (movement_array_list[office_list_temp[right_index_temp].id]["right"]) > 0:
            if path_length > len(office_list_temp):
                break
            if movement_array_list[office_list_temp[right_index_temp].id]["right"] < min_people_count_in_path:
                min_people_count_in_path = movement_array_list[office_list_temp[right_index_temp].id]["right"]
            path_length += 1
            right_index_temp += 1
            most_right_member_id = office_list_temp[right_index_temp].id

        left_index_temp = index
        while (movement_array_list[office_list_temp[left_index_temp].id]["left"]) < 0:
            if path_length > len(office_list_temp):
                break
            if abs(movement_array_list[office_list_temp[left_index_temp].id]["left"]) < min_people_count_in_path:
                min_people_count_in_path = abs(movement_array_list[office_list_temp[left_index_temp].id]["left"])
            path_length += 1
            left_index_temp -= 1
            most_left_member_id = office_list_temp[left_index_temp].id
        if (path_length) > len(office_list)//2:
            index = most_left_member_id
            while(office_list_temp[index].id != most_right_member_id):
                movement_array_list[office_list_temp[index].id]["right"] -= min_people_count_in_path
                movement_array_list[office_list_temp[index].id + 1]["left"] += min_people_count_in_path
                index += 1
            movement_array_list[office_list_temp[index].id]["right"] -= min_people_count_in_path
            movement_array_list[office_list_temp[index].id + 1]["left"] += min_people_count_in_path

            index = most_right_member_id
            while(office_list_temp[index].id != most_left_member_id):
                movement_array_list[office_list_temp[index].id]["right"] -= min_people_count_in_path
                movement_array_list[office_list_temp[index].id + 1]["left"] += min_people_count_in_path
                index -= 1
            movement_array_list[office_list_temp[index].id]["right"] += min_people_count_in_path
            movement_array_list[office_list_temp[index].id + 1]["left"] -= min_people_count_in_path
        else:
            index += 1

    index = 0
    while index < len(office_list):
        path_length = 0
        min_people_count_in_path = float("inf")
        left_index_temp = index
        path_member = []
        while (movement_array_list[office_list_temp[left_index_temp].id]["left"]) > 0:
            if path_length > len(office_list_temp):
                break
            if movement_array_list[office_list_temp[left_index_temp].id]["left"] < min_people_count_in_path:
                min_people_count_in_path = movement_array_list[office_list_temp[left_index_temp].id]["left"]
            path_length += 1
            left_index_temp += 1
            most_left_member_id = office_list_temp[left_index_temp].id

        right_index_temp = index
        while (movement_array_list[office_list_temp[right_index_temp].id]["right"]) < 0:
            if path_length > len(office_list_temp):
                break
            if abs(movement_array_list[office_list_temp[right_index_temp].id]["right"]) < min_people_count_in_path:
                min_people_count_in_path = abs(movement_array_list[office_list_temp[right_index_temp].id]["right"])
            path_length += 1
            right_index_temp -= 1
            most_right_member_id = office_list_temp[right_index_temp].id
        if (path_length) > len(office_list)//2:
            index = most_right_member_id
            while(office_list_temp[index].id != most_left_member_id):
                movement_array_list[office_list_temp[index].id]["left"] -= min_people_count_in_path
                movement_array_list[office_list_temp[index].id + 1]["right"] += min_people_count_in_path
                index += 1
            movement_array_list[office_list_temp[index].id]["left"] -= min_people_count_in_path
            movement_array_list[office_list_temp[index].id + 1]["right"] += min_people_count_in_path

            index = most_left_member_id
            while(office_list_temp[index].id != most_right_member_id):
                movement_array_list[office_list_temp[index].id]["left"] -= min_people_count_in_path
                movement_array_list[office_list_temp[index].id + 1]["right"] += min_people_count_in_path
                index -= 1
            movement_array_list[office_list_temp[index].id]["left"] += min_people_count_in_path
            movement_array_list[office_list_temp[index].id + 1]["right"] -= min_people_count_in_path
        else:
            index += 1



def movement_apply(office_list):
    # print("movement_apply")
    # move to office_list[index]
    total_move_count = 0
    total_output = ""
    movement_array_list = init_movement_array(len(office_list))
    for index, office in enumerate(office_list):
        for denstiny, people_count in office.others_move_out_list.items():
            move(index, denstiny, office_list, movement_array_list, FROM_OTHERS_TO_MY)
        # office_list[index].others_move_out_list = {}

        for denstiny, people_count in office.my_move_out_list.items():
            move(index, denstiny, office_list, movement_array_list, FROM_MY_TO_OTHERS)
        # office_list[index].my_move_out_list = {}
    optimize_path(office_list, movement_array_list)
    total_move_count = 0
    waiting_list = []
    for index, movement_array in enumerate(movement_array_list):
        total_move_count += abs(movement_array["right"])
        waiting_list.append(index)

    move_count = 0
    move_index = 0

    while (move_count < total_move_count):
        for move_index in waiting_list:
            movement_array = movement_array_list[move_index]
            while (abs(movement_array["right"]) != 0):
                if move_index < (len(office_list) - 1):
                    if movement_array["right"] > 0:
                        move_out_office_index = move_index + 2
                        move_in_office_index = move_index + 1
                        people_change = -1
                    else:
                        move_out_office_index = move_index + 1
                        move_in_office_index = move_index + 2
                        people_change = 1
                else:
                    if movement_array["right"] > 0:
                        move_out_office_index = 1
                        move_in_office_index = move_index + 1
                        people_change = -1
                    else:
                        move_out_office_index = move_index + 1
                        move_in_office_index = 1
                        people_change = 1
                if office_list[move_out_office_index - 1].people > 0:
                    total_output += "{} {}\n".format(move_out_office_index, move_in_office_index)
                    office_list[move_out_office_index - 1].people_change(-1)
                    office_list[move_in_office_index - 1].people_change(1)
                    movement_array["right"] += people_change
                    move_count += 1
                else:
                    break
            if movement_array["right"] == 0:
                remove_index = move_index
                break
        if remove_index != None:
            waiting_list.remove(remove_index)
            remove_index = None

    # check_movement_done(office_list)
    sys.stdout.write("{}\n".format(total_move_count))
    sys.stdout.write(total_output)
    sys.stdout.flush()

def find_conflict(office_list):
    conflict_office_list = []
    for index, office in enumerate(office_list):
        office_list[index].forward_last_search = None
        office_list[index].backward_last_search = None
        office_list[index].conflict_mark = CONFLICT_NONE
        candidate_count = office_list[index].get_candidate_people_count()
        if candidate_count > office_list[index].max:
            office_list[index].conflict_mark = CONFLICT_MUCH
            conflict_office_list.append(index)
        elif candidate_count < office_list[index].min:
            office_list[index].conflict_mark = CONFLICT_LESS
            conflict_office_list.append(index)
    return conflict_office_list

# judge index1 is in index2 left or right. dlt < 0:left, dlt > 0:right
# 0,1,2,3,...max, 0, 1, 2 from left to right
def cal_distance(index1, index2, office_list_length):
    dlt = index1 - index2
    if dlt > office_list_length/2:
        dlt = dlt - office_list_length
    elif dlt < -office_list_length/2:
        dlt = dlt + office_list_length
    return dlt


def get_pk_role(office, office_list_length, mode):
    # 0,1,2,3,...max, 0, 1, 2 from left to right
    most_far_office_id_in_left = None
    max_left_path = 0
    most_far_office_id_in_right = None
    max_right_path = 0
    if mode == FIND_OFFICE_CAN_MOVE_INTO:
        for move_in_office in office.others_move_in_list.keys():
            if office.others_move_in_list[move_in_office] != 0:
                distance = cal_distance(move_in_office, office.id, office_list_length)
                if distance < 0:
                    if max_left_path > distance:
                        most_far_office_id_in_left = move_in_office
                        max_left_path = distance
                else:
                    if max_right_path < distance:
                        most_far_office_id_in_right = move_in_office
                        max_left_path = distance
    elif mode == FIND_OFFICE_CAN_MOVE_OUT:
        for move_out_office in office.others_move_out_list.keys():
            if office.others_move_out_list[move_out_office] != 0:
                distance = cal_distance(move_out_office, office.id, office_list_length)
                if distance < 0:
                    if max_left_path > distance:
                        most_far_office_id_in_left = move_out_office
                        max_left_path = distance
                else:
                    if max_right_path < distance:
                        most_far_office_id_in_right = move_out_office
                        max_left_path = distance
    return most_far_office_id_in_left, most_far_office_id_in_right

# return winner, loser, loser's destination
def pk(office_list, office_1, office_2, conflict_index, mode):
    if mode == FIND_OFFICE_CAN_MOVE_INTO:
        office_1_second_choice = find_nearest_available_office(office_list, office_1, FIND_OFFICE_CAN_MOVE_INTO, office_list[office_1].except_list)
        office_2_second_choice = find_nearest_available_office(office_list, office_2, FIND_OFFICE_CAN_MOVE_INTO, office_list[office_2].except_list)
        distance_office_1_move_to_conflict_index = abs(cal_distance(office_2, office_2_second_choice, len(office_list))) + abs(cal_distance(office_1, conflict_index, len(office_list)))
        distance_office_2_move_to_conflict_index = abs(cal_distance(office_1, office_1_second_choice, len(office_list))) + abs(cal_distance(office_2, conflict_index, len(office_list)))

        if distance_office_1_move_to_conflict_index > distance_office_2_move_to_conflict_index:
            return office_2, office_1, office_1_second_choice
        elif distance_office_1_move_to_conflict_index < distance_office_2_move_to_conflict_index:
            return office_1, office_2, office_2_second_choice
        else:
            if office_list[office_2_second_choice].conflict_mark == CONFLICT_MUCH:
                return office_2, office_1, office_1_second_choice
            else:
                return office_1, office_2, office_2_second_choice
    elif mode == FIND_OFFICE_CAN_MOVE_OUT:
        office_1_second_choice = find_nearest_available_office(office_list, office_1, FIND_OFFICE_CAN_MOVE_OUT, office_list[office_1].except_list)
        office_2_second_choice = find_nearest_available_office(office_list, office_2, FIND_OFFICE_CAN_MOVE_OUT, office_list[office_2].except_list)
        distance_office_1_move_to_conflict_index = abs(cal_distance(office_2, office_2_second_choice, len(office_list))) + abs(cal_distance(office_1, conflict_index, len(office_list)))
        distance_office_2_move_to_conflict_index = abs(cal_distance(office_1, office_1_second_choice, len(office_list))) + abs(cal_distance(office_2, conflict_index, len(office_list)))

        if distance_office_1_move_to_conflict_index > distance_office_2_move_to_conflict_index:
            return office_2, office_1, office_1_second_choice
        elif distance_office_1_move_to_conflict_index < distance_office_2_move_to_conflict_index:
            return office_1, office_2, office_2_second_choice
        else:
            if office_list[office_2_second_choice].conflict_mark == CONFLICT_LESS:
                return office_2, office_1, office_1_second_choice
            else:
                return office_1, office_2, office_2_second_choice

# one of guy from office_source would move to office_a, but now need change to office_b
def move_change(office_source, office_a, office_b, mode):
    if mode == FIND_OFFICE_CAN_MOVE_INTO:
        # office_source: decrease office_a in my_move_out_list
        if office_a.id in office_source.my_move_out_list.keys():
            if office_source.my_move_out_list[office_a.id] >= 1:
                office_source.my_move_out_list[office_a.id] -= 1
            else:
                return False
            if office_source.my_move_out_list[office_a.id] == 0:
                del office_source.my_move_out_list[office_a.id]
        else:
            return False
        # office_source: add office_b in my_move_out_list
        if office_b.id in office_source.my_move_out_list.keys():
            office_source.my_move_out_list[office_b.id] += 1
        else:
            office_source.my_move_out_list.update({office_b.id: 1})
        # office_a: decrease office_source in others_move_in_list
        if office_source.id in office_a.others_move_in_list.keys():
            if office_a.others_move_in_list[office_source.id] >= 1:
                office_a.others_move_in_list[office_source.id] -= 1
            else:
                return False
            if office_a.others_move_in_list[office_source.id] == 0:
                del office_a.others_move_in_list[office_source.id]
        else:
            return False
        # office_b: add office_source in others_move_in_list
        if office_source.id in office_b.others_move_in_list.keys():
            office_b.others_move_in_list[office_source.id] += 1
        else:
            office_b.others_move_in_list.update({office_source.id: 1})
    elif mode == FIND_OFFICE_CAN_MOVE_OUT:
        # office_source: decrease office_a in my_move_in_list
        if office_a.id in office_source.my_move_in_list.keys():
            if office_source.my_move_in_list[office_a.id] >= 1:
                office_source.my_move_in_list[office_a.id] -= 1
            else:
                return False
            if office_source.my_move_in_list[office_a.id] == 0:
                del office_source.my_move_in_list[office_a.id]
        else:
            return False
        # office_source: add office_b in my_move_in_list
        if office_b.id in office_source.my_move_in_list.keys():
            office_source.my_move_in_list[office_b.id] += 1
        else:
            office_source.my_move_in_list.update({office_b.id: 1})
        # office_a: decrease office_source in others_move_out_list
        if office_source.id in office_a.others_move_out_list.keys():
            if office_a.others_move_out_list[office_source.id] >= 1:
                office_a.others_move_out_list[office_source.id] -= 1
            else:
                return False
            if office_a.others_move_out_list[office_source.id] == 0:
                del office_a.others_move_out_list[office_source.id]
        else:
            return False
        # office_b: add office_source in others_move_out_list
        if office_source.id in office_b.others_move_out_list.keys():
            office_b.others_move_out_list[office_source.id] += 1
        else:
            office_b.others_move_out_list.update({office_source.id: 1})

def conflict_solve(office_list, conflict_list):
    move_list = []
    for conflict_index in conflict_list:
        # cal people need to move to other office
        condidate_count = office_list[conflict_index].get_candidate_people_count()
        # too much people want to move in this office
        if condidate_count > office_list[conflict_index].max:
            conflict_people_count = condidate_count - office_list[conflict_index].max
            # manage conflict people one by one
            for _ in range(conflict_people_count):
                office_1, office_2 = get_pk_role(office_list[conflict_index], len(office_list), FIND_OFFICE_CAN_MOVE_INTO)
                if office_1 != None and office_2 != None:
                    if conflict_index not in office_list[office_1].except_list:
                        office_list[office_1].except_list.append(conflict_index)
                    if conflict_index not in office_list[office_2].except_list:
                        office_list[office_2].except_list.append(conflict_index)
                    win, loser, loser_destination = pk(office_list, office_1, office_2, conflict_index, FIND_OFFICE_CAN_MOVE_INTO)
                    move_list.append([office_list[loser], office_list[conflict_index], office_list[loser_destination], FIND_OFFICE_CAN_MOVE_INTO])
                    # move_change(office_list[loser], office_list[conflict_index], office_list[loser_destination], FIND_OFFICE_CAN_MOVE_INTO)
                elif not office_1 == None:
                    if conflict_index not in office_list[office_1].except_list:
                        office_list[office_1].except_list.append(conflict_index)
                    office_1_second_choice = find_nearest_available_office(office_list, office_1, FIND_OFFICE_CAN_MOVE_INTO, office_list[office_1].except_list)
                    move_list.append([office_list[office_1], office_list[conflict_index], office_list[office_1_second_choice], FIND_OFFICE_CAN_MOVE_INTO])
                    # move_change(office_list[office_1], office_list[conflict_index], office_list[office_1_second_choice], FIND_OFFICE_CAN_MOVE_INTO)
                elif not office_2 == None:
                    if conflict_index not in office_list[office_2].except_list:
                        office_list[office_2].except_list.append(conflict_index)
                    office_2_second_choice = find_nearest_available_office(office_list, office_2, FIND_OFFICE_CAN_MOVE_INTO, office_list[office_2].except_list)
                    move_list.append([office_list[office_2], office_list[conflict_index], office_list[office_2_second_choice], FIND_OFFICE_CAN_MOVE_INTO])
                    # move_change(office_list[office_2], office_list[conflict_index], office_list[office_2_second_choice], FIND_OFFICE_CAN_MOVE_INTO)
                # elif (office_list[conflict_index].my_move_out_list == {} and
                #       office_list[conflict_index].others_move_out_list == {}):
                else:
                    office_new_choice = find_nearest_available_office(office_list, conflict_index, FIND_OFFICE_CAN_MOVE_INTO, office_list[conflict_index].except_list)
                    # num_of_move_people = -office_list[conflict_index].capacity_to_max
                    num_of_move_people = office_list[conflict_index].get_candidate_people_count() - office_list[conflict_index].max
                    if office_new_choice != None:
                        move_out_temp = {office_new_choice: num_of_move_people}
                        office_list[conflict_index].my_move_out_list.update(move_out_temp)
                        move_in_temp = {conflict_index: num_of_move_people}
                        office_list[office_new_choice].others_move_in_list.update(move_in_temp)
        # move too much people out of office
        elif condidate_count < office_list[conflict_index].min:
            conflict_people_count = office_list[conflict_index].min - condidate_count
            for _ in range(conflict_people_count):
                office_1, office_2 = get_pk_role(office_list[conflict_index], len(office_list), FIND_OFFICE_CAN_MOVE_OUT)
                if office_1 != None and office_2 != None:
                    if conflict_index not in office_list[office_1].except_list:
                        office_list[office_1].except_list.append(conflict_index)
                    if conflict_index not in office_list[office_2].except_list:
                        office_list[office_2].except_list.append(conflict_index)
                    win, loser, loser_destination = pk(office_list, office_1, office_2, conflict_index, FIND_OFFICE_CAN_MOVE_OUT)
                    move_list.append([office_list[loser], office_list[conflict_index], office_list[loser_destination], FIND_OFFICE_CAN_MOVE_OUT])
                    # move_change(office_list[loser], office_list[conflict_index], office_list[loser_destination], FIND_OFFICE_CAN_MOVE_OUT)
                elif not office_1 == None:
                    if conflict_index not in office_list[office_1].except_list:
                        office_list[office_1].except_list.append(conflict_index)
                    office_1_second_choice = find_nearest_available_office(office_list, office_1, FIND_OFFICE_CAN_MOVE_OUT, office_list[office_1].except_list)
                    move_list.append([office_list[office_1], office_list[conflict_index], office_list[office_1_second_choice], FIND_OFFICE_CAN_MOVE_OUT])
                    # move_change(office_list[office_1], office_list[conflict_index], office_list[office_1_second_choice], FIND_OFFICE_CAN_MOVE_OUT)
                elif not office_2 == None:
                    if conflict_index not in office_list[office_2].except_list:
                        office_list[office_2].except_list.append(conflict_index)
                    office_2_second_choice = find_nearest_available_office(office_list, office_2, FIND_OFFICE_CAN_MOVE_OUT, office_list[office_2].except_list)
                    move_list.append([office_list[office_2], office_list[conflict_index], office_list[office_2_second_choice], FIND_OFFICE_CAN_MOVE_OUT])
                    # move_change(office_list[office_2], office_list[conflict_index], office_list[office_2_second_choice], FIND_OFFICE_CAN_MOVE_OUT)
                # elif (office_list[conflict_index].my_move_in_list == {} and
                #       office_list[conflict_index].others_move_in_list == {}):
                else:
                    office_new_choice = find_nearest_available_office(office_list, conflict_index, FIND_OFFICE_CAN_MOVE_OUT, office_list[conflict_index].except_list)
                    # num_of_move_people = -office_list[conflict_index].capacity_to_min
                    num_of_move_people = office_list[conflict_index].min - office_list[conflict_index].get_candidate_people_count()
                    if office_new_choice != None:
                        move_in_temp = {office_new_choice: num_of_move_people}
                        office_list[conflict_index].my_move_in_list.update(move_in_temp)
                        move_out_temp = {conflict_index: num_of_move_people}
                        office_list[office_new_choice].others_move_out_list.update(move_out_temp)
    for movement in move_list:
        move_change(movement[0], movement[1], movement[2], movement[3])

def balance_my_list_and_others(office_list):
    for index in range(len(office_list)):
        candidate_people_count = office_list[index].get_candidate_people_count()
        if ((office_list[index].ok == OFFICE_TOO_MANY) and (candidate_people_count < office_list[index].min)):
            delete_key_list = []
            for key, value in office_list[index].my_move_out_list.items():
                if key in office_list[index].others_move_in_list.keys():
                    if (candidate_people_count + value) < office_list[index].max:
                        delete_key_list.append(key)
                        candidate_people_count += value
                        office_list[key].others_move_in_list[index] -= value
                        office_list[index].my_move_out_list[key] -= value
                    else:
                        decrease = (candidate_people_count + value) - office_list[index].max
                        office_list[key].others_move_in_list[index] = decrease
                        office_list[index].my_move_out_list[key] = decrease
                        break
                    # todo: sort the path and del furthest fist
            for key in delete_key_list:
                if office_list[key].others_move_in_list[index] == 0:
                    del office_list[key].others_move_in_list[index]
                if office_list[index].my_move_out_list[key] == 0:
                    del office_list[index].my_move_out_list[key]

        elif ((office_list[index].ok == OFFICE_TOO_LESS) and (office_list[index].get_candidate_people_count() > office_list[index].max)):
            delete_key_list = []
            for key, value in office_list[index].my_move_in_list.items():
                if key in office_list[index].others_move_out_list.keys():
                    if (candidate_people_count - value) > office_list[index].min:
                        delete_key_list.append(key)
                        candidate_people_count -= value
                        office_list[key].others_move_out_list[index] -= value
                        office_list[index].my_move_in_list[key] -= value
                    else:
                        addition = office_list[index].min - (candidate_people_count - value)
                        office_list[key].others_move_out_list[index] = addition
                        office_list[index].my_move_in_list[key] = addition
                        break
            for key in delete_key_list:
                if office_list[key].others_move_out_list[index] == 0:
                    del office_list[key].others_move_out_list[index]
                if office_list[index].my_move_in_list[key] == 0:
                    del office_list[index].my_move_in_list[key]
                    # todo: sort the path and del furthest fist


def get_move_solution(office_list, office_number):
    # movement data: [A,B,C]. Move C people from A to B
    # move people out from office who has too many people
    ## find the nearest movement, store in a list, if the end of movement is same, create a class conflict
    for index in range(office_number):
        nearest_office = find_nearest_available_office(office_list, index, FIND_OFFICE_CAN_MOVE_INTO)
        num_of_move_people = -office_list[index].capacity_to_max
        if nearest_office != None:
            move_out_temp = {nearest_office: num_of_move_people}
            office_list[index].my_move_out_list.update(move_out_temp)
            move_in_temp = {index: num_of_move_people}
            office_list[nearest_office].others_move_in_list.update(move_in_temp)

        nearest_office = find_nearest_available_office(office_list, index, FIND_OFFICE_CAN_MOVE_OUT)
        num_of_move_people = -office_list[index].capacity_to_min
        if nearest_office != None:
            move_in_temp = {nearest_office: num_of_move_people}
            office_list[index].my_move_in_list.update(move_in_temp)
            move_out_temp = {index: num_of_move_people}
            office_list[nearest_office].others_move_out_list.update(move_out_temp)
    balance_my_list_and_others(office_list)
    conflict_list = find_conflict(office_list)
    while(conflict_list != []):
        conflict_solve(office_list, conflict_list)
        balance_my_list_and_others(office_list)
        conflict_list = find_conflict(office_list)

def check_movement_done(office_list):
    ok = True
    for index in range(len(office_list)):
        if (office_list[index].people >= office_list[index].min and
            office_list[index].people <= office_list[index].max):
            office_list[index].ok = OFFICE_GOOD
        elif office_list[index].people < office_list[index].min:
            office_list[index].ok = OFFICE_TOO_LESS
        else:
            office_list[index].ok = OFFICE_TOO_MANY
        if office_list[index].ok != OFFICE_GOOD:
            print("office_index:{}, status:{}".format(index, office_list[index].ok))
            ok = False
        if office_list[index].others_move_in_list != {}:
            print("office_index:{}, others_move_in_list:{}".format(index, office_list[index].others_move_in_list))
            ok = False
        if office_list[index].others_move_out_list != {}:
            print("office_index:{}, others_move_out_list:{}".format(index, office_list[index].others_move_out_list))
            ok = False
        if office_list[index].my_move_in_list != {}:
            print("office_index:{}, my_move_in_list:{}".format(index, office_list[index].my_move_in_list))
            ok = False
        if office_list[index].my_move_out_list != {}:
            print("office_index:{}, my_move_out_list:{}".format(index, office_list[index].my_move_out_list))
            ok = False
    return ok

def create_index_list(max_export, max_import):
    index_list = [0]
    index_export = range(-1, -max_export - 1, -1)
    index_import = range(1, max_import + 1, 1)
    for i in range(min(max_import,max_export)):
        index_list.append(index_export[i])
        index_list.append(index_import[i])
    if max_import > max_export:
        for j in index_import[i+1:max_import + 1]:
            index_list.append(j)
    else:
        for j in index_export[i+1:max_export + 1]:
            index_list.append(j)
    return index_list

if __name__ == '__main__':
    start_time = time.process_time()
    office_number, office_limitation_list = get_input()

    office_list = []
    for i in range(office_number):
        office_list.append(Office())

    init_all_office(office_list, office_number, office_limitation_list)

    get_move_solution(office_list, office_number)
    movement_apply(office_list)
