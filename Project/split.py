import pandas as pd
import numpy as np

data = pd.read_csv(r'/Users/leo/Downloads/BTCUSD_241227-bookTicker-2024-09-01.csv', sep=",")
data["price"] = (data["best_bid_price"]+data["best_ask_price"])/2
df = data[["event_time", "price"]]
# df["event_time"] = pd.to_datetime(df["event_time"], unit='ms')


class MultipleTimeSeriesCV:
    """Generates tuples of train_idx, test_idx pairs
    Assumes the MultiIndex contains levels 'symbol' and 'date'
    purges overlapping outcomes"""

    def __init__(self,
                 X,
                 n_splits=2,
                 lookahead=None,
                 train_period_length=None,
                 test_period_length=None,
                 shuffle=False):
        
        self.X_length = len(X)
        self.n_splits = n_splits
        self.lookahead = lookahead

        if (test_period_length == None) and (train_period_length == None):
            self.test_length = int(0.3 * self.X_length//self.n_splits)
            self.train_length = int(0.7 * self.X_length//self.n_splits - 2*self.lookahead)
            # print(f"test_length: {self.test_length}, train_length :{self.train_length}")
            
        else:
            self.test_length = test_period_length
            self.train_length = train_period_length
        self.shuffle = shuffle

    def split(self, X, y=None, groups=None):
        # unique_dates = X["event_time"].unique()
        dates = X["event_time"]
        days = sorted(dates, reverse=True)
        print(len(days))

        train_start_idx = -self.lookahead
        split_idx = []

        for i in range(self.n_splits):
            # print(f"i: {i}, split: {self.n_splits}")
            test_end_idx = train_start_idx + self.lookahead
            test_start_idx = test_end_idx + self.test_length
            train_end_idx = test_start_idx + self.lookahead - 1
            train_start_idx = train_end_idx + self.train_length  - 1
            # print(f"test_end_idx: {test_end_idx}, test_start_idx :{test_start_idx},train_end_idx : {train_end_idx},train_start_idx : {train_start_idx}")
            
            
            split_idx.append([train_start_idx, train_end_idx,
                              test_start_idx, test_end_idx])

        dates = X.reset_index()[['event_time']]

        for train_start, train_end, test_start, test_end in split_idx[::-1]:
            # print("train_start", train_start)
            train_idx = dates[(dates.event_time >= days[train_start])
                              & (dates.event_time <= days[train_end])].index

            # print(f"train_index: {train_idx[0],train_idx[-1]}")
            test_idx = dates[(dates.event_time > days[test_start])
                             & (dates.event_time <= days[test_end])].index
            # print(f"test_index: {test_idx[0], test_idx[-1]}")
            if self.shuffle:
                np.random.shuffle(list(train_idx))
            yield train_idx, test_idx




n_splits = 2
lookahead = 1000

cv = MultipleTimeSeriesCV(n_splits=n_splits,
                          lookahead=lookahead,
                          X = df)
                          


len(data)
i = 0
for train_idx, test_idx in cv.split(X=data):
    train = data.iloc[train_idx]
    train_dates = pd.to_datetime(train['event_time'], unit="ms")
    test = data.iloc[test_idx]
    test_dates = pd.to_datetime(test["event_time"], unit="ms")
    df = pd.concat([train.reset_index(),test.reset_index()])
    n = len(df)
    assert n== len(df.drop_duplicates())
    print(len(train),
          train_dates.min(), train_dates.max(),
          len(test),
          test_dates.min(), test_dates.max())
    i += 1