"""Script to get data for core functions."""

from BackEnd import core

from timeit import default_timer as timer
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os

sns.set_theme(color_codes=True)

# time it takes creating share packages with variable secret length

number_of_bytes = range(1, 50)
number_of_packages = 5
number_threshold = 5
data_points = None

for i in range(0, len(number_of_bytes)):
    mock_secret = os.urandom(number_of_bytes[i])
    start = timer()
    core.split_large_secret_into_share_packages(mock_secret, number_threshold, number_of_packages)
    stop = timer()
    if i == 0:
        data_points = np.array([[number_of_bytes[i], stop - start]])
    else:
        data_points = np.append(data_points, np.array([[number_of_bytes[i], stop - start]]), axis=0)


print(pd.DataFrame(data_points))

dataframe = pd.DataFrame(data=data_points[:, 1:])

sns.lineplot(data=dataframe)
plt.title('Large Secret: Time per length of secret in bytes.')
plt.legend('Data')
plt.ylabel('Time')
plt.xlabel('Bytes')
plt.show()


x = data_points[0:, 0]
y = data_points[0:, 1]
x, y = pd.Series(x), pd.Series(y)
sns.regplot(x=x, y=y)
plt.title('Large Secret: Time per length of secret in bytes.')
plt.legend('Data')
plt.ylabel('Time')
plt.xlabel('Bytes')
plt.show()


# time it takes creating share packages with variable package number

number_of_bytes = 32
number_threshold = 5
number_of_packages = range(2, 100)
data_points = None

for i in range(0, len(number_of_packages)):
    mock_secret = os.urandom(number_of_bytes)
    start = timer()
    core.split_large_secret_into_share_packages(mock_secret, number_threshold, number_of_packages[i])
    stop = timer()
    if i == 0:
        data_points = np.array([[number_of_packages[i], stop - start]])
    else:
        data_points = np.append(data_points, np.array([[number_of_packages[i], stop - start]]), axis=0)


print(pd.DataFrame(data_points))

dataframe = pd.DataFrame(data=data_points[:, 1:])

sns.lineplot(data=dataframe)
plt.title('Large Secret: Time per number of packages created.')
plt.legend('Data')
plt.ylabel('Time')
plt.xlabel('Packages')
plt.show()


x = data_points[0:, 0]
y = data_points[0:, 1]
x, y = pd.Series(x), pd.Series(y)
sns.regplot(x=x, y=y)
plt.title('Large Secret: Time per number of packages created.')
plt.legend('Data')
plt.ylabel('Time')
plt.xlabel('Packages')
plt.show()
plt.show()


# time it takes creating share packages with variable threshold number

number_of_bytes = 32
number_threshold = range(2, 100)
number_of_packages = 5
data_points = None

for i in range(0, len(number_threshold)):
    mock_secret = os.urandom(number_of_bytes)
    start = timer()
    core.split_large_secret_into_share_packages(mock_secret, number_threshold[i], number_of_packages)
    stop = timer()
    if i == 0:
        data_points = np.array([[number_threshold[i], stop - start]])
    else:
        data_points = np.append(data_points, np.array([[number_threshold[i], stop - start]]), axis=0)


print(pd.DataFrame(data_points))

dataframe = pd.DataFrame(data=data_points[:, 1:])

sns.lineplot(data=dataframe)
plt.title('Large Secret: Time per threshold of shamir algorithm.')
plt.legend('Data')
plt.ylabel('Time')
plt.xlabel('Threshold')
plt.show()


x = data_points[0:, 0]
y = data_points[0:, 1]
x, y = pd.Series(x), pd.Series(y)
sns.regplot(x=x, y=y, color="g")
plt.title('Large Secret: Time per threshold of shamir algorithm.')
plt.legend('Data')
plt.ylabel('Time')
plt.xlabel('Threshold')
plt.show()


# time it takes to restore packages from minimum threshold

number_of_bytes = 32
number_threshold = range(2, 100)
number_of_packages = 100
data_points = None


for i in range(0, len(number_threshold)):
    mock_secret = os.urandom(number_of_bytes)
    packages = core.split_large_secret_into_share_packages(mock_secret, number_threshold[i], number_of_packages)
    start = timer()
    core.recover_large_secret(packages)
    stop = timer()
    if i == 0:
        data_points = np.array([[number_threshold[i], stop - start]])
    else:
        data_points = np.append(data_points, np.array([[number_threshold[i], stop - start]]), axis=0)


print(pd.DataFrame(data_points))

dataframe = pd.DataFrame(data=data_points[:, 1:])

sns.lineplot(data=dataframe)
plt.title('Large Secret: Time per restore with threshold variance.')
plt.legend('Data')
plt.ylabel('Time')
plt.xlabel('Threshold')
plt.show()


x = data_points[0:, 0]
y = data_points[0:, 1]
x, y = pd.Series(x), pd.Series(y)
sns.regplot(x=x, y=y, color="g", order=2)
plt.title('Large Secret: Time per restore with threshold variance.')
plt.legend('Data')
plt.ylabel('Time')
plt.xlabel('Threshold')
plt.show()


