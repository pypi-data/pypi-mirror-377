from lisatools.sensitivity import SensitivityMatrix
import numpy as np

frequency = np.linspace(1e-3, 1e-2, 1000)

Sn = 1e-40 * (1 + np.random.rand(frequency.shape[0]))

matrix = [[Sn, Sn, Sn], [Sn, Sn, Sn], [Sn, Sn, Sn]]

sens_mat = SensitivityMatrix(frequency, matrix)

