# Copyright 2020 Joseph Lin Chu
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import numpy as np

class StarCluster(object):
    """Star Clustering Algorithm"""
    
    def fit(self, X):
        # Set Constant of Proportionality
        golden_ratio = ((1.0 + (5.0 ** 0.5)) / 2.0)
        # Number of Nodes
        n = X.shape[0]
        # Number of Features
        d = X.shape[1]

        # Construct Node-To-Node Matrix of Distances
        distances_matrix = np.zeros((n, n, d), dtype='float32')
        for i in range(n):
            for j in range(n):
                distances_matrix[i, j] = X[i] - X[j]
        distances_matrix = np.linalg.norm(distances_matrix, axis=-1)

        # Determine Average Distance And Extend By Constant of Proportionality To Set Limit
        limit = np.sum(distances_matrix) / (n * n - n) * golden_ratio

        # Construct List of Distances Less Than Limit
        distances_list = []
        for i in range(n):
            for j in range(n):
                if i < j:
                    distances_list.append((i, j, distances_matrix[i, j]))

        # Sort List of Distances From Shortest To Longest
        distances_list.sort(key=lambda x: x[2])

        # Build Matrix of Connections Starting With Closest Pairs Until Average Mass Exceeds Limit
        empty_clusters = []
        mindex = 0
        self.labels_ = np.zeros(n, dtype='int32') - 1
        mass = np.zeros(n, dtype='float32')
        while np.mean(mass) <= limit:
            i, j, distance = distances_list[mindex]
            mass[i] += distance
            mass[j] += distance
            if self.labels_[i] == -1 and self.labels_[j] == -1:
                if not empty_clusters:
                    empty_clusters = [np.max(self.labels_) + 1]
                empty_clusters.sort()
                cluster = empty_clusters.pop(0)
                self.labels_[i] = cluster
                self.labels_[j] = cluster
            elif self.labels_[i] == -1:
                self.labels_[i] = self.labels_[j]
            elif self.labels_[j] == -1:
                self.labels_[j] = self.labels_[i]
            elif self.labels_[i] < self.labels_[j]:
                empty_clusters.append(self.labels_[j])
                self.labels_[np.argwhere(self.labels_ == self.labels_[j])] = self.labels_[i]
            elif self.labels_[j] < self.labels_[i]:
                empty_clusters.append(self.labels_[i])
                self.labels_[np.argwhere(self.labels_ == self.labels_[i])] = self.labels_[j]
            mindex += 1

        distances_matrix[distances_matrix == 0.0] = np.inf
        # Reduce Mass of Each Node By Effectively Twice The Distance To Nearest Neighbour
        for i in range(n):
            mindex = np.argmin(distances_matrix[i])
            distance = distances_matrix[i, mindex]
            mass[i] -= distance
            mass[mindex] -= distance

        # Set Threshold Based On Average Modified By Deviation Reduced By Constant of Proportionality
        threshold = np.mean(mass) - np.std(mass) / golden_ratio

        # Disconnect Lower Mass Nodes
        for i in range(n):
            if mass[i] <= threshold:
                self.labels_[i] = -1

        # Ignore Masses of Nodes In Clusters Now
        mass[self.labels_ != -1] = -np.inf

        # Go Through Disconnected Nodes From Highest To Lowest Mass And Reconnect To Nearest Neighbour That Hasn't Already Connected To It Earlier
        while -1 in self.labels_:
            i = np.argmax(mass)
            mindex = i
            while self.labels_[mindex] == -1:
                mindex = np.argmin(distances_matrix[i])
                distance = distances_matrix[i, mindex]
                distances_matrix[i, mindex] = np.inf
            self.labels_[i] = self.labels_[mindex]
            mass[i] = -np.inf

        return self

    def predict(self, X):
        self.fit(X)
        return self.labels_