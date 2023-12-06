# -*- coding: utf-8 -*-
"""
An Integrated Analysis of Incident Patterns and Safety
Measures in Urban Transportation
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler,RobustScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import LinearSVC
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import RepeatedStratifiedKFold
from scipy.stats import loguniform
from sklearn.model_selection import GridSearchCV
from yellowbrick.features import FeatureImportances
from sklearn import metrics
from yellowbrick.classifier import ClassificationReport

data=pd.read_csv("injury-details-2023-q2.csv")

"""

```
1.Analyzing the Impact of Operator and Route on Incident Occurrence:
Investigate if specific operators or routes have higher incident rates. Identify factors contributing to increased incidents.
```

"""

#Specific Operators
import matplotlib.pyplot as plt
import seaborn as sns

# Group data by Operator and count incidents
operator_incident_counts = data.groupby('Operator')['Incident type'].count().reset_index()

# Visualize incident counts by Operator with numbers on bars
plt.figure(figsize=(12, 6))
barplot = sns.barplot(x='Operator', y='Incident type', data=operator_incident_counts)
plt.title('Incident Counts by Operator')
for p in barplot.patches:
    barplot.annotate(f'{p.get_height()}', (p.get_x() + p.get_width() / 2., p.get_height()),
                     ha='center', va='center', xytext=(0, 10), textcoords='offset points')

plt.show()

# Group data by Route and count incidents
route_incident_counts = data.groupby('Route')['Incident type'].count().reset_index()

# Calculate incident rate by route
route_incident_counts['Incident Rate'] = route_incident_counts['Incident type'] / len(data) * 100

# Select top 10 routes by incident rate
top_routes = route_incident_counts.nlargest(10, 'Incident Rate')

# Visualize top 10 routes by incident rate
plt.figure(figsize=(12, 6))
barplot = sns.barplot(x='Route', y='Incident Rate', data=top_routes)
plt.title('Top 10 Routes by Incident Rate')

# Format the y-axis as percentages without decimals
from matplotlib.ticker import FuncFormatter
barplot.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f'{y:.0%}'))

plt.show()

# Explore specific types of incidents
plt.figure(figsize=(12, 6))
ax = sns.countplot(x='Incident type', data=data)
plt.title('Distribution of Incident Types')
plt.xticks(rotation=45, ha='right')

# Annotate each bar with the count or percentage value
for p in ax.patches:
    height = p.get_height()
    ax.annotate(f'{height}', (p.get_x() + p.get_width() / 2., height),
                ha='center', va='center', xytext=(0, 10), textcoords='offset points')

plt.show()

# Count incidents per operator and incident type
incident_counts = data.groupby(['Operator', 'Incident type']).size().unstack(fill_value=0)

# Reset the index for better plotting
incident_counts = incident_counts.reset_index()

# Create a heatmap
plt.figure(figsize=(12, 8))
sns.heatmap(incident_counts.set_index('Operator'), cmap="viridis", annot=True, fmt='g')
plt.title('Incident Counts per Operator and Incident Type')
plt.xlabel('Incident Type')
plt.ylabel('Operator')

# Show the plot
plt.show()

"""2. Analyze how age and gender impact likelihood and severity of incidents. Identify vulnerable demographics."""

import seaborn as sns
import matplotlib.pyplot as plt

# Create a new column 'Severity' based on the 'Injury outcome'
data['Severity'] = data['Injury outcome'].apply(lambda x: 'Severe' if x == 'Taken to hospital' else 'Non-Severe')

# Count incidents based on age, gender, and severity
incident_counts = data.groupby(['Age', 'Gender', 'Severity']).size().reset_index(name='Count')

# Set Seaborn style
sns.set(style="whitegrid")

# Plotting using Seaborn
plt.figure(figsize=(14, 8))

# Plot for likelihood of incidents
plt.subplot(2, 1, 1)
ax1 = sns.barplot(x='Age', y='Count', hue='Gender', data=incident_counts[incident_counts['Severity'] == 'Non-Severe'])
plt.title('Likelihood of Incidents by Age and Gender (Non-Severe)')
plt.xlabel('Age Group')
plt.ylabel('Count')
plt.legend(title='Gender')

# Annotate each bar with the count number
for p in ax1.patches:
    ax1.annotate(f'{p.get_height():.0f}', (p.get_x() + p.get_width() / 2., p.get_height()),
                 ha='center', va='center', xytext=(0, 10), textcoords='offset points')

# Plot for severity of incidents
plt.subplot(2, 1, 2)
ax2 = sns.barplot(x='Age', y='Count', hue='Gender', data=incident_counts[incident_counts['Severity'] == 'Severe'])
plt.title('Severity of Incidents by Age and Gender (Severe)')
plt.xlabel('Age Group')
plt.ylabel('Count')
plt.legend(title='Gender')

# Annotate each bar with the count number
for p in ax2.patches:
    ax2.annotate(f'{p.get_height():.0f}', (p.get_x() + p.get_width() / 2., p.get_height()),
                 ha='center', va='center', xytext=(0, 10), textcoords='offset points')

plt.tight_layout()
plt.show()

# Print the results in text form
print("Likelihood of Incidents by Age and Gender (Non-Severe):")
print(incident_counts[incident_counts['Severity'] == 'Non-Severe'][['Age', 'Gender', 'Count']])

print("\nSeverity of Incidents by Age and Gender (Severe):")
print(incident_counts[incident_counts['Severity'] == 'Severe'][['Age', 'Gender', 'Count']])

# Create a new column 'Severity' based on the 'Injury outcome'
data['Severity'] = data['Injury outcome'].apply(lambda x: 'Severe' if x == 'Taken to hospital' else 'Non-Severe')

# Count incidents based on age, gender, and severity
incident_counts = data.groupby(['Age', 'Gender', 'Severity']).size().reset_index(name='Count')

# Pivot the data for easy analysis
incident_pivot = incident_counts.pivot_table(index=['Age', 'Gender'], columns='Severity', values='Count', fill_value=0)

# Calculate likelihood and severity ratios
incident_pivot['Likelihood Ratio'] = incident_pivot['Severe'] / incident_pivot['Non-Severe']
incident_pivot['Severity Ratio'] = incident_pivot['Severe'] / incident_pivot.sum(axis=1)

# Set thresholds for identifying vulnerable demographics
likelihood_threshold = 0.1
severity_threshold = 0.1

# Identify vulnerable demographics based on the thresholds
vulnerable_likelihood = incident_pivot.loc[incident_pivot['Likelihood Ratio'] > likelihood_threshold, 'Likelihood Ratio']
vulnerable_severity = incident_pivot.loc[incident_pivot['Severity Ratio'] > severity_threshold, 'Severity Ratio']

# Reset the index for proper alignment
vulnerable_likelihood = vulnerable_likelihood.reset_index()
vulnerable_severity = vulnerable_severity.reset_index()

# Visualize the vulnerable demographics
plt.figure(figsize=(14, 6))

# Plotting Likelihood Ratio for Vulnerable Demographics
plt.subplot(1, 2, 1)
sns.barplot(x='Age', y='Likelihood Ratio', hue='Gender', data=vulnerable_likelihood)
plt.title('Likelihood Ratio for Vulnerable Demographics')
plt.xlabel('Age Group')
plt.ylabel('Likelihood Ratio')
plt.legend(title='Gender')

# Plotting Severity Ratio for Vulnerable Demographics
plt.subplot(1, 2, 2)
sns.barplot(x='Age', y='Severity Ratio', hue='Gender', data=vulnerable_severity)
plt.title('Severity Ratio for Vulnerable Demographics')
plt.xlabel('Age Group')
plt.ylabel('Severity Ratio')
plt.legend(title='Gender')

plt.tight_layout()
plt.show()

# Print the results in text form
print("Likelihood Ratio for Vulnerable Demographics:")
print(vulnerable_likelihood)

print("\nSeverity Ratio for Vulnerable Demographics:")
print(vulnerable_severity)

"""3. Explore if certain time periods have higher incident rates. Analyze temporal patterns in incidents."""

# Assuming 'Date' is in datetime format
data['Date'] = pd.to_datetime(data['Date'])

# Extract time-related features
data['Year'] = data['Date'].dt.year
data['Month'] = data['Date'].dt.month
data['Day'] = data['Date'].dt.day
data['DayOfWeek'] = data['Date'].dt.day_name()

# Count incidents based on time-related features
time_period_counts = data.groupby(['Year', 'Month', 'Day', 'DayOfWeek']).size().reset_index(name='Count')

# Calculate incident rates per day
total_days = (data['Date'].max() - data['Date'].min()).days + 1
incident_rates = time_period_counts.groupby('DayOfWeek')['Count'].mean() / total_days * 100  # Convert to percentage

# Visualize incident counts over time
plt.figure(figsize=(16, 8))
sns.lineplot(data=time_period_counts, x='Month', y='Count', hue='Year', marker='o', palette='bright')
plt.title('Incident Counts Over Time')
plt.xlabel('Month')
plt.ylabel('Incident Count')
plt.legend(title='Year', loc='lower left')
plt.xticks(range(1, 13))
plt.show()

# Print the incident rates for each day of the week
print("Incident Rates by Day of the Week:")
print(incident_rates)

# Determine if more accidents occur on weekends
weekend_days = ['Saturday', 'Sunday']
weekend_incidents = time_period_counts[time_period_counts['DayOfWeek'].isin(weekend_days)]['Count'].sum()
weekday_incidents = time_period_counts[~time_period_counts['DayOfWeek'].isin(weekend_days)]['Count'].sum()

print("\nTotal Incidents on Weekends:", weekend_incidents)
print("Total Incidents on Weekdays:", weekday_incidents)

# Calculate the percentage of incidents on weekends
percentage_weekend_incidents = (weekend_incidents / (weekend_incidents + weekday_incidents)) * 100
print(f"\nPercentage of Incidents on Weekends: {percentage_weekend_incidents:.2f}%")

# Calculate average incident count per month
monthly_avg = time_period_counts.groupby('Month')['Count'].mean()

# Calculate average incident count per year
yearly_avg = time_period_counts.groupby('Year')['Count'].mean()

# Print the results
print("Monthly Average Incident Counts:")
print(monthly_avg)

print("\nYearly Average Incident Counts:")
print(yearly_avg)

# Visualize monthly average incident counts
plt.figure(figsize=(12, 6))
monthly_avg.plot(kind='line', marker='o', color='skyblue')
plt.xticks(range(1, 13))
plt.title('Monthly Average Incident Counts')
plt.xlabel('Month')
plt.ylabel('Average Incident Count')
plt.show()

# Visualize yearly average incident counts
plt.figure(figsize=(12, 6))
yearly_avg.plot(kind='line', marker='o', color='orange')
plt.xticks(range(2014, 2024))
plt.title('Yearly Average Incident Counts')
plt.xlabel('Year')
plt.ylabel('Average Incident Count')
plt.show()



"""4. Comparing Safety Records of Different Operators: Compare incident rates and severity between operators. Assess differences in safety records."""

# Calculate incident rates
operator_incident_rates = data.groupby('Operator')['Incident type'].count() / data.groupby('Operator')['Incident type'].nunique()

# Calculate severity
severity_counts = data.groupby(['Operator', 'Severity']).size().unstack(fill_value=0)
severity_counts['Total'] = severity_counts.sum(axis=1)
severity_counts['Severity Rate'] = severity_counts['Severe'] / severity_counts['Total']

# Normalize data
incident_rates_normalized = (operator_incident_rates - operator_incident_rates.min()) / (operator_incident_rates.max() - operator_incident_rates.min())
severity_rates_normalized = (severity_counts['Severity Rate'] - severity_counts['Severity Rate'].min()) / (severity_counts['Severity Rate'].max() - severity_counts['Severity Rate'].min())

# Combine normalized data into a single DataFrame
combined_data = pd.concat([incident_rates_normalized, severity_rates_normalized], axis=1)

# Visualize combined bar chart
plt.figure(figsize=(12, 6))
combined_data.plot(kind='bar', stacked=False, colormap='viridis')
plt.title('Incident Rates and Severity Rates by Operator')
plt.xlabel('Operator')
plt.ylabel('Normalized Rate')
plt.legend()
plt.show()

print("\nNormalized Incident Rates:")
print(incident_rates_normalized)

print("\nSeverity Rates by Operator:")
print(severity_rates_normalized)

"""5.Garage Location and Incident Frequency: Investigate if garage location correlates with incidents. Evaluate impact of garage placement on safety."""

# Group data by garage location and incident type
garage_incident_counts = data.groupby(['Garage', 'Incident type']).size().unstack(fill_value=0)

# Calculate the total incidents by garage location
garage_total_incidents = garage_incident_counts.sum(axis=1)

# Normalize the incident counts by the total incidents for each garage location
garage_incident_rates = garage_incident_counts.div(garage_total_incidents, axis=0) * 100  # Multiply by 100 to get percentages


# Plotting the comparison with proper percentage formatting
plt.figure(figsize=(20, 20))
sns.heatmap(garage_incident_rates, cmap="Blues", annot=True, fmt=".2f", cbar_kws={'label': 'Incident Rate (%)'})
plt.title('Incident Rates by Garage Location')
plt.xlabel('Incident Type')
plt.ylabel('Garage Location')
plt.show()

# Get the top 3 garages for each incident type
top3_garages = garage_incident_rates.apply(lambda column: ', '.join(column.nlargest(3).index))

# Print the top 3 garages for each incident type
for incident_type, top_garages in top3_garages.items():
    print(f'Top 3 Garages for Incident Type "{incident_type}": {top_garages}')

from scipy.stats import chi2_contingency


# Chi-squared test for each incident type to evaluate the impact of garage placement
chi2_results = {}

for incident_type in garage_incident_rates.columns:
    contingency_table = pd.crosstab(garage_incident_rates.index, garage_incident_rates[incident_type])
    _, p_value, _, _ = chi2_contingency(contingency_table)
    chi2_results[incident_type] = p_value

# Identify incident types with significant impact based on p-values
significant_incident_types = [incident_type for incident_type, p_value in chi2_results.items() if p_value < 0.05]

# Check if there are significant incident types before creating the heatmap
if significant_incident_types:
    # Visualize incident rates for significant incident types
    plt.figure(figsize=(20, 10))
    sns.heatmap(garage_incident_rates[significant_incident_types], cmap="Blues", annot=True, fmt=".2f", cbar_kws={'label': 'Incident Rate (%)'})
    plt.title('Incident Rates by Garage Location (Significant Incident Types)')
    plt.xlabel('Incident Type')
    plt.ylabel('Garage Location')
    plt.show()
else:
    print("No incident types with significant impact.")

"""6.Effect of Incident Type on Injury Outcomes: Analyze how incident types influence injury severity. Identify incident types leading to more severe injuries."""

# Create a cross-tabulation of incident types and injury outcomes
incident_severity_cross = pd.crosstab(data['Incident type'], data['Injury outcome'])

# Visualize incident outcomes for each incident type
plt.figure(figsize=(14, 8))
sns.heatmap(incident_severity_cross, annot=True, cmap='viridis', cbar=True, fmt='d')
plt.title('Incident Outcomes by Incident Type')
plt.xlabel('Injury Outcome')
plt.ylabel('Incident Type')
plt.show()

# Find incident types leading to more severe injuries
most_severe_incidents = incident_severity_cross.idxmax(axis=0)

# Display the results
print("Incident types leading to more severe injuries:")
print(most_severe_incidents)

"""7.Long-term Trends in Incident Rates: Study long-term trends in incident rates over multiple years. Provide insights for long-term safety planning."""

# Convert 'Date' to datetime format
data['Date'] = pd.to_datetime(data['Date'])

# Extract time-related features
data['Year'] = data['Date'].dt.year

# Count incidents based on time-related features
incident_counts = data.groupby('Year').size().reset_index(name='Incident Count')

# Calculate Year-over-Year (YOY) Change
incident_counts['YOY Change'] = incident_counts['Incident Count'].pct_change() * 100

# Calculate 5-Year Rolling Average
incident_counts['5-Year Rolling Avg'] = incident_counts['Incident Count'].rolling(window=5).mean()

# Visualize incident counts, YOY Change, and 5-Year Rolling Average
plt.figure(figsize=(16, 8))

# Incident Counts Over Time
plt.subplot(2, 1, 1)
sns.lineplot(data=incident_counts, x='Year', y='Incident Count', marker='o')
plt.xticks(range(2014, 2024))
plt.title('Incident Counts Over Time')
plt.xlabel('Year')
plt.ylabel('Incident Count')

# YOY Change
plt.subplot(2, 1, 2)
sns.lineplot(data=incident_counts, x='Year', y='YOY Change', marker='o', color='orange')
plt.axhline(0, color='gray', linestyle='--', linewidth=1)  # Zero line for reference
plt.xticks(range(2015, 2024))  # Start from the second year for YOY Change
plt.title('Year-over-Year (YOY) Change in Incident Counts')
plt.xlabel('Year')
plt.ylabel('YOY Change (%)')

plt.tight_layout()
plt.show()

# Display the DataFrame with YOY Change and 5-Year Rolling Average
print(incident_counts)

"""8.Comparative Safety Analysis by Borough: Compare incident rates and types across boroughs. Identify high-risk areas for certain incident types."""

# Group data by borough and incident type
borough_incident_counts = data.groupby(['Borough', 'Incident type']).size().unstack(fill_value=0)

# Calculate the total incidents by borough
borough_total_incidents = borough_incident_counts.sum(axis=1)

# Normalize the incident counts by the total incidents for each borough
borough_incident_rates = borough_incident_counts.div(borough_total_incidents, axis=0) * 100  # Multiply by 100 to get percentages

# Identify top 5 high-risk areas for all incident types
top_high_risk_areas = {}

# Get a list of all unique incident types
incident_types_of_interest = data['Incident type'].unique()

# Calculate the number of rows and columns needed for subplots
num_incident_types = len(incident_types_of_interest)
num_rows = (num_incident_types + 1) // 2  # Add 1 to handle odd number of incident types
num_cols = 2

# Plotting the comparison with proper percentage formatting
plt.figure(figsize=(15, 5 * num_rows))

for i, incident_type in enumerate(incident_types_of_interest, 1):
    plt.subplot(num_rows, num_cols, i)

    # Find top 5 high-risk areas for each incident type
    top_areas = borough_incident_rates[incident_type].nlargest(5)

    # Bar graph for top 5 high-risk areas
    top_areas.plot(kind='bar', color='skyblue')
    plt.title(f'Top 5 High-Risk Areas for {incident_type}')
    plt.xlabel('Borough')
    plt.ylabel('Incident Rate (%)')

plt.tight_layout()
plt.show()

# Additional heatmap
plt.figure(figsize=(20,20))
sns.heatmap(borough_incident_rates, cmap="Blues", annot=True, fmt=".2f", cbar_kws={'label': 'Incident Rate (%)'})
plt.title('Incident Rates by Borough')
plt.xlabel('Incident Type')
plt.ylabel('Borough')

plt.tight_layout()
plt.show()

# Display the top 5 high-risk areas for each incident type
for incident_type in incident_types_of_interest:
    top_areas = borough_incident_rates[incident_type].nlargest(5)
    print(f'\nTop 5 High-Risk Areas for {incident_type}:\n')
    print(top_areas.to_string())

"""9.Predictive Modeling for Incident Occurrence: Develop predictive model to forecast incidents based on route, operator, demographics, etc."""

data=pd.read_csv("injury-details-2023-q2.csv")
pd.options.display.max_columns = None
display(data)
data.info()

#Preprocessing

data = data.dropna() # drop rows with any missing values
data = data.dropna(axis=1) # drop columns with any missing values
data.info()

data = data.drop(columns=['ID','Injury'])

# Initialize the LabelEncoder
label_encoder = LabelEncoder()

# List of columns to be label encoded
columns_to_encode = ['Route', 'Operator', 'Borough', 'Garage', 'Incident type', 'Injury outcome', 'Victim category', 'Age', 'Gender']

# Apply label encoding to the specified columns
data[columns_to_encode] = data[columns_to_encode].apply(lambda col: label_encoder.fit_transform(col))

# Convert the date column to a date variable
data['Date'] = pd.to_datetime(data['Date'])

# Extract the year from the date column
data['Date']  = data['Date'].dt.year

data

#Heatmap
corr = data.corr()
plt.figure(figsize=(18, 15))
sns.heatmap(corr, annot=True, vmin=-1.0, cmap='mako')
plt.title("Correlation Heatmap")
plt.show()

# Data preparation
X = data.drop(columns=['Incident type', 'Date'])
y = data['Incident type']

# Assuming 'y' is your target variable
class_distribution = pd.value_counts(y)
class_distribution.plot(kind='bar', rot=0)
plt.xlabel('Class')
plt.ylabel('Count')
plt.title('Class Distribution')
plt.show()

from imblearn.over_sampling import RandomOverSampler
# Example of oversampling the minority class
oversampler = RandomOverSampler(sampling_strategy='minority')
X_resampled, y_resampled = oversampler.fit_resample(X, y)
X= X_resampled
y= y_resampled
# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)

from imblearn import under_sampling, over_sampling
summary = over_sampling.RandomOverSampler().fit_resample(X, y)
print("Class distribution after oversampling:", pd.value_counts(summary[1]))

dummy_classifier=DummyClassifier(strategy='stratified')
dummy_classifier.fit(X_train,y_train)
baseline_acc=dummy_classifier.score(X_test,y_test)
print("Baseline Accuracy: {:.2f}".format(baseline_acc))

#Model1
#Linear SVC
# Create LinearSVC object and fit the model
lsvc = LinearSVC(dual=False)
lsvc.fit(X_train, y_train)
# Predict on the test set
y_pred_test = lsvc.predict(X_test)
# Calculate accuracy
lsvc_accuracy = accuracy_score(y_test, y_pred_test)
print("Accuracy:",lsvc_accuracy)
cv1 = cross_val_score(lsvc, X_train, y_train, cv=5)
cv1_mean = cv1.mean()
print("Cross-validation:",cv1_mean)

print("Classification Report:")
print(classification_report(y_test, y_pred_test, zero_division=1))

#Model2 KNN

k_values = range(1, 40)  # Range of k values to try
accuracy_scores = []

for k in k_values:
    knn = KNeighborsClassifier(n_neighbors=k)
    knn.fit(X_train, y_train)
    y_pred = knn.predict(X_test)
    accuracy = np.mean(y_pred == y_test)  # Calculate accuracy
    accuracy_scores.append(accuracy)

# Plot the accuracy scores for different k values
plt.plot(k_values, accuracy_scores)
plt.xlabel('Number of Neighbors (k)')
plt.ylabel('Accuracy')
plt.title('K-Nearest Neighbors - Accuracy vs. Number of Neighbors')

best_k = k_values[np.argmax(accuracy_scores)]
print("Best value of k: {}".format(best_k))

k = 27  # Number of neighbors
knn = KNeighborsClassifier(n_neighbors=k)
knn.fit(X_train, y_train)
y_pred = knn.predict(X_test)


# Predict on the test set
y_pred_test = knn.predict(X_test)
# Calculate accuracy
accuracy = accuracy_score(y_test, y_pred_test)
print("Accuracy:",accuracy)
cv1 = cross_val_score(knn, X_train, y_train, cv=5)
cv1_mean = cv1.mean()
print("Cross-validation:",cv1_mean)

print("Classification Report:")
print(classification_report(y_test, y_pred, zero_division=1))

#Model 3
#SVC
# Create SVC object and fit the model
svc = SVC()
svc.fit(X_train, y_train)
# Predict on the test set
y_pred_test = svc.predict(X_test)
# Calculate accuracy
accuracy = accuracy_score(y_test, y_pred_test)
print("Accuracy:",accuracy)
cv1 = cross_val_score(svc, X_train, y_train, cv=5)
cv1_mean = cv1.mean()
print("Cross-validation:",cv1_mean)

print("Classification Report:")
print(classification_report(y_test, y_pred_test, zero_division=1))

#Model4
#Logistic Regression
logReg = LogisticRegression(max_iter=20,random_state=42)
logReg.fit(X_train, y_train)
y_pred = logReg.predict(X_test)
accuracy = metrics.accuracy_score(y_test, y_pred)
print("Accuracy:",accuracy)

cv1 = cross_val_score(logReg, X_train, y_train, cv=5)
cv1_mean = cv1.mean()
print("Cross-validation:",cv1_mean)

print("Classification Report:")
print(classification_report(y_test, y_pred, zero_division=1))

#Model 5
#Random forest n_estimator and testing accuracy
scoresrf =[]
for k in range(1, 200):
    rfc = RandomForestClassifier(n_estimators=k)
    rfc.fit(X_train, y_train)
    y_predrf = rfc.predict(X_test)
    scoresrf.append(accuracy_score(y_test, y_predrf))
import matplotlib.pyplot as plt
plt.plot(range(1, 200), scoresrf)
plt.xlabel('Value of n_estimators for Random Forest Classifier')
plt.ylabel('Testing Accuracy')

best_n_estimators = scoresrf.index(max(scoresrf)) + 1
print("Best value of n_estimators: {}".format(best_n_estimators))

#Random Forest model
model_rf = RandomForestClassifier(n_estimators=156, max_features= 6, random_state=42)
model_rf.fit(X_train, y_train)
predict_rf = model_rf.predict(X_test)
accuracy_rf = accuracy_score(y_test, predict_rf)
print("Accuracy:", accuracy_rf)
#cross-validation
rfcv = cross_val_score(model_rf, X_train, y_train, scoring='accuracy', cv=5)
rfcv = pd.Series(rfcv)
print("Cross-validation: ", rfcv.mean())

print("Classification Report:")
print(classification_report(y_test, predict_rf, zero_division=1))

# Gradient Boosting Classifier
from sklearn.ensemble import GradientBoostingClassifier

gbc = GradientBoostingClassifier()
gbc.fit(X_train, y_train)
y_pred_gbc = gbc.predict(X_test)

print("GBM Accuracy: ", accuracy_score(y_test, y_pred_gbc))

#cross-validation
rfcv = cross_val_score(gbc, X_train, y_train, scoring='accuracy', cv=5)
rfcv = pd.Series(rfcv)
print("Cross-validation: ", rfcv.mean())

print("Classification Report:")
print(classification_report(y_test, y_pred_gbc, zero_division=1))

# XGBoost
import xgboost as xgb

xgb_model = xgb.XGBClassifier()
xgb_model.fit(X_train, y_train)
y_pred_xgb = xgb_model.predict(X_test)

print("XGBoost Accuracy: ", accuracy_score(y_test, y_pred_xgb))

print("Classification Report:")
print(classification_report(y_test, y_pred_xgb, zero_division=1))

importances_gbc = gbc.feature_importances_

# Print feature importances
for feature, importance in zip(X_train.columns, importances_gbc):
    print(f"{feature}: {importance}")

import matplotlib.pyplot as plt

# Assuming importances_gbc is your list of feature importances
features = X_train.columns

# Sorting features by importance
sorted_indices = importances_gbc.argsort()[::-1]
sorted_features = [features[i] for i in sorted_indices]
sorted_importances = [importances_gbc[i] for i in sorted_indices]

# Plotting the feature importances
plt.figure(figsize=(10, 6))
plt.barh(sorted_features, sorted_importances, color='green')
plt.xlabel('Importance')
plt.title('Feature Importances for Gradient Boosting Classifier')
plt.show()

# Stacking Ensemble
from sklearn.ensemble import StackingClassifier

estimators = [('rf', model_rf), ('gbc', gbc)]
stacker = StackingClassifier(estimators=estimators, final_estimator=LogisticRegression(max_iter=1000))

stacker.fit(X_train, y_train)
y_pred_stacker = stacker.predict(X_test)

print("Stacking Ensemble Accuracy: ", accuracy_score(y_test, y_pred_stacker))

print("Classification Report:")
print(classification_report(y_test, y_pred_stacker, zero_division=1))

# Assuming stacker is your stacking ensemble model
importances_lr = stacker.final_estimator_.coef_[0]

# Print feature importances
for feature, importance in zip(X_train.columns, importances_lr):
    print(f"{feature}: {importance}")


features = X_train.columns

# Selecting the top N features
top_n = 8  # You can adjust this based on the number of features you want to visualize
top_features = features[:top_n]
top_importances = importances_lr[:top_n]

# Plotting the feature importances
plt.figure(figsize=(10, 6))
plt.barh(top_features, top_importances, color='skyblue')
plt.xlabel('Importance')
plt.title('Top Feature Importances for Stacking Ensemble')
plt.show()

# Make predictions on new data
new_data = pd.DataFrame({
    'Route': [485],
    'Operator': [5],
    'Borough': [37],
    'Garage': [71],
    'Injury outcome': [4],
    'Victim category': [7],
    'Age': [1],
    'Gender': [2]
})

predictions = stacker.predict(new_data)
print(predictions)

# Make predictions on new data
new_data = pd.DataFrame({
    'Route': [688],
    'Operator': [6],
    'Borough': [46],
    'Garage': [81],
    'Injury outcome': [2],
    'Victim category': [7],
    'Age': [3],
    'Gender': [1]
})

predictions = stacker.predict(new_data)
print(predictions)

# Make predictions on new data
new_data = pd.DataFrame({
    'Route': [133],
    'Operator': [4],
    'Borough': [7],
    'Garage': [60],
    'Injury outcome': [5],
    'Victim category': [8],
    'Age': [0],
    'Gender': [1]
})

predictions = stacker.predict(new_data)
print(predictions)

# Get predicted values
y_pred_test = lsvc.predict(X_test)

# Sort actual and predicted values for plotting
y_test = np.sort(y_test)
y_pred_test = np.sort(y_pred_test)

# Plot
plt.plot(y_test, color='b', label='Actual')
plt.plot(y_pred_test, color='r', label='Predicted')
plt.title('Actual vs Predicted: Linear SVC')
plt.xlabel('Sample Index')
plt.ylabel('Target Value')
plt.legend()

plt.show()

# Get predicted values
y_pred_test = knn.predict(X_test)

# Sort actual and predicted values for plotting
y_test = np.sort(y_test)
y_pred_test = np.sort(y_pred_test)

# Plot
plt.plot(y_test, color='b', label='Actual')
plt.plot(y_pred_test, color='r', label='Predicted')
plt.title('Actual vs Predicted: KNN')
plt.xlabel('Sample Index')
plt.ylabel('Target Value')
plt.legend()

plt.show()

# Get predicted values
y_pred_test = svc.predict(X_test)

# Sort actual and predicted values for plotting
y_test = np.sort(y_test)
y_pred_test = np.sort(y_pred_test)

# Plot
plt.plot(y_test, color='b', label='Actual')
plt.plot(y_pred_test, color='r', label='Predicted')
plt.title('Actual vs Predicted: SVC')
plt.xlabel('Sample Index')
plt.ylabel('Target Value')
plt.legend()

plt.show()

# Get predicted values
y_pred_test = logReg.predict(X_test)

# Sort actual and predicted values for plotting
y_test = np.sort(y_test)
y_pred_test = np.sort(y_pred_test)

# Plot
plt.plot(y_test, color='b', label='Actual')
plt.plot(y_pred_test, color='r', label='Predicted')
plt.title('Actual vs Predicted: Logistic Regression')
plt.xlabel('Sample Index')
plt.ylabel('Target Value')
plt.legend()

plt.show()

# Get predicted values
y_pred_test = model_rf.predict(X_test)

# Sort actual and predicted values for plotting
y_test = np.sort(y_test)
y_pred_test = np.sort(y_pred_test)

# Plot
plt.plot(y_test, color='b', label='Actual')
plt.plot(y_pred_test, color='r', label='Predicted')
plt.title('Actual vs Predicted: Random Forest')
plt.xlabel('Sample Index')
plt.ylabel('Target Value')
plt.legend()

plt.show()

# Get predicted values
y_pred_test = gbc.predict(X_test)

# Sort actual and predicted values for plotting
y_test = np.sort(y_test)
y_pred_test = np.sort(y_pred_test)

# Plot
plt.plot(y_test, color='b', label='Actual')
plt.plot(y_pred_test, color='r', label='Predicted')
plt.title('Actual vs Predicted: GBC')
plt.xlabel('Sample Index')
plt.ylabel('Target Value')
plt.legend()

plt.show()

# Get predicted values
y_pred_test = xgb_model.predict(X_test)

# Sort actual and predicted values for plotting
y_test = np.sort(y_test)
y_pred_test = np.sort(y_pred_test)

# Plot
plt.plot(y_test, color='b', label='Actual')
plt.plot(y_pred_test, color='r', label='Predicted')
plt.title('Actual vs Predicted: XGB')
plt.xlabel('Sample Index')
plt.ylabel('Target Value')
plt.legend()

plt.show()

# Get predicted values
y_pred_test = stacker.predict(X_test)

# Sort actual and predicted values for plotting
y_test = np.sort(y_test)
y_pred_test = np.sort(y_pred_test)

# Plot
plt.plot(y_test, color='b', label='Actual')
plt.plot(y_pred_test, color='r', label='Predicted')
plt.title('Actual vs Predicted: Stacking Ensemble')
plt.xlabel('Sample Index')
plt.ylabel('Target Value')
plt.legend()

plt.show()

# Number of training iterations
num_iterations = 10

# Lists to store training and test accuracies
train_accuracies = []
test_accuracies = []

# Loop through multiple iterations
for iteration in range(num_iterations):
    # Fit the model on the training data for the current iteration
    lsvc.fit(X_train, y_train)

    # Predict on the training set
    y_pred_train = lsvc.predict(X_train)

    # Calculate training accuracy
    train_accuracy = accuracy_score(y_train, y_pred_train)
    train_accuracies.append(train_accuracy)

    # Predict on the test set
    y_pred_test = lsvc.predict(X_test)

    # Calculate test accuracy
    test_accuracy = accuracy_score(y_test, y_pred_test)
    test_accuracies.append(test_accuracy)

# Plot the training vs. test accuracy graph
plt.plot(range(1, num_iterations + 1), train_accuracies, label='Training Accuracy', marker='o')
plt.plot(range(1, num_iterations + 1), test_accuracies, label='Test Accuracy', marker='o')
plt.xlabel('Training Iterations')
plt.ylabel('Accuracy')
plt.title('Training vs. Test Accuracy: Linear SVC')
plt.legend()
plt.grid(True)
plt.show()

from sklearn.model_selection import learning_curve
from sklearn.metrics import roc_curve, auc
from sklearn.preprocessing import label_binarize
from sklearn.multiclass import OneVsRestClassifier

# Learning Curves
def plot_learning_curve(estimator, title, X, y, ylim=None, cv=None, n_jobs=None, train_sizes=np.linspace(.1, 1.0, 5)):
    plt.figure()
    plt.title(title)
    if ylim is not None:
        plt.ylim(*ylim)
    plt.xlabel("Training examples")
    plt.ylabel("Score")
    train_sizes, train_scores, test_scores = learning_curve(
        estimator, X, y, cv=cv, n_jobs=n_jobs, train_sizes=train_sizes)
    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)
    plt.grid()

    plt.fill_between(train_sizes, train_scores_mean - train_scores_std,
                     train_scores_mean + train_scores_std, alpha=0.1,
                     color="r")
    plt.fill_between(train_sizes, test_scores_mean - test_scores_std,
                     test_scores_mean + test_scores_std, alpha=0.1, color="g")
    plt.plot(train_sizes, train_scores_mean, 'o-', color="r",
             label="Training score")
    plt.plot(train_sizes, test_scores_mean, 'o-', color="g",
             label="Cross-validation score")

    plt.legend(loc="best")
    return plt

# ROC Curves
def plot_roc_curve(y_test, y_scores, model_name):
    n_classes = len(np.unique(y_test))
    y_test_bin = label_binarize(y_test, classes=np.unique(y_test))

    fpr = dict()
    tpr = dict()
    roc_auc = dict()

    for i in range(n_classes):
        fpr[i], tpr[i], _ = roc_curve(y_test_bin[:, i], y_scores[:, i])
        roc_auc[i] = auc(fpr[i], tpr[i])

    # Micro-average ROC curve and ROC area
    fpr["micro"], tpr["micro"], _ = roc_curve(y_test_bin.ravel(), y_scores.ravel())
    roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])

    # Plot ROC curve
    plt.figure(figsize=(8, 6))
    plt.plot(fpr["micro"], tpr["micro"],
             label=f'Micro-average ROC curve (area = {roc_auc["micro"]:0.2f})',
             color='deeppink', linestyle=':', linewidth=4)

    for i in range(n_classes):
        plt.plot(fpr[i], tpr[i], label=f'ROC curve - Class {i} (area = {roc_auc[i]:0.2f})')

    plt.plot([0, 1], [0, 1], 'k--', lw=2)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(f'ROC Curve - {model_name}')
    plt.legend(loc="lower right")
    plt.show()

# Plot Learning Curves
plot_learning_curve(stacker, "Learning Curve - Stacking Ensemble", X_train, y_train, cv=5, n_jobs=-1)
plot_learning_curve(xgb_model, "Learning Curve - XGBoost", X_train, y_train, cv=5, n_jobs=-1)
plot_learning_curve(model_rf, "Learning Curve - Random Forest", X_train, y_train, cv=5, n_jobs=-1)

# Plot ROC Curves
y_scores_stacker = stacker.predict_proba(X_test)
plot_roc_curve(y_test, y_scores_stacker, "Stacking Ensemble")

y_scores_xgb = xgb_model.predict_proba(X_test)
plot_roc_curve(y_test, y_scores_xgb, "XGBoost")

y_scores_rf = model_rf.predict_proba(X_test)
plot_roc_curve(y_test, y_scores_rf, "Random Forest")
