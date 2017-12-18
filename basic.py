# -*- coding: utf-8 -*-

import pickle
from pyteomics import mzxml, auxiliary
import pandas as pd
import numpy as np
import re
import jcamp
import spc
from io import StringIO
import itertools
import matplotlib.pyplot as plt
import seaborn as sns


def merge_csv(flist, **kwargs):
    """
        合并csv
    """
    return pd.concat([pd.read_csv(f, **kwargs) for f in flist], axis=1)


def psave(data, file_name):
    # 保存数据
    with open(file_name, 'wb') as f:
        pickle.dump(data, f)


def pload(file_name):
    # 读取数据
    with open(file_name, 'rb') as f:
        return pickle.load(f)


def get_real(rt):
    # 获取保留时间数值min
    return rt.real


def rep(c):
    # repmat保留时间，以匹配mz和intensity
    return np.vstack([c[0], np.tile(c[1], len(c[0])), c[2]]).T


def read_mzxml(file_path):
    """
    读取质谱mzxml文件，将其转换为pandas-dataframe,columns = columns=['intensity','rt','mz']
    :param file_path:
    :return: df
    """
    with mzxml.read(file_path) as reader:
        a = [rep([s['intensity array'], get_real(s['retentionTime']), s['m/z array']]) for s in reader]
    b = np.vstack(a)
    df = pd.DataFrame(b, columns=['intensity', 'rt', 'mz'])
    return df


def regstr(text, regexp):
    """
    正则匹配子字符串
    :param text:
    :param regexp:
    :return:
    """

    m = re.search(regexp, text)
    if m:
        return m.group(0)


def read_dx(dx_file):
    """
    :param dx_file: .dx红外光谱文件
    :return: pd.Series,波数-吸光度
    """
    with open(dx_file) as dx:
        data = jcamp.jcamp_read(dx)
        ir = pd.Series(data['y'], name=data['yunits'], index=data['x'])
        ir.index.name = data['xunits']
    return ir


def read_spc(spc_file):
    """
    调用spc库，读取spc文件
    :param spc_file:
    :return: dataframe
             index：波数
             values: log(1/R)
    """
    f = spc.File(spc_file)
    stringIO = StringIO(f.data_txt())
    df = pd.read_csv(stringIO, '\t', index_col=0, header=None)
    df1 = pd.DataFrame(df.values, index=df.index, columns=[f.__dict__['ylabel']])
    df1.index.name = f.__dict__['xlabel']
    return df1


def make_weights(x):
    """
    从x按列生成weight
    :param x: column vector或者按列排列的matrix
    :return: weights
    """
    x = np.array(x)
    if len(x.shape) < 2:
        x = x.reshape(-1, 1)
    weights = x/x.sum(axis=0)
    return weights


def plot_ConfusionMatrix(cm, unique_labels, normalize=True):
    """
    画混淆矩阵
    :param cm: confusionMatrix
    :param unique_labels: 各类的标签
    :param normalize: 是否normalize
    :return:
    """
    cm_norm = cm
    if normalize:
        cm_norm = cm/cm.sum(axis=1)
    sns.heatmap(cm_norm, annot=cm, xticklabels=unique_labels, yticklabels=unique_labels)
    plt.xlabel('预测值')
    plt.ylabel('真实值')

