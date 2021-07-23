﻿# -*- coding: utf-8 -*-
import logging
import re
import pandas as pd
from lifetimes import ModifiedBetaGeoFitter, GammaGammaFitter
from sklearn.metrics import mean_absolute_error

train_data = "train_data.csv"


def snakify(column_name):
    '''
    Function to convert pandas column names into snake case.
    '''
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', column_name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def load_data(data):
    """
    Load dataset as a pandas dataframe from csv.
    """
    data = pd.read_csv(
        data)  # I need to set up ingestion from cloud storage / BQ
    data.columns = [
        snakify(col) if col != "T_CAL" else 'T_cal' for col in data.columns
    ]
    key = 'customer_id'
    data[key] = data[key].astype("object")
    return data


def mbg_fitter(data, penalty=0.1):
    """
    Fit calibration data to derive Modified BG/NBD parameters.
    """
    mbg = ModifiedBetaGeoFitter(penalizer_coef=penalty)
    mbg.fit(data['frequency_cal'], data['recency_cal'], data['T_cal'])
    return mbg


def ggf_fitter(data, penalty=0):
    """
    Fit calibration data to derive Gamma Gamma mixing parameters.
    """
    ggf = GammaGammaFitter(penalizer_coef=penalty)
    ggf.fit(data['frequency_cal'], data['monetary_value'])
    return ggf


def save_training_error(repeat, ggf):
    """
    Save error in repeat-customer average profit estimation.
    """
    return mean_absolute_error(
        repeat['monetary_holdout'].mean(),
        ggf.conditional_expected_average_profit(repeat['frequency_cal'],
                                                repeat['monetary_value']).mean,
    )


def save_pickle(mbg, ggf):
    """
    Save Modified BG/NBD & GG parameters to pickle files.
    """
    mbg.save_model('mbg.pkl', save_date=False, save_generate_data_method=False)
    ggf.save_model('ggf.pkl', save_date=False, save_generate_data_method=False)


def run_training(train_data):
    data = load_data(data=train_data)
    mbg = mbg_fitter(data=data)
    repeat = data[data['frequency_cal'] > 0]
    repeat.loc[repeat['monetary_value'] <= 0, ['monetary_value']] = 0.0001
    # checking the independence assumption
    p_corr = repeat[['frequency_cal', 'monetary_value'
                     ]].corr()['frequency_cal']['monetary_value']
    if abs(p_corr) < 0.1:
        ggf = ggf_fitter(data=repeat)
        print(
            "Expected conditional average profit: %s, Average future profit: %s"
            % (round(
                ggf.conditional_expected_average_profit(
                    repeat['frequency_cal'], repeat['monetary_value']).mean(),
                2), round(repeat['monetary_holdout'].mean(), 2)))
        absolute_val_error = save_training_error(
            repeat=repeat, ggf=ggf)  # how to spit this out to console
        save_pickle(mbg=mbg, ggf=ggf)
        # better yet, save error to file or print to console...
        return absolute_val_error
    else:
        logging.warning(
            "Pearson correlation co-efficient {} appears to be too high (independence assumption violated...)"
            .format(round(p_corr, 5)))