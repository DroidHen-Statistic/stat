import numpy as np
import matplotlib.pyplot as plt
import os
import sys
from ready_for_train import Vector_Reader as v_reader
head_path = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))
# print(head_path)
sys.path.append(head_path)
import config
from utils import *

from collections import defaultdict


import copy


def _gen_defaultdict():
    # return copy.copy(defaultdict(int))
    return defaultdict(int)

# 读机器id


class Machine_Vector_Reader(v_reader):
    # Machine_Id_2_Lv = {1:1, 4:2, 5:4, 6:5, 7:6, 11:7, 8:10, 10:13, 9:16,
    # 2:19, 3:22, 12:25, 13:28, 17:31, 14:34, 16:37, 15:40, 18:43, 19:46,
    # 20:49, 21:52, 22:55, 23:58, 24:61, 25:64, 26:67, 27:70, 28:73, 29:76,
    # 30:79, 31:82, 32:85, 33:88,34:91}
    # 已经排好序
    # max_group = 999
    Machine_Id_2_Lv = [(1, 1), (4, 2), (5, 4), (6, 5), (7, 6), (11, 7), (8, 10), (10, 13), (9, 16), (2, 19), (3, 22), (12, 25), (13, 28), (17, 31), (14, 34), (16, 37), (15, 40), (
        18, 43), (19, 46), (20, 49), (21, 52), (22, 55), (23, 58), (24, 61), (25, 64), (26, 67), (27, 70), (28, 73), (29, 76), (30, 79), (31, 82), (32, 85), (33, 88), (34, 91)]

    Lv_Group_Machine_Count = defaultdict(int)  # 等级段开放的机器个数
    Lv_Group_Machine_Percent = defaultdict(float)   # 等级段开放的机器比例，开放两个就是50%

    @staticmethod
    def lv_group_list():
        return [v[1] for v in Machine_Vector_Reader.Machine_Id_2_Lv]

    @staticmethod
    def lv_group_pos(lv_group):
        pos = 0
        for m_id, cr_lv in Machine_Vector_Reader.Machine_Id_2_Lv:
            if cr_lv == lv_group:
                return pos
            pos += 1
        return pos

    @staticmethod
    def lv_2_machine_id(lv):
        # lv_2_id = other_util.flip_dict(Machine_Vector_Reader.Machine_Id_2_Lv)
        m_ids = []
        for m_id, cr_lv in Machine_Vector_Reader.Machine_Id_2_Lv:
            # for m_id, cr_lv in
            # sorted(Machine_Vector_Reader.Machine_Id_2_Lv.items(), key = lambda x
            # : x[1] ):
            if lv >= cr_lv:
                m_ids.append(m_id)
            else:
                break
        return m_ids

    # 传入等级，返回等级分组
    @staticmethod
    def lv_2_group(lv):
        pre_lv = 0
        for m_id, cr_lv in Machine_Vector_Reader.Machine_Id_2_Lv:
            if lv < cr_lv:
                return pre_lv
            elif lv == cr_lv:
                return pre_lv
            else:
                pre_lv = cr_lv
        # return Machine_Vector_Reader.max_group
        return pre_lv

    def __init__(self, input_dir='null', out_put_dir='null'):
        v_reader.__init__(self, input_dir, out_put_dir)

    @staticmethod
    def calc_lv_group_m_count():
        for m_id, cr_lv in Machine_Vector_Reader.Machine_Id_2_Lv:
            m_count = len(Machine_Vector_Reader.lv_2_machine_id(cr_lv))
            Machine_Vector_Reader.Lv_Group_Machine_Count[cr_lv] = m_count
            Machine_Vector_Reader.Lv_Group_Machine_Percent[
                cr_lv] = round(1. / m_count, 4)
        # Machine_Vector_Reader.Lv_Group_Machine_Count[]

    """
    读玩家数据，继承类可以重写这个函数
    """

    def _read_user_data(self, file_dir, seq_len, max_len):
        """
        max_len : 原始文件的最大序列长度
        """
        # pay_count = 0
        # no_pay_count = 0
        mid_lv_count = [defaultdict(_gen_defaultdict),
                        defaultdict(_gen_defaultdict)]
        for payed in range(2)[::-1]:
            pre_fix = ""
            if payed == 1:
                pre_fix = 'pay_'
            file_machine = os.path.join(file_dir, pre_fix + "machine_id.txt")
            if (not os.path.exists(file_machine)):
                continue
            f_machine = open(file_machine, 'r')

            file_lv = os.path.join(file_dir, pre_fix + "level.txt")
            f_lv = open(file_lv, 'r')

            while True:
                line = f_machine.readline().strip()
                if not line:
                    break
                lv_line = f_lv.readline().strip()

                line = line.split(" ")
                lv_line = lv_line.split(" ")
                # if len(line) < seq_len or line[-1] == "-1":  # 被抛掉的数据
                if line[-1] == '-1':
                    break
                cr_len = len(line)
                # for in line[::-1]
                for i in range(seq_len):
                    # cr_index = max(0, cr_len - seq_len + i)
                    cr_index = cr_len - seq_len + i
                    if cr_index >= cr_len or cr_index < 0:
                        continue
                    # print(line[cr_index])
                    try:
                        cr_mid = int(float(line[cr_index]))
                        cr_lv = int(float(lv_line[cr_index]))
                        cr_lv_group = self.lv_2_group(cr_lv)
                        mid_lv_count[payed][cr_mid][cr_lv_group] += 1
                    except:
                        break
            #         # [cr_mid] += 1
            # f_machine.close()
            # f_bonus.close()
            # f_coin.close()
            # f_time.close()
        # return [data, lable]
        return mid_lv_count


if __name__ == '__main__':
    # d = {3:33, 4:44}
    # k = other_util.flip_dict(d)
    # print(k)
    mv_reader = Machine_Vector_Reader()
    mv_reader.calc_lv_group_m_count()
    seq_len = 50
    max_len = 50
    mid_lv_count = [defaultdict(_gen_defaultdict),
                    defaultdict(_gen_defaultdict)]
    uid_2_vectors = []
    # 从文件里读
    import pickle
    vector_file = "vector.data"
    if not os.path.exists(vector_file):
        uid_2_vectors = mv_reader.gen_uid_vector(seq_len, max_len)
        with open(vector_file, 'wb') as f:
            pickle.dump(uid_2_vectors, f)
    else:
        with open(vector_file, 'rb') as f:
            uid_2_vectors = pickle.load(f)

    lv_total = defaultdict(_gen_defaultdict)
    for cr_uid, vector in uid_2_vectors.items():
        print(cr_uid)
        for payed, cr_mid_lv_count in enumerate(vector):
            for cr_mid, lv_count in cr_mid_lv_count.items():
                for cr_lv, count in lv_count.items():
                    mid_lv_count[payed][cr_mid][cr_lv] += count
                    lv_total[payed][cr_lv] += count
        # break
    # X = Machine_Vector_Reader.lv_group_list()
    # X = range(len(Machine_Vector_Reader.Machine_Id_2_Lv) ) # 要大于所有的 #错了
    figure_path = file_util.get_figure_path("slot", "machine_used")
    # if not os.path.exists(figure_path):
    #     os.mkdir(figure_path)

    X_label = [x for x in Machine_Vector_Reader.Lv_Group_Machine_Percent.keys()]
    import copy
    y_expect = [
        x for x in Machine_Vector_Reader.Lv_Group_Machine_Percent.values()]
    fig_count = 0
    for payed, cr_mid_lv_count in enumerate(mid_lv_count):
        # title_raw = r"machine:%d" + (" (pay)" if payed else "")
        postfix = "(pay)" if payed else ""
        for cr_mid, lv_count in cr_mid_lv_count.items():
            if len(lv_count) <= 0:
                continue
            title = "machine_%d%s" % (cr_mid, postfix)
            # title += str(cr_mid)
            cr_X_label = copy.copy(X_label)
            y = [0] * len(y_expect)
            total = [0] * len(y_expect)
            for cr_lv, count in lv_count.items():
                pos = Machine_Vector_Reader.lv_group_pos(cr_lv)
                cr_lv_total = lv_total[payed][cr_lv]
                y[pos] = round(count / cr_lv_total, 4)
                # cr_X_label[pos] = str(cr_X_label[pos]) + "(%s)" % cr_lv_total
                cr_X_label[pos] = cr_X_label[pos]
                total[pos] = cr_lv_total

            gcf = plt.figure(fig_count, figsize=(10, 4))
            ax = plt.gca()
            axisx = ax.xaxis
            ax.set_title(title)
            ax.set_xlabel("Lv group")
            # xlim=(0, X_label[-1])
            # ax.set_xlim(xlim)
            ax.xaxis.set_major_locator(plt.MultipleLocator(1))
            ax.set_ylabel("use percent")
            ax.plot(y_expect, '--.', label="except")
            ax.plot(y, '-', label="real")

            ax.set_xticklabels([-1, 0] + cr_X_label)

            for label in axisx.get_ticklabels():
                # label.set_color("red")
                label.set_rotation(45)
                label.set_fontsize(8)
            # ax.set_xticklabels.set_ticklabels(['a','b','c','d','e'])
            # s1 = plt.subplot(111)
            # s1.xaxis.set_ticklabels(Machine_Vector_Reader.lv_group_list())

            # s1.set_ylabel('odds_mean')
            # s1.plt(X,y_expect, '--.', lable="use count")
            # s1.plt(X, y, '-o', lable="use count")

            # 加上标注
            for pos in range(len(y)):
                # plt.text(pos, y , total[pos] ,color='b',fontsize=2)
                if total[pos] > 0:
                    # plt.text(pos, y[pos], "total: %s" % total[pos])
                    plt.text(pos, y[pos], total[pos])

            plt.text(15, 1, s='Numbers above curve are total counts',
                     color='blue', va="top", ha="center")
            # plt.annotate('total counts above curve',xy=(0,0),xytext=(0.2,0.2),arrowprops=dict(facecolor='blue', shrink=0.1))

            ax.legend(loc="upper right")
            # plt.show()
            file_name = os.path.join(figure_path, title + ".png")
            # gcf.savefig(file_name, dpi= 160)
            gcf.savefig(file_name)
            plt.close(fig_count)
            # plt.close('all')
            fig_count += 1
            # gcf.close()
            # exit()
        # break
        # plt.figure()

    k = Machine_Vector_Reader.lv_2_machine_id(37)
    # print(k)

    # exit()
