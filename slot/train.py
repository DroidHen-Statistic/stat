import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from collections import defaultdict
from enum import Enum, unique
from utils import *
import matplotlib.pyplot as plt
import shutil

from sklearn import preprocessing
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import Normalizer
from sklearn.model_selection import StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import GradientBoostingClassifier 
from sklearn.naive_bayes import GaussianNB
from sklearn.cluster import KMeans
from sklearn.cluster import DBSCAN

from sklearn.model_selection import train_test_split
from sklearn import tree

from dtw import dtw

import pydotplus
from sklearn.model_selection import cross_val_score
# from sklearn.model_selection import cross_validate
from sklearn.pipeline import Pipeline

from sklearn.svm import SVC
import csv

import config
import pickle
from twh.ready_for_train import *


def train(x, y, seq_len, uid):
    scaler = StandardScaler()
    # x = scaler.fit_transform(x)
    
    # x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1, random_state=42)
    # print(y_test)
    path = file_util.get_figure_path("slot",str(uid))
    pay_count = np.sum(y)
    print("pay_count: %d" %pay_count)
    print(len(x))
    x_train = x_test = x
    y_train = y_test = y

    clfs = {"DT":tree.DecisionTreeClassifier(max_depth = 5, class_weight = "balanced"),
        "RF":RandomForestClassifier(max_depth = 5),"ExtraTrees":ExtraTreesClassifier(),"AdaBoost":AdaBoostClassifier(),"GBDT":GradientBoostingClassifier(),"Bayes":GaussianNB()}
    
    # clfs = {"DT":tree.DecisionTreeClassifier(max_depth = 5)} 
    for name, clf in clfs.items():
        print("------%s-------" % name)
        pipe_lr = Pipeline([('clf', clf)])

        cross_accuracy = np.mean(cross_val_score(clf, x_train,
                                y_train, scoring="accuracy", cv=5))
        cross_recall = np.mean(cross_val_score(clf, x_train,
                                y_train, scoring="recall", cv=5))
        cross_precision = np.mean(cross_val_score(clf, x_train,
                                y_train, scoring="precision", cv=5))
        # roc_auc = np.mean(cross_val_score(clf, x_train,
        #                         y_train, scoring="roc_auc", cv=5))
        f1 = np.mean(cross_val_score(clf, x_train,
                                y_train, scoring="f1", cv=5))
        print("cross_validation accuracy:%f recall: %f, precision %f" %(cross_accuracy, cross_recall, cross_precision))
    
        pipe_lr.fit(x_train, y_train)
        y_predict = pipe_lr.predict(x_test)
        pay_count = np.sum(y_test)
        # print(pipe_lr.named_steps['clf'].theta_)
        # print(pipe_lr.named_steps['clf'].sigma_)
        # print(pay_count)
        positive_true = 0
        negative_true = 0
        for i in range(len(y_test)):
            if y_test[i] == 1 and y_predict[i] == 1:
                positive_true += 1
            if y_test[i] == 0 and y_predict[i] == 0:
                negative_true += 1
        recall = float(positive_true/pay_count)
        precision = positive_true/np.sum(y_predict)
        accuracy = (positive_true + negative_true)/len(y_predict)
        
        print('Test accuracy: %.3f pay_count: %d recall: %d' % (pipe_lr.score(x_test, y_test), pay_count, recall))


    
    # with open(os.path.join(path,"test.dot"), 'w') as f:
    #     f = tree.export_graphviz(clf, out_file=f)
    # dot_data = tree.export_graphviz(clf, out_file=None)
    # graph = pydotplus.graph_from_dot_data(dot_data) 
    # graph.write_pdf(os.path.join(path,"tree.pdf"))

def plot_coins(pay_data, uid):
    pay_count = np.sum(y)
     # 金币相关
    pay_coins = [x[0] for x in pay_data]
    pay_coins = sorted(pay_coins)

    # print(pay_coins)
    return np.percentile(pay_coins, 75)

def plot_time(x, y, seq_len, uid):
    pay_count = np.sum(y)
    time = np.array(x)[:,4]
    print(time)

def plot_odds(x, y, seq_len, uid):
    path = file_util.get_figure_path("slot",str(uid))

    pay_count = np.sum(y)
    print("pay_count: %d" %pay_count)

    # 付费的每一次的赔率(纵向比较)
    plt.figure(1)
    for i in range(seq_len):
        plt.plot([x_[-seq_len + i] for x_ in x[-pay_count:]],'b-o')
        plt.savefig(os.path.join(path, "odds_"+str(i)))
        plt.cla()

    for seq in x[-pay_count:]:
        plt.plot(seq[-seq_len:], '-o')
        plt.gca().set_xlabel('spin')
        plt.gca().set_ylabel('odds')
    plt.savefig(os.path.join(path, "odds_seq_pay"))
    plt.cla()

    # 付费的赔率序列，没5个画一幅图
    count = 0
    i = 0
    for seq in x[-pay_count:]:
        count += 1
        if count > 5:
            count = 1
            i += 1
            plt.savefig(os.path.join(path, "odds_seq_pay_" + str(i)))
            plt.cla()
        plt.plot(seq[-seq_len:], '-o')
        plt.gca().set_xlabel('spin')
        plt.gca().set_ylabel('odds')
    plt.savefig(os.path.join(path, "odds_seq_pay_" + str(i)))
    plt.cla()

    # 未付费的赔率序列
    count = 0
    i = 0
    for seq in x[:-pay_count]:
        count += 1
        if count > 5:
            count = 1
            i += 1
            plt.savefig(os.path.join(path, "odds_seq_no_pay_"+str(i)))
            plt.cla()
        plt.plot(seq[-seq_len:],'-o')
    plt.savefig(os.path.join(path, "odds_seq_no_pay_"+str(i+1)))

    for seq in x[-31:]:
        plt.plot(seq[-seq_len:], '-o')
    plt.savefig(os.path.join(path, "odds_seq"))
    plt.show()

    
    odds_pay_mean = np.mean(np.array(x[-pay_count:])[:,-seq_len:], axis = 0)
    print(odds_pay_mean)
    odds_no_pay_mean = np.mean(np.array(x[:-pay_count])[:,-seq_len:], axis = 0)
    print(odds_no_pay_mean)

    odds_pay_var = np.var(np.array(x[-pay_count:])[:,-seq_len:], axis = 0)
    print(odds_pay_var)
    odds_no_pay_var = np.var(np.array(x[:-pay_count])[:,-seq_len:], axis = 0)
    print(odds_no_pay_var)

    # 赔率序列中每一次均值（纵向均值）
    plt.figure(2)
    plt.plot(odds_pay_mean, '-o',label = 'pay')
    plt.plot(odds_no_pay_mean,'-o',label = 'no_pay')
    plt.gca().set_xlabel('spin')
    plt.gca().set_ylabel('odds_mean')
    plt.legend(loc = "upper right")
    plt.savefig(os.path.join(path, "odds_mean"))
    plt.cla()

    # 赔率序列的纵向方差
    plt.figure(3)
    plt.plot(odds_pay_var, '-o', label = 'pay')
    plt.plot(odds_no_pay_var,'-o', label = 'no_pay')
    plt.legend(loc = "upper right")
    plt.gca().set_xlabel('spin')
    plt.gca().set_ylabel('odds_var')
    plt.savefig(os.path.join(path, "odds_var"))
    plt.cla()

def odds_cluster_DBSCAN(X):
    dbscan = DBSCAN(eps = 0.035, min_samples = 8, metric = cal_dtw)
    y_pred = dbscan.fit_predict(X)
    print(len(dbscan.core_sample_indices_))

    return y_pred

def odds_cluster_Birch(X):
    birch = Birch(n_clusters = None) #threshold branching_factor n_clusters 
    y_pred = birch.fit_predict(X)
    return y_pred

def cal_dtw(x,y):
    x = x.reshape(-1,1)
    y = y.reshape(-1,1)
    dist, cost, acc, path = dtw(x, y, dist=lambda x, y: np.linalg.norm(x - y, ord = 1))

    # plt.figure(1)
    # plt.plot(x, 'bo-')
    # plt.plot(y + 10, 'o-')
    # for i in range(len(path[0])):
    #     x_tmp = [path[0][i], path[1][i]]
    #     tmp = [x[path[0][i]], y[path[1]][i] + 10]
    #     plt.plot(x_tmp, tmp, '.--')
    # print(dist)

    # plt.figure(2)
    # plt.imshow(acc.T, origin='lower', cmap=plt.cm.gray, interpolation='nearest')
    # plt.plot(path[0], path[1], 'w')
    # plt.xlim((-0.5, acc.shape[0]-0.5))
    # plt.ylim((-0.5, acc.shape[1]-0.5))
    # print(path[0], path[1])
    
    # plt.show()
    
    return dist

def corelation(x,y):
    score, p_value = other_util.mul_pearson(x,y)
    return score


if __name__ == '__main__':

    from scipy import stats
    # from scipy.stat import skew
    file_names = ['coin', 'is_free', 'level', 'odds',
                  'time_delta', 'win_bonus', 'win_free']
    seq_len = 40
    max_len = 50

    # mean_time = calc_len_times(seq_len, max_len)
    # exit()
    x = []
    y = []
    uid_2_vectors = gen_uid_vector(seq_len, max_len)
    coins = {}
    # scaler = Normalizer()
    # x = scaler.fit_transform(x)
    for uid, vectors in uid_2_vectors.items():
        print("--------",uid,"--------------")
        data_pay = vectors[1]
        data_not_pay = vectors[0]
        print("data_pay:", len(data_pay))
        print("data_not_pay", len(data_not_pay))

        X = np.array((data_pay + data_not_pay))
        Y = np.array(([1] * len(data_pay) + [0] * len(data_not_pay)))
        # if uid == str(1560678):
        #     x1 = X[3]
        #     x2 = X[4]
        #     cal_dtw(x1,x2)
        # X = scaler.fit_transform(X)
        y_pred = odds_cluster_DBSCAN(X)
        print(y_pred)
        labels = set(y_pred)
        path = file_util.get_figure_path("slot",str(uid),"cluster")
        if os.path.exists(path):
            shutil.rmtree(path)
        for label in labels:
            path = file_util.get_figure_path("slot",str(uid),"cluster",str(label))
            print("label: %s" %label)
            x_tmp = X[y_pred == label, :]
            for i,x in enumerate(x_tmp):
                plt.plot(x)
                plt.savefig(os.path.join(path, str(i)))
                plt.cla()

        # score = corelation(X,Y)
        # x_ = range(len(score))
        # # features = ["coin", "earn", "earn/coin", "mean", "variance", "skewness", "kurtosis", "min", "max"]
        # plt.plot(x_, score, '--o', label = str(uid))

        # x += (data_pay + data_not_pay)
        # y += ([1] * len(data_pay) + [0] * len(data_not_pay))
        
        # train(X, Y, seq_len, uid)

        # data_pay_avg = np.mean(data_pay, axis = 0)[3:]
        # data_not_pay_avg = np.mean(data_not_pay, axis = 0)[3:]
        # x_tick = range(len(data_pay_avg))
        # plt.plot(x_tick,data_pay_avg, label = "pay")
        # plt.plot(x_tick,data_not_pay_avg, label ="not_pay")
        # plt.gca().set_xlabel("features")
        # plt.legend(loc = "upper right")
        # features = ["coin", "earn", "earn/coin", "mean", "variance", "skewness", "kurtosis", "min", "max"]
        # plt.xticks(x_tick, features, rotation = -30)
        # path = file_util.get_figure_path("slot",str(uid))
        # plt.savefig(os.path.join(path, "odds_stat_pay_and_no_pay_limited_by_coin"))
        # plt.cla()
        # 
    # x = np.array(x)
    # y = np.array(y)
    # print(np.sum(y))
    # score = corelation(x,y)
    # x_ = range(len(score))
    # features = ["coin", "earn", "earn/coin", "mean", "variance", "skewness", "kurtosis", "min", "max"]
    # plt.plot(x_, score, '--o', label = "total")
    # plt.xticks(x_, features, rotation = -30)
    # plt.legend(loc = "upper right")
    # print(score)
    # plt.show()
    # print("\n")

# def dirlist(path, allfile):
#     filelist = os.listdir(path)
#     for filename in filelist:
#         filepath = os.path.join(path, filename)
#         if os.path.isdir(filepath):
#             cr_uid = filename
#             dirlist(filepath, allfile)
#         else:
#             allfile.append(filepath)
#     return allfile