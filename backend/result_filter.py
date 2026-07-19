class ResultFilter:

    def __init__(self, dataframe):

        self.df = dataframe.copy()

    def by_severity(self, severity):

        if severity is None:

            return self.df

        return self.df[
            self.df["severity"] == severity
        ]

    def anomaly_only(self):

        return self.df[
            self.df["anomaly"] == -1
        ]