import numpy as np
import scipy.stats as stats


class EditablePDF:
    def __init__(self, mean=0, std=1, skew=0, kurtosis=0, x=np.linspace(-5, 5, 1000)):
        self.mean = mean
        self.std = std
        self.skew = skew
        self.kurtosis = kurtosis  # 0 = normal, >0 = peakier, <0 = flatter
        self.x = x

        self.update()

    def update(self):
        skew_factor = min(abs(self.skew) * 0.5, 4)
        kurtosis_factor = max(0, self.kurtosis) * 2

        margin = 4 + skew_factor + kurtosis_factor

        xmin = self.mean - margin * self.std
        xmax = self.mean + margin * self.std

        # Rebuild x-axis based on the updated range
        self.x = np.linspace(xmin, xmax, 40000)
        dist = stats.skewnorm(a=self.skew, loc=self.mean, scale=self.std)
        self.y = dist.pdf(self.x)

        if self.kurtosis != 0:
            if self.kurtosis > 0:
                self.y = np.power(self.y, 1 + self.kurtosis)
            else:
                factor = 1 / (1 - self.kurtosis)
                self.y = np.power(self.y, factor)

        # Normalize
        self.y /= np.trapezoid(self.y, self.x)

    def set_mean(self, val):
        self.mean = val
        self.update()

    def set_std(self, val):
        self.std = val
        self.update()

    def set_skew(self, val):
        self.skew = val
        self.update()

    def set_kurtosis(self, val):
        self.kurtosis = val
        self.update()

    @property
    def plot(self):
        return self.x, self.y,\
            self.mean, self.std, self.skew, self.kurtosis