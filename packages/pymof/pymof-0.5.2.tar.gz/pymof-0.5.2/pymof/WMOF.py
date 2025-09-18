import numpy as np
import numba as nb
from numba import jit, objmode, types
from scipy.stats import rankdata
from scipy.spatial.distance import cdist
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
from .MOF import _Var_Massratio
from .MOF import _point_in_radius

# Calculate windowing mass ratio
@jit(nopython=True)
def _Window_Massratio(Data,Window,Overlap_ratio):
  n =Data.shape[0]
  scores = np.zeros(n)

  assert(Window > 0 )
  assert(0.0 <= Overlap_ratio <= 0.5)

  overlap_size = int(Overlap_ratio * Window)
  mid_overlap_point = int(Window - overlap_size/2)
  score_count = 0

  # Windowing data and send to MOF
  for start_point in range(0, n , Window - overlap_size):
    stop_point = min(n, start_point + Window)
    w = stop_point - start_point
    current_data = Data[start_point : stop_point]
    # Last data window size (w) <= Window
    current_scores = _Var_Massratio(current_data,w)

    # Assign score to data points
    stop_score_count = min(n, start_point + mid_overlap_point)
    for i in range(score_count, stop_score_count):
      scores[i] = current_scores[i - start_point]
      score_count += 1

  return scores

class WMOF:

# Windowing mass-ratio-variance based outlier factor (WMOF)
# This algorithm is an extension of the mass-ratio-variance outlier factor algorithm (MOF).
# WMOF operates on overlapping windows of fixed size, specified by the user.
# The use of overlapping windows ensures that anomalies occurring at window boundaries are not missed.
# For each window, the MOF score is computed for all data points within the window.

# Parameters-free
# ----------
  def __init__(self):
    self.name='WMOF'
    self.Data = []
    self.decision_scores_ = np.array([], dtype = np.int32)
    self.Anomaly = np.array([])

  def fit(self,Data,Window=100, Overlap_ratio = 0.2):

    '''
    Parameters
    ----------
    Data : numpy array of shape (n_samples, n_features)
        The input samples.
    Window : integer (int)
        number of points for each calculation
        default window size is 100.
    Overlap_ratio : float
        0.0 <= Overlap_ratio <= 0.5
        A Overlap_ratio between window frame.
        default ratio is 0.2
    '''
    '''
    Returns
    -------
    self : object
    '''

  #  Fitted estimator.
    self.Data = Data

  # Calculate mass ratio variance (MOF)
    self.decision_scores_= _Window_Massratio(Data,Window,Overlap_ratio)

  def detectAnomaly(self, theshold):
    '''
    Parameters
    ----------
    theshold : float
        A theshold value for detect anomaly points
    '''
    '''
    Returns
    -------
    idx : numpy array of shape (n_samples,)
        An index array of anomaly points in data
    '''
    # Check data avaliablity
    assert(len(self.Data) != 0)

    if self.decision_scores_.shape[0] == 0:
      self.fit(self.Data)
    idx = np.squeeze(np.argwhere(self.decision_scores_ > theshold))
    self.Anomaly = np.append(self.Anomaly,idx).astype(np.int32)
    self.Anomaly = np.unique(self.Anomaly)

    return idx
  
  def visualize(self):
    '''
    Parameters free
    Visualize data points
    '''
    '''
    Parameters
    ----------
    '''
    '''
    Returns
    -------
    '''
    if self.Data.shape[1] == 3:
      fig = plt.figure(figsize=(15, 15))
      ax = fig.add_subplot(111, projection='3d')
      p = ax.scatter(self.Data[:, 0], self.Data[:, 1], self.Data[:, 2], c = np.log(self.decision_scores_+0.00001), cmap='jet')
      fig.colorbar(p)
    elif self.Data.shape[1] == 2:
      fig = plt.figure(figsize=(15, 15))
      ax = fig.add_subplot()
      p = ax.scatter(self.Data[:, 0], self.Data[:, 1], c = np.log(self.decision_scores_+0.00001), cmap='jet')
      fig.colorbar(p)
    else :
      print("Cannot visualize dimension space more than 3")
    return self.decision_scores_