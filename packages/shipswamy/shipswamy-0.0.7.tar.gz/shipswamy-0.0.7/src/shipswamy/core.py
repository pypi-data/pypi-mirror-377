def print_ml_programs(indx):
    ml2_progs=[
r"""
#Program1a:
import csv  
a=[]  
with open('enjoysport.csv', 'r') as csvfile:  
    for row in csv.reader(csvfile): 
        a.append(row)  
print("\n The total number of training instances are: " ,len(a)-1)  
num_attribute =len(a[0])-1  
print("\n The initial hypothesis is: ")  
hypothesis =['0']*num_attribute  
print(hypothesis)  
for i in range(1,len(a)):  
    if a[i][num_attribute] == 'yes':  
        for j in range(0, num_attribute):  
            if hypothesis[j] =='0' or hypothesis[j] == a[i][j]:  
                hypothesis[j] =a[i][j]  
            else:  
                hypothesis[j] = '?'  
print("\n The hypothesis for the training instance {} is :\n".format(i),hypothesis)  
print("\n The Maximally specific hypothesis for the training instance is ") 
print(hypothesis)


#Program1b: 

import numpy as np  
import pandas as pd  
data = pd.DataFrame(data=pd.read_csv('enjoysport.csv'))  
concepts = np.array(data.iloc[:,0:-1])  
print(concepts)  
target = np.array(data.iloc[:,-1])  
print(target)  
def learn(concepts, target):  
    specific_h = concepts[0].copy()  
    print("initialization of specific_h and general_h")  
    print(specific_h)  
    general_h = [["?" for i in range(len(specific_h))] for i in range(len(specific_h))]  
    print(general_h)  
    for i, h in enumerate(concepts):  
        if target[i] == "yes":  
            for x in range(len(specific_h)):  
                if h[x]!= specific_h[x]:  
                    specific_h[x]='?'  
                    general_h[x][x]='?' 
        if target[i] == "no":  
            for x in range(len(specific_h)):  
                if h[x]!= specific_h[x]:  
                    general_h[x][x]= specific_h[x]  
                else:  
                    general_h[x][x]='?'  
        print(" steps of Candidate Elimination Algorithm",i+1)  
        print(specific_h)  
        print(general_h)  
    indices =[i for i, val in enumerate(general_h) if val ==['?', '?', '?', '?', '?', '?']]  
    for i in indices:  
        general_h.remove (['?','?','?','?','?','?'])  
    return specific_h, general_h  
s_final, g_final = learn(concepts, target)  
print("Final Specific_h:", s_final, sep="\n")  
print("Final General_h:", g_final, sep="\n")""",
r"""
#Program 2:
import pandas as pd
import math

data = {
    "S.No": [1, 2, 3, 4, 5],
    "CGPA": [">=9", "<8", ">=9", "<8", ">=8"],
    "Interactiveness": ["Yes", "Yes", "Yes", "No", "Yes"],
    "Practical Knowledge": ["Good", "Good", "Average", "Good", "Good"],
    "Job Offer": ["Yes", "Yes", "No", "No", "No"]
}
df = pd.DataFrame(data)

def foil_gain(pos, neg, new_pos, new_neg):
    if new_pos == 0:
        return 0
    gain = new_pos * (math.log2(new_pos / (new_pos + new_neg)) - math.log2(pos / (pos + neg)))
    return gain

total_pos = len(df[df["Job Offer"] == "Yes"])
total_neg = len(df[df["Job Offer"] == "No"])

attributes = ["CGPA", "Interactiveness", "Practical Knowledge"]
values = {
    "CGPA": df["CGPA"].unique(),
    "Interactiveness": df["Interactiveness"].unique(),
    "Practical Knowledge": df["Practical Knowledge"].unique()
}
gains = []
for attr in attributes:
    for val in values[attr]:
        subset = df[df[attr] == val]
        new_pos = len(subset[subset["Job Offer"] == "Yes"])
        new_neg = len(subset[subset["Job Offer"] == "No"])
        gain = foil_gain(total_pos, total_neg, new_pos, new_neg)
        gains.append((f'{attr}={val}', gain, new_pos, new_neg))

gains.sort(key=lambda x: x[1], reverse=True)

print("FOIL Gain and Rule Candidates:\n")
for rule, gain, pos, neg in gains:
    print(f"Rule: IF {rule} THEN Job Offer = Yes | FOIL Gain = {gain:.4f} | Positives = {pos} | Negatives = {neg}")""",
r"""
#program3:
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import BaggingClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.metrics import accuracy_score, classification_report

data = load_breast_cancer()
X = data.data
y = data.target

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

from sklearn.ensemble import BaggingClassifier
from sklearn.tree import DecisionTreeClassifier
bag_model = BaggingClassifier(
    estimator=DecisionTreeClassifier(),
    n_estimators=50,
    random_state=42
)
bag_model.fit(X_train, y_train)
y_pred_bag = bag_model.predict(X_test)

print("Bagging Accuracy:", accuracy_score(y_test, y_pred_bag))
print("\n Classification Report:\n", classification_report(y_test, y_pred_bag))
print("\n Bagging Accuracy:", accuracy_score(y_test, y_pred_bag))
print("\nClassification Report:\n", classification_report(y_test, y_pred_bag))

from sklearn.ensemble import AdaBoostClassifier
boost_model = AdaBoostClassifier(
    estimator=DecisionTreeClassifier(max_depth=1),
    n_estimators=50,
    random_state=42
)
boost_model.fit(X_train, y_train)
y_pred_boost = boost_model.predict(X_test)

print(" Boosting Accuracy:", accuracy_score(y_test, y_pred_boost))
print("\n Classification Report:\n", classification_report(y_test, y_pred_boost))""",
r"""
#Program4:
from sklearn.datasets import load_breast_cancer
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

data = load_breast_cancer()
X = data.data

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

k = 2
kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
clusters = kmeans.fit_predict(X_scaled)

from sklearn.decomposition import PCA
pca = PCA(n_components=2)
principal_components = pca.fit_transform(X_scaled)

plt.figure(figsize=(10, 7))
for cluster_id in sorted(set(clusters)):
    plt.scatter(principal_components[clusters == cluster_id, 0],
                principal_components[clusters == cluster_id, 1],
                label=f'Cluster {cluster_id}', alpha=0.7)
plt.title(f'K-Means Clusters (K={k}) - PCA Reduced Data')
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.legend()
plt.grid(True)
plt.show()"""
    ]
    print(ml2_progs[indx-1])