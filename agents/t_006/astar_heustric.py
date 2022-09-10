import json
from copy import deepcopy

list = ()
result_dict = {}


def HValue(player_id, c_key):
    oppo_player_id = 0 if player_id == 1 else 1
    self_player_id = player_id
    self_ring = str(2 * self_player_id + 1)
    oppo_ring = str(2 * oppo_player_id + 1)
    self_counter = str(2 * self_player_id + 2)
    oppo_counter = str(2 * oppo_player_id + 2)
    oppo_player_id = str(oppo_player_id)
    self_player_id = str(player_id)
    #

    def helpfunc1(str1):
        # dont have empty, can have self-counter or not, must have oppo_counter and self-ring
        left, right = 0,0
        for i in range(len(str1)):
            if str1[i] == self_ring:
                break
            elif str1[i] == self_counter:
                left -= 1
            else:
                left += 1
        for i in range(len(str1)-1, -1, -1):
            if str1[i] == self_ring:
                break
            elif str1[i] == self_counter:
                right -= 1
            else:
                right += 1
        if str1.count(self_ring) == 1:
            return str1.count(self_ring) + str1.count(oppo_counter) - max(0, left, right)
        if str1.count(self_ring) > 1:
            return str1.count(self_ring) + str1.count(oppo_counter) - max(0, left, right) - max(0, sorted([0, left, right])[1])

    def helpfunc2(str1):
        # dont have self ring,  must have oppo_counter and self-ring and self count
        minuser = 0
        minu_list = []
        for i in range(len(str1)):
            if str1[i] == '0':
                minu_list.append(minuser)
                minuser = 0
            elif str1[i] == self_counter:
                minuser-=1
            elif str1[i] == oppo_counter:
                minuser+=1
        minu_list.append(minuser)
        if str1.count('000') == 1:
            c_temp = 2
        else:
            c_temp = str1.count('00')
        for elem in minu_list:
            if elem > 0:
                c_temp+=elem
        return 2*str1.count('0') + str1.count(oppo_counter) - c_temp

    def helpfunc3(str1):
        # dont have self_counter,  must have oppo_counter and self-ring and empty
        minuser = 0
        minu_list = []
        for i in range(len(str1)):
            if str1[i] == self_ring:
                minu_list.append(minuser)
                minuser = 0
            else:
                minuser += 1
        minu_list.append(minuser)
        if str1.count(self_ring) == 1:
            temp = deepcopy(minu_list)
            temp.remove(max(minu_list))
            if max(temp)==max(minu_list):
                return str1.count(self_ring) + 2 * str1.count('0') + str1.count(oppo_counter) - max(minu_list) - 1
            return str1.count(self_ring) + 2 * str1.count('0') + str1.count(oppo_counter) - max(minu_list)
        if str1.count(self_ring) == 2:
            return str1.count(self_ring) + 2 * str1.count('0') + str1.count(oppo_counter) - max(minu_list) - sorted(minu_list)[-2] + str1.count(self_ring+oppo_counter+self_ring)
        if str1.count(self_ring) == 3:
            return str1.count(self_ring) + 2 * str1.count('0') + str1.count(oppo_counter) - max(minu_list) - sorted(minu_list)[-2] + str1.count(self_ring+oppo_counter+self_ring)

    def helpfunc4(str1):
        # all must have except oppo ring
        if str1.count(self_ring) == 1:
            left, right = [], []
            left_minuser, right_minuser = 0 , 0
            left_minu_list = []
            right_minu_list = []
            for i in range(len(str1)):
                if str1[i] == self_ring:
                    break
                elif str1[i] == self_counter:
                    left_minuser -= 1
                elif str1[i] == oppo_counter:
                    left_minuser += 1
                elif str1[i] == '0':
                    left_minu_list.append(left_minuser)
                    left_minuser = 1
            left_minu_list.append(left_minuser)
            for i in range(1, len(left_minu_list)):
                for j in range(i):
                    left_minu_list.append(sum(left_minu_list[j:j+i]))
            left_max = max(left_minu_list)
            for i in range(len(str1) - 1, -1, -1):
                if str1[i] == self_ring:
                    break
                elif str1[i] == self_counter:
                    right_minuser -= 1
                elif str1[i] == oppo_counter:
                    right_minuser += 1
                elif str1[i] == '0':
                    right_minu_list.append(right_minuser)
                    right_minuser = 1
            right_minu_list.append(right_minuser)
            for i in range(1, len(right_minu_list)):
                for j in range(i):
                    right_minu_list.append(sum(right_minu_list[j:j+i]))
            right_max = max(right_minu_list)
            return 1 + 2 * str1.count('0') + str1.count(oppo_counter) - max(0,left_max, right_max)
        else:
            minuser = 0
            minu_list = []
            for i in range(len(str1)):
                if str1[i] == self_ring:
                    minu_list.append(minuser)
                    minuser = 0
                elif str1[i] == '0':
                    minu_list.append(minuser)
                    minuser = 1
                elif str1[i] == self_counter:
                    minuser -= 1
                else:
                    minuser += 1
            minu_list.append(minuser)
            return str1.count(self_ring) + 2 * str1.count('0') + str1.count(oppo_counter) - max(minu_list) - \
                   sorted(minu_list)[-2] + str1.count(self_ring + oppo_counter + self_ring)
                   # + str1.count(self_ring + self_counter + self_ring) + str1.count(self_ring + oppo_counter + self_ring) + \
                   # str1.count(self_ring + oppo_counter + self_counter + self_ring) + str1.count(self_ring + self_counter + oppo_counter + self_ring)

    # cantain oppo rings
    if not c_key.count(str(oppo_ring)) == 0:
        return 46 + c_key.count("0")

    # don't contain oppo rings
    # don't contain oppo rings and oppo counter
    elif c_key.count(oppo_counter) == 0:
        # don't contain oppo rings and oppo counter and self ring -- only have self counter and 0
        if c_key.count(self_ring) == 0:
            # the number of ring need
            temp = c_key.split(self_counter)
            while '' in temp:
                temp.remove('')
                ring_need_num = len(temp)
            else:
                ring_need_num = len(temp)
            # the number of ring to move
            ring_move_num = c_key.count('0')
            return ring_move_num + ring_need_num
        # don't contain oppo rings and oppo counter but have self ring -- only have self counter and 0 and self ring
        else:
            no_self_counter_list = c_key.split(self_counter)
            if '' in no_self_counter_list:
                no_self_counter_list.remove('')
            ans_list = []
            for string in no_self_counter_list:
                isRing = False
                tempstr = ''
                for s in string:
                    if isRing and s == self_ring:
                        ans_list.append(tempstr)
                        tempstr = s
                        isRing = False
                    elif s == self_ring and tempstr == '':
                        tempstr += s
                        isRing = True
                    elif s == self_ring and tempstr[0] == '0':
                        tempstr += s
                        ans_list.append(tempstr)
                        tempstr = ''
                        isRing = False
                    else:
                        tempstr += s
                if not tempstr == '':
                    ans_list.append(tempstr)
            ans = 0
            for elem in ans_list:
                if elem.count(self_ring)>0:
                    ans += len(elem)
                else:
                    ans += len(elem)+1
            return ans
    # contain oppo counter and self rings and self counter and empty
    else:
        #don't have self rings and self counter
        if c_key.count(self_ring) == 0 and c_key.count(self_counter) == 0:
            return c_key.count('0')+1
        # don't have self ring and empty
        elif c_key.count('0') == 0 and c_key.count(self_ring) == 0:
            return min(c_key.count(self_counter)+1, c_key.count(oppo_counter))
        # dont have empty
        elif c_key.count('0') == 0:
            return helpfunc1(c_key)
        elif c_key.count(self_ring) == 0:
            return helpfunc2(c_key)
        elif c_key.count(self_counter) == 0:
            return helpfunc3(c_key)
        # all must have
        else:
            return helpfunc4(c_key)


if __name__ == "__main__":

    # print(HValue(1, '40020'))

    
    for c1 in range(5):
        for c2 in range(5):
            for c3 in range(5):
                for c4 in range(5):
                    for c5 in range(5):
                        c_list = (c1, c2, c3, c4, c5)
                        c_key = "".join(map(str, c_list))
                        result_dict["0"+c_key] = HValue(0, c_key)
                        result_dict["1"+c_key] = HValue(1, c_key)

    test_case = {
        '042141': 4,
        '004004': 4,
        '004014': 4,
        '040040': 4,
        '040141': 4,
        '041214': 2,
        '042144': 2,
        '002120': 5,
        '000024': 5,
        '100243': 4,
        '100244': 4,
        '024042': 4,
        '042242': 2,
        '022444': 3,
        '014014': 3,
        '001411': 5,
        '011404': 3,
        '001412': 4,
        '011412': 4,
        '012412': 3,
        '041122': 2,
        '004421': 3,
        '012401': 4,
        '100034': 4,
        '100223': 3,
        '000040': 5,
        '000044': 4,
        '042120': 4,
        '011111': 5,
        '010101': 5,
        '022414': 2,
        '100020': 5,
        '000022': 4,
        '100022': 4,
        '100302': 5,
        '000140': 5,
        '000120': 5,
        '000422': 4,
        '100422': 4,
        '001241': 4,
        '001414': 5,
        '134023': 3,
        '134204': 3,
        '134402': 3,
        '040020': 5,
        '140020': 4

    }
    for k, v in test_case.items():
        if HValue(int(k[0]), k[1:]) != v:
            print(f'key is {k}, true value is {v}, but get {HValue(int(k[0]), k[1:])}')


    with open("astar_heustric.json", 'w', encoding='utf-8') as f:
        json.dump(result_dict, f, indent=4, ensure_ascii=False)


















