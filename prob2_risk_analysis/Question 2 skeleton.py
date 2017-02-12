# Python Project Template
'''
Template follows "Machine Learning Mastery with Python" by Jason Brownlee.

'''


################################################################################
# 1. Prepare Problem

# a) Load libraries
import sys
#import os
import pickle
from time import time

## evaluation
from sklearn.metrics import precision_score, recall_score 
import matplotlib.pyplot as plt
import pandas as pd
#from ggplot import *
import numpy as np

#from sklearn.datasets import load_iris
from sklearn.preprocessing import MinMaxScaler
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.grid_search import GridSearchCV

from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest, SelectPercentile

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC

from sklearn.cross_validation import StratifiedShuffleSplit
from sklearn.cross_validation import train_test_split


# b) Load dataset
data = pd.read_csv(r"C:\Users\Andri\Google Drive\Dev\M\Career\DKDC_Kiva\Data\20161102 Full borrower info.csv")
df_X = data.ix[:,:-1]
df_Y = data.ix[:,-1:]


################################################################################
# 2. Summarize Data

# a) Descriptive statistics
#df_Y.describe() 
#df[target1].head(20)


# b) Data visualizations


################################################################################
# 3. Prepare Data

# a) Data Cleaning
# TODO
#drop columns
#df_X = df_X.drop('disbursed_time', 1) # bc `ValueError: invalid literal for float(): 12/4/79`
#df_X = df_X.drop('borrower_birth_date', 1) # bc `ValueError: invalid literal for float(): 12/4/79`
#df_X = df_X.drop('loan_status', 1) # take out `loan_status` bc other y variable
#df_X = df_X.drop('payment_frequency', 1) # bc `ValueError: could not convert string to float: monthly`
#df_X = df_X.drop('amount_settled', 1)  # exclude because may be other y variable

#label encode
from sklearn import preprocessing
le = preprocessing.LabelEncoder() # to convert strings to cats
for i in df_X.columns:
    if df_X[i].dtype == object:
        df_X[i] = le.fit_transform(df_X[i])

for i in df_Y.columns:
    if df_Y[i].dtype == object:
        df_Y[i] = le.fit_transform(df_Y[i])

#fill NaNs (bc `ValueError: Input contains NaN, infinity or a value too large for dtype('float64').`)
df_X = df_X.fillna(0)


# b) Feature Selection
from sklearn.feature_selection import SelectKBest, SelectPercentile
#selection = SelectKBest(k=10)
selection = SelectPercentile(percentile=10)
X_features = selection.fit(df_X, df_Y).transform(df_X)
feature_names = [df_X.columns[i] for i in selection.get_support(indices=True)]
feature_scores = [selection.scores_[i] for i in selection.get_support(indices=True)]
print feature_names
print feature_scores
print


# c) Data Transforms


################################################################################
# 4. Evaluate Algorithms

# a) Split-out validation dataset

# simple `train_test_split`
from sklearn.cross_validation import train_test_split
X_train, X_test, y_train, y_test = train_test_split(df_X,
                                                    df_Y,
                                                    test_size = 0.1,
                                                    random_state=5)

#print X_train, X_test, y_train, y_test

##`K Fold`
#from sklearn.model_selection import KFold
#kf = KFold(n_splits=3)
#kf.get_n_splits(X)
#
#for train_index, test_index in kf.split(X):
#    print "KFold value:", 
#    print("TRAIN:", train_index, "TEST:", test_index)
#    X_train, X_test = X[train_index], X[test_index]
#    y_train, y_test = y[train_index], y[test_index]


# b) Test options and evaluation metric


# c) Spot-Check Algorithms

'''
following "Forecasting Peer-to-Peer Lending Risk" Destine et al:
– Logistical Regression 1
– Random Forest 1
– Naive Bayes (Bernoulli, Gaussian, Multinomial) 1
– K-Nearest Neighbors 1
– Gradient Boosting 0
– Voting Classifier 0
'''

# Logistical Regression
from sklearn.linear_model import LogisticRegression
lr = LogisticRegression()
print("LogisticRegression score: ", lr.fit(X_train, y_train).score(X_test, y_test))
print

# Random Forest
from sklearn.ensemble import RandomForestClassifier
rfc = RandomForestClassifier()
print("RandomForestClassifier score: ", rfc.fit(X_train, y_train).score(X_test, y_test))
print

# Naive Bayes (Gaussian)
from sklearn.naive_bayes import GaussianNB
gnb = GaussianNB()
print("GaussianNB score: ", gnb.fit(X_train, y_train).score(X_test, y_test))
print 

# K-Nearest Neighbors
from sklearn.neighbors import KNeighborsClassifier
knn = KNeighborsClassifier()
print("KNeighborsClassifier score: ", knn.fit(X_train, y_train).score(X_test, y_test))
print

# Decision Tree
from sklearn.tree import DecisionTreeClassifier
dtc = DecisionTreeClassifier()
print("DecisionTreeClassifier score: ", dtc.fit(X_train, y_train).score(X_test, y_test))
print

# d) Compare Algorithms

models = []
# append in |("name", clf_pipeline, param_grid)| format for each `models` 
# entry. combine inside the loop, and then do CV, GridSearchCV, .fit, 
# results.append(clf.score_)
### define scalars,arrays to use in GridSearch
feature_min = 1
feature_max = 2 #10 better # TODO
max_svc_max_iter = int(1e3) # may crash due to non-scaling. return to 1e3.
svm_C = [0.001, 1, 100]
svm_kernel = ["linear", "poly", "rbf", "sigmoid"]
svm_gamma = [0.01, 0.9, 10]            
dt_min_samples_split = [2,5,10]
knn_n_neighbors = [2,5,10]
Boolean_fullGridSearch = True
if Boolean_fullGridSearch:
    # LR variants
    models.append(('lr',
                   Pipeline([("scale", MinMaxScaler(feature_range=(0, 1))),
                             ("features", FeatureUnion([("univ_select", SelectKBest()),
                                                        ("pca", PCA())])),
                             ("lr", LogisticRegression())]),
                   dict(features__pca__n_components = range(feature_min,feature_max),
                        features__univ_select__k = range(feature_min,feature_max))
                   )
                  )
    # RF variants
    models.append(('rf',
                   Pipeline([("scale", MinMaxScaler(feature_range=(0, 1))),
                             ("features", FeatureUnion([("univ_select", SelectKBest()),
                                                        ("pca", PCA())])),
                             ("rf", RandomForestClassifier())]),
                   dict(features__pca__n_components = range(feature_min,feature_max),
                        features__univ_select__k = range(feature_min,feature_max))
                   )
                  )               
    # GNB variants
    models.append(('gnb',
                   Pipeline([("gnb", GaussianNB())]),
                   dict()
                   )
                  )
    # KNN variants
    models.append(('knn',
                   Pipeline([("knn", KNeighborsClassifier())]),
                   dict()
                   )
                  )
    # DT variants
    models.append(('dt',
                   Pipeline([("dt", DecisionTreeClassifier())]),
                   dict()
                   )
                  )
    # SVM variants
    models.append(('svm',
                   Pipeline([("svm", SVC())]),
                   dict()
                   )
                  )           
else:
    print "pick best model from Grid Search..."

# prepare results reports                   
best_estimators = []
best_scores = []
names = []
cv = StratifiedShuffleSplit(y = df_Y, 
                            n_iter = 10, #default is 10; change to 30 for increased fidelity 
                            test_size = 0.1, 
                            random_state = 2017)

# cycle through all grid searches
for name, pipeline, param_grid in models:
    print "Start:", name
    grid_search = GridSearchCV(estimator = pipeline, 
                               param_grid = param_grid, 
                               verbose = 2,
                               cv = cv,
                               scoring = None, #default "scoring=None". try 'f1', 'recall' to combine both R and P.
                               n_jobs = 1) # parallelize to lower runtime
    grid_search.fit(df_X, df_Y)
    best_estimators.append(grid_search.best_estimator_)
    best_scores.append([grid_search.best_score_])
    names.append(name)
    print "End:", name
    print "grid_search.best_score_:", grid_search.best_score_

# boxplot algorithm comparison
fig = plt.figure()
fig.suptitle('Algorithm Comparison')
ax = fig.add_subplot(111)
plt.boxplot(best_scores)
ax.set_xticklabels(names)
ax.tick_params(axis='both', which='major', labelsize=8)
plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
plt.show()

################################################################################
# 5. Improve Accuracy

# a) Algorithm Tuning

# b) Ensembles


################################################################################
# 6. Finalize Model

# a) Predictions on validation dataset

# b) Create standalone model on entire training dataset

# c) Save model for later use


