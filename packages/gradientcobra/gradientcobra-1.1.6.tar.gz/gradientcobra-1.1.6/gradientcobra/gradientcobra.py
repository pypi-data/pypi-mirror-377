# --------------- Version 1.1.0 -------------------
# =================================================

# Import all the libraries 
# ========================
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, AdaBoostRegressor, ExtraTreesRegressor
from sklearn.linear_model import RidgeCV, LassoCV, BayesianRidge, SGDRegressor, LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.svm import SVR
from sklearn.utils import shuffle
from sklearn.utils.validation import check_X_y, check_array
from scipy import spatial
from sklearn.metrics import mean_squared_error, mean_absolute_error, mean_absolute_percentage_error
# Plotting figures
import matplotlib.pyplot as plt
from matplotlib import cm
from scipy.stats import gaussian_kde as kde
# Table type
import numpy as np
import pandas as pd
# import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from sklearn.base import BaseEstimator
from tqdm import tqdm, trange

class GradientCOBRA(BaseEstimator):
    def __init__(self,
                random_state = None, 
                learning_rate = 0.1,
                bandwidth_list = None,
                speed = 'constant',
                estimator_list = None, 
                estimator_params = None, 
                opt_method = "grad",
                max_iter = int(300),
                opt_params = None,
                kernel = 'radial', 
                kernel_exponent = 1.0,
                show_progress = True,
                loss_function = None,
                loss_weight = None,
                norm_constant = None):
        """
        This is a class of the implementation of the Kernel-based consensual aggregation method for regression by Has (2023).


        * Parameters:
        ------------
            - `random_state`: (default is `None`) set the random state of the random generators in the class.
            
            - `learning_rate`: (default is `0.1`) the learning rate in gradient descent algorithm for estimating the optimal bandwidth.
            
            - 'bandwidth_list'  : a list of bandwidth parameters for grid search algorithm (`default = np.linspace(0.00001, 10, 300)`).
            
            - `speed`: (default is `constant`) the adjusting speed of the learning rate. It is helpful when the cost function is flat around the optimal value, changing the learning speed might help the algorithm to converge faster.
                It should be an element of ['constant', 'linear', 'log', 'sqrt_root', 'quad', 'exp'].
            
            - `estimator_list`: (default is None) the list of intial estimators (machines as addressed in Biau et al. (2016)). 
                If it is None, intial learners including 'linear_regression', 'ridge', 'lasso', 'knn', 'random_forest' and 'svm' are used with default parameters.
                It should be a sublist of the following list: ['linear_regression', 'knn', 'ridge', 'lasso', 'tree', 'random_forest', 'svm', 'sgd', 'bayesian_ridge', 'adaboost', 'gradient_boost'].

            - `estimator_params`: (default is `None`) a dictionary containing the parameters of the basic estimators given in the `estimator_list` argument. 
                It must be a dictionary with:
                - `key`     : the name of the basic estimator defined in `estimator_list`, 
                - `value`   : a dictionary with (key, value) = (parameter, value).

            - `opt_method`: (default is "grad") optimization algorithm for estimating the bandwidth parameter. 
                It should be either "grid" (grid search) or "grad" (gradient descent for non-compactly supported kernel). 
                By default, it is set to be "grad" with default "radial" kernel.
                
            - `max_iter`: maximum iteration of gradient descent algorithm (default = 100).
            
            - opt_params: (default is 'None') a dictionary of additional parameters for the optimization algorithm (both grid search and gradient descent). 
                Its should contain some of the following keys:
                - 'epsilon'         : stopping criterion for gradient descent algorithm (default = 10 ** (-2))
                - 'n_tries'         : the number of tries for selecting initial position of gradient descent algorithm (default = 5)
                - 'start'           : the initial value of the bandwidth parameter (default = None)
                - 'n_cv'            : number of cross-validation folds (default = int(5))
                - 'precision'       : the precision to estimate the gradient for gradient descent algorithm (default = 2 * 10 ** (-5)).
            
             - `kernel`: (default is `'radial'`) the kernel function used for the aggregation. It should be an element of the list ['exponential', 'gaussian', 'radial', 'cauchy', 'reverse_cosh', 'epanechnikov', 'biweight', 'triweight', 'triangular', 'cobra', 'naive'].
                Some options such as 'gaussian' and 'radial' lead to the same radial kernel function. 
                For 'cobra' or 'naive', they correspond to Biau et al. (2016).

            - `kernel_exponent`: (default is 1.0) exponential `alpha` of the exponential and radial kernel function i.e., K(x) = exp(|x|^{\alpha}}). By default, alpha = 2.0,

            - show_progress: (default is `True`) boolean defining whether or not to show the progress of the optimization algorithm for both grid search and gradient descent.

            - `loss_function`: (default is None) a function or string defining the cost function to be optimized for estimating the optimal bandwidth parameter.
                By defalut, the K-Fold cross-validation MSE is used. Otherwise, it must be either:
                - a function of two argumetns (y_true, y_pred) or
                - a string element of the list ['mse', 'mae', 'mape', 'weighted_mse']. If it is `weighted_mse`, one can define the weight for each training point using `loss_weight` argument below.
            
            - `loss_weight`: (default is None) a list of size equals to the size of the training data defining the weight for each individual data point in the loss function. 
                If it is None and the `loss_function = weighted_mse`, then a normalized weight W(i) = 1/PDF(i) is assigned to individual i of the training data.
            
            - `norm_constant`: (default is None) a normalized constant used to scale the features in optimization algorithm.
        
        * Returns:
        ---------
            self : returns an instance of self. 

        * Methods: 
        ---------
            - fit : fitting the aggregation method on the design features (original data or predicted features).
            - split_data : split the data into D_k = {(X_k,y_k)} and D_l = {(X_l,y_l)} to construct the estimators and perform aggregation respectively.
            - build_basic_estimators : build basic estimators for the aggregation. It is also possible to set the values of (hyper) parameters for each estimators.
            - load_predictions : to make predictions using constructed basic estimators.
            - distances : construct distance matrix according to the kernel function used in the aggregation.
            - kappa_cross_validation_error : the objective function to be minimized.
            - optimize_bandwidth : the optimization method to estimate the optimal bendwidth parameter.
            - predict : for building prediction on the new observations using any given bendwidth or the estimated one.
            - draw_learning_curve : for plotting the graphic of learning algorithm (error vs parameter).
        """
        self.random_state = random_state
        self.learning_rate = learning_rate
        self.bandwidth_list = bandwidth_list
        self.speed = speed
        self.kernel = kernel
        self.estimator_list = estimator_list
        self.show_progress = show_progress
        self.estimator_params = estimator_params
        self.opt_method = opt_method
        self.max_iter = max_iter
        self.opt_params = opt_params
        self.kernel_exponent = kernel_exponent
        self.loss_weight = loss_weight
        self.loss_function = loss_function
        self.norm_constant = norm_constant

    # List of kernel functions
    def reverse_cosh(self, x, y):
        return 1/np.cosh(x*y) ** self.kernel_exponent
        
    def exponential(self, x, y):
        return np.exp(-y*x ** self.kernel_exponent)

    def radial(self, x, y):
        return np.exp(-x*y)
        
    def epanechnikov(self, x, y):
        return (1 - x*y) * (x*y < 1)
        
    def biweight(self, x, y):
        return (1-x*y) ** 2 * (x*y < 1)
        
    def triweight(self, x, y):
        return (1-x*y) ** 3 * (x*y < 1)
        
    def triangular(self, x, y):
        return (1-np.abs(x*y)) * (x*y < 1)
        
    def naive(self, x, y):
        return np.array(x*y)
        
    def cauchy(self, x, y):
        return 1/(1 + np.array(x*y))
    
    # List of loss functions
    def mse(self, y_true, pred, id = None):
        return mean_squared_error(y_true, pred)
    def mae(self, y_true, pred, id = None):
        return mean_absolute_error(y_true, pred)
    def mape(self, y_true, pred, id = None):
        return mean_absolute_percentage_error(y_true, pred)
    def wgt_mse(self, y_true, pred, id = None):
        w_err2 = np.dot(self.loss_weight_[id], (y_true - pred) ** 2)/(np.dot(self.loss_weight_[id], y_true) ** 2)
        return w_err2
    def loss_func(self, y_true, pred, id = None):
        return self.loss_function(y_true, pred)

    def fit(self, 
            X, y, 
            X_l = None, y_l = None, 
            split = .5, overlap = 0, 
            as_predictions = False):
        '''
        This method builds basic estimators and performs optimization algorithm to estimate the bandwidth parameter for the aggregation.
        
        * Parameters:
        -------------
            - `X, y`            : the training input and out put. If the argument `as_predictions = True`, then these two inputs should be the pretrained predicted features and its corresponding target, and the optimization algorithm is performed directly on it.
            - `X_l, y_l`        : optional aggregation part of the training data (`(X_l, y_l)` in the paper). By default, they are `None`, if given, the argument `(X, y)` will be treated as `(X_k, y_k)` for building basic estimators, and the given (X_l, y_l) will be used for aggregation.
                                  If (X_l, y_l) is not `None`, then the argument `as_predictions` is automatically set to be `False` because both parts of the training data are provided.
            - `split`           : The proportion of `(X_k, y_k)` for training basic estimators. By default, it is equal to 0.5.
            - `overlap`         : The proportion of overlapping data between `(X_k, y_k)` and `(X_l, y_l)`. It is 0 by default.
            - `as_predictions`   : a boolean type controlling whether `X` should be treated as input data or pretrained predicted features. Be default, it is `False`.
        '''
        X, y = check_X_y(X, y)
        if X.dtype == object:
            X = X.astype(np.float64)
        if y.dtype == object:
            y = y.astype(np.float64)
        self.X_ = X
        self.y_ = y
        if self.estimator_list is None:
            M = 6
        else:
            M = len(self.estimator_list)
        if self.norm_constant is None:
            self.normalize_constant = 30 / (np.max(np.abs(y)) * M)
        else:
             self.normalize_constant = self.norm_constant / (np.max(np.abs(y))* M)
        self.as_predictions_ = as_predictions
        self.shuffle_input_ = True
        if (X_l is not None) and (y_l is not None):
            X_l, y_l = check_X_y(X_l, y_l)
            self.X_k_, self.X_l_ = X, X_l
            self.y_k_, self.y_l_ = y, y_l
            self.shuffle_input_ = False
            self.as_predictions_ = False
            self.iloc_l = np.array(range(len(self.y_l_)), dtype = np.int64)
        
        self.basic_estimtors = {}
        opt_param = {'epsilon' : 1e-2,
                     'n_tries' : int(5),
                     'start' : None,
                     'n_cv' : int(5),
                     'precision' : 10 ** (-7)
        }

        if self.bandwidth_list is None:
            self.bandwidth_list_ = np.linspace(0.00001, 10, 300)
        else:
            self.bandwidth_list_ = self.bandwidth_list
        
        # Set optional parameters
        if self.opt_params is not None:
            for obj in self.opt_params:
                opt_param[obj] = self.opt_params[obj]
        self.opt_params_ = opt_param
    
        self.opt_method_ = self.opt_method
        if self.kernel not in ['radial', 'gaussian', 'exponential', 'reverse_cosh']:
            self.opt_method_ = 'grid'

        self.list_kernels = {
            'reverse_cosh' : self.reverse_cosh,
            'inverse_cosh' : self.reverse_cosh,
            'exponential' : self.exponential,
            'gaussian' : self.radial,
            'radial' : self.radial,
            'epanechnikov' : self.epanechnikov,
            'biweight' : self.biweight,
            'triweight' : self.triweight,
            'triangular' : self.triangular,
            'cobra' : self.naive,
            'naive' : self.naive,
            'cauchy' : self.cauchy
        }

        # Loss function
        if (self.loss_function is None) or (self.loss_function == 'mse') or (self.loss_function == 'mean_squared_error'):
            self.loss = self.mse
        elif (self.loss_function == 'mae') or (self.loss_function == 'mean_absolute_error'):
            self.loss = self.mae
        elif (self.loss_function == "mape") or (self.loss_function == 'mean_absolute_percentage_error'):
            self.loss = self.mape
        elif (self.loss_function == 'weighted_mse') or (self.loss_function == 'weighted_mean_squared_error'):
            if self.loss_weight is None:
                pdf = kde(self.y_)(self.y_)
                wgt = 1/pdf
                wgt /= np.sum(wgt)
                self.loss_weight_ = wgt
            else:
                self.loss_weight_ = self.loss_weight
            self.loss = self.wgt_mse

        if callable(self.loss_function):
            self.loss = self.loss_func
        
        if not self.as_predictions_:
            self.split_data(split = split, 
                            overlap=overlap, 
                            shuffle_data=self.shuffle_input_)
            self.build_baisc_estimators()
            self.load_predictions()
            self.optimize_bandwidth(params = self.opt_params_)
        else:
            self.pred_X_l = X * self.normalize_constant
            self.y_l_ = y
            self.number_estimators = X.shape[1]
            self.iloc_l = np.array(range(len(y)))
            self.optimize_bandwidth(params = self.opt_params_)
        return self
    
    def split_data(self, 
                   split, 
                   overlap = 0, 
                   shuffle_data = True):
        if shuffle_data:
            self.shuffled_index = shuffle(range(len(self.y_)), random_state=self.random_state)
            k1 = int(len(self.y_) * (split-overlap/2))
            k2 = int(len(self.y_) * (split+overlap/2))
            self.iloc_k = np.array(self.shuffled_index[:k2], dtype = np.int64)
            self.iloc_l = np.array(self.shuffled_index[k1:], dtype = np.int64)
            self.X_k_, self.X_l_ = self.X_[self.iloc_k,:], self.X_[self.iloc_l,:]
            self.y_k_, self.y_l_ = self.y_[self.iloc_k], self.y_[self.iloc_l]

    def build_baisc_estimators(self):
        all_estimators = {
            'linear_regression' : LinearRegression(),
            'extra_trees' : ExtraTreesRegressor(random_state=self.random_state),
            'knn' : KNeighborsRegressor(),
            'lasso' : LassoCV(random_state=self.random_state),
            'ridge' : RidgeCV(),
            'tree' : DecisionTreeRegressor(random_state=self.random_state),
            'random_forest' : RandomForestRegressor(random_state=self.random_state),
            'svm' : SVR(),
            'bayesian_ridge' : BayesianRidge(),
            'sgd' : SGDRegressor(random_state=self.random_state),
            'adaboost' : AdaBoostRegressor(random_state=self.random_state),
            'gradient_boost' : GradientBoostingRegressor(random_state=self.random_state)
        }
        estimator_dict = {}
        if self.estimator_list == "all":
            estimator_dict = all_estimators
        elif self.estimator_list is None:
            estimator_dict = {'linear_regression' : LinearRegression(),
                              'lasso' : LassoCV(random_state=self.random_state),
                              'ridge' : RidgeCV(),
                              'knn' : KNeighborsRegressor(),
                              'random_forest' : RandomForestRegressor(random_state=self.random_state),
                              'svm' : SVR()}
        else:
            for name in self.estimator_list:
                estimator_dict[name] = all_estimators[name]
        self.estimator_names = list(estimator_dict.keys())
        param_dict = {
            'linear_regression' : None,
            'knn' : None,
            'lasso' : None,
            'ridge' : None,
            'tree' : None,
            'random_forest' : None,
            'svm' : None,
            'bayesian_ridge' : None,
            'sgd' : None,
            'adaboost' : None,
            'gradient_boost' : None,
            'extra_trees' : None
        }
        self.basic_estimators = {}
        if self.estimator_params is not None:
            for name in list(self.estimator_params):
                param_dict[name] = self.estimator_params[name]
        for machine in self.estimator_names:
            try:
                mod = estimator_dict[machine]
                if param_dict[machine] is not None:
                    if machine == 'adaboost':
                        mod.estimator = DecisionTreeRegressor(random_state=self.random_state)
                        param_ = {}
                        for p_ in mod.estimator.get_params():
                            if p_ in list(param_dict[machine].keys()):
                                param_[p_] = param_dict[machine][p_]
                                param_dict[machine].pop(p_)
                        mod.estimator.set_params(**param_)
                        mod.set_params(**param_dict[machine])
                    else:
                        mod.set_params(**param_dict[machine])
            except ValueError:
                continue
            self.basic_estimators[machine] = mod.fit(self.X_k_, self.y_k_)
        return self

    def load_predictions(self):
        self.pred_features = {}
        for machine in self.estimator_names:
            self.pred_features[machine] = self.basic_estimators[machine].predict(self.X_l_) * self.normalize_constant
        self.pred_X_l = np.column_stack([v for v in self.pred_features.values()])
        self.number_estimators = len(self.estimator_names)
        return self

    def distances(self, 
                  x, 
                  pred_test = None, 
                  p = 2):
        if pred_test is None:
            ids = np.array(range(self.opt_params_['n_cv']))
            size_each = x.shape[0] // self.opt_params_['n_cv']
            size_remain = x.shape[0] - size_each * self.opt_params_['n_cv']
            self.shuffled_index_cv = shuffle(
                np.concatenate([np.repeat(ids, size_each), np.random.choice(ids, size_remain)]),
                random_state=self.random_state
            ) 
            if p != 0:
                self.distance_matrix = spatial.distance_matrix(x,x,p) ** 2
            else:
                dis = np.ndarray(shape=(x.shape[0], x.shape[0]))
                for i in range(x.shape[0]):
                    dis[i,:] = [spatial.distance.hamming(x[i,:], x[j,:]) for j in range(x.shape[0])]
                self.distance_matrix = dis
        else:
            if p != 0:
                self.distance_matrix_test = spatial.distance_matrix(x,pred_test,p) ** 2
            else:
                dis = np.ndarray(shape=(x.shape[0], pred_test.shape[0]))
                for i in range(x.shape[0]):
                    dis[i,:] = [spatial.distance.hamming(x[i,:], pred_test[j,:]) for j in range(pred_test.shape[0])]
                self.distance_matrix_test = dis
    
    def kappa_cross_validation_error(self, 
                                     bandwidth = 1):
        list_kernels = self.list_kernels
        if self.kernel in ['cobra', 'naive']:
            cost = np.full((self.opt_params_['n_cv'], 
                            self.number_estimators), 
                            fill_value = np.float32)
            for m in range(1, self.number_estimators+1, 1):
                ratio = 1 - m/self.number_estimators
                for i in range(self.opt_params_['n_cv']):
                    D_k = 1*(list_kernels[self.kernel](self.distance_matrix[self.shuffled_index_cv != i,:][:,self.shuffled_index_cv == i], bandwidth) < ratio)
                    D_k_ = np.sum(D_k, axis=0, dtype=np.float32)
                    D_k_[D_k_ == 0 | np.isnan(D_k_)] = np.inf
                    res = np.matmul(self.y_l_[self.shuffled_index_cv != i], D_k)/D_k_
                    res[np.isnan(res)] = 0
                    cost[i, m-1] = self.loss(self.y_l_[self.shuffled_index_cv == i], res, id = self.iloc_l[self.shuffled_index_cv == i])
            cost_ = cost.mean(axis=0)
        else:
            cost = np.full(self.opt_params_['n_cv'], fill_value = np.float32)
            for i in range(self.opt_params_['n_cv']):
                D_k = list_kernels[self.kernel](self.distance_matrix[self.shuffled_index_cv != i,:][:,self.shuffled_index_cv == i], bandwidth)
                D_k_ = np.sum(D_k, axis=0, dtype=np.float32)
                D_k_[(D_k_ == 0) | np.isnan(D_k_)] = np.inf
                res = np.matmul(self.y_l_[self.shuffled_index_cv != i], D_k)/D_k_
                res[np.isnan(res)] = 0
                temp = self.loss(self.y_l_[self.shuffled_index_cv == i], res, id = self.iloc_l[self.shuffled_index_cv == i])
                if np.isnan(temp):
                    cost[i] = np.inf
                else:
                    cost[i] = temp
            cost_ = cost.mean()
        return cost_
        
    def optimize_bandwidth(self, 
                           params):
        def select_best_index(arr):
            l, c = arr.shape
            if l > 1:
                return arr[l//2,]
            else:
                return arr
            
        def gradient(f, x0, eps = self.opt_params_['precision']):
            return np.array([(f(x0 + eps) - f(x0 - eps))/(2*eps)])
        # def gradient(f, x0, eps = self.opt_params_['precision']):
        #     return np.array([(f(x0 + eps) - f(x0))/eps])

        kernel_to_dist = {'naive' : 'naive',
                          'cobra' : 'naive',
                          '0-1' : 'naive',
                          'reverse_cosh' : 'l2',
                          'uniform' : 'naive',
                          'exponential' : 'l2',
                          'gaussian' : 'l2',
                          'normal' : 'l2',
                          'radial' : 'l2',
                          'epanechnikov' : 'l2',
                          'biweight' : 'l2',
                          'triweight' : 'l2',
                          'triangular' : 'l1',
                          'triang' : 'l1',
                          'cauchy' : 'l2'}
        self.distance_matrix = {}
        self.index_each_fold = {}
        self.distance = kernel_to_dist[self.kernel]
        if self.distance in ['l2', None]:
            self.p_ = 2
        elif self.distance in ['l1']:
            self.p_ = 1
        else:
            self.p_ = 0
        self.distances(self.pred_X_l, p = self.p_)
        if self.opt_method_ in ['grid', 'grid_search', 'grid search']:
            n_iter = len(self.bandwidth_list_)
            if self.kernel in ['cobra', 'naive']:
                errors = np.full((n_iter, self.number_estimators), np.float32)
                if self.show_progress:
                    for iter in tqdm(range(n_iter), f"* Grid search progress"):
                        errors[iter,:] = self.kappa_cross_validation_error(bandwidth=self.bandwidth_list_[iter])
                else:
                    for iter in range(n_iter):
                        errors[iter,:] = self.kappa_cross_validation_error(bandwidth=self.bandwidth_list_[iter])
                opt_risk = np.min(np.min(errors))
                opt_id = np.array(np.where(errors == opt_risk))
                self.optimization_outputs = {
                    'number_retained_estimators' : opt_id[1][len(opt_id[1])//2] + 1,
                    'opt_method' : 'grid',
                    'opt_bandwidth' : self.bandwidth_list_[opt_id[0][len(opt_id[1])//2]],
                    'opt_index': opt_id[0][len(opt_id[1])//2],
                    'kappa_cv_errors': errors
                }
            else:
                errors = np.full(n_iter, np.float32)
                if self.show_progress:
                    for iter in tqdm(range(n_iter), f"* Grid search progress"):
                        errors[iter] = self.kappa_cross_validation_error(bandwidth=self.bandwidth_list_[iter])
                else:
                    for iter in range(n_iter):
                        errors[iter] = self.kappa_cross_validation_error(bandwidth=self.bandwidth_list_[iter])
                opt_risk = np.min(np.min(errors))
                opt_id = select_best_index(np.array(np.where(errors == opt_risk)).reshape((-1,1)))
                self.optimization_outputs = {
                    'opt_method' : 'grid',
                    'opt_bandwidth' : self.bandwidth_list_[opt_id[0]],
                    'opt_index': opt_id[0],
                    'kappa_cv_errors': errors
                }
        if self.opt_method_ in ['grad', 'gradient descent', 'gd', 'GD']:
            n_iter = len(self.bandwidth_list_)
            errors = np.full(n_iter, float)
            collect_bw = []
            gradients = []
            speed_list = {
                'constant' : lambda x, y: y,
                'linear' : lambda x, y: x*y,
                'log' : lambda x, y: np.log(1+x) * y,
                'sqrt_root' : lambda x, y: np.sqrt(1+x) * y,
                'quad' : lambda x, y: (1+x ** 2) * y,
                'exp' : lambda x, y: np.exp(x) * y
            }
            if self.opt_params_['start'] is None:
                bws = np.linspace(0.0001, 3, num = self.opt_params_['n_tries'])
                initial_tries = [self.kappa_cross_validation_error(bandwidth=b) for b in bws]
                bw0 = bws[np.argmin(initial_tries)]
            else:
                bw0 = self.opt_params_['start']
            grad = gradient(self.kappa_cross_validation_error, bw0, self.opt_params_['precision'])
            grad0 = grad
            test_threshold = np.inf
            if self.show_progress:
                r0 = self.learning_rate / abs(grad)        # make the first step exactly equal to `learning-rate`.
                rate = speed_list[self.speed]              # the learning rate can be varied, and speed defines this change in learning rate.
                test_threshold = 1.0
                count = 1
                pbar = trange(self.max_iter, desc=f"* GD progress: iter: {count} / bw: {np.round(bw0,3)} / grad: {np.round(grad[0],3)} / stop criter: {np.round(test_threshold,3)} ", leave=True)
                for count in pbar:
                    bw = bw0 - rate(count, r0) * grad
                    if bw < 0 or np.isnan(bw):
                        bw = bw0 * 0.95
                    if count > 3:
                        if np.sign(grad)*np.sign(grad0) < 0:
                            r0 = r0 * 0.99
                        if test_threshold > self.opt_params_['epsilon']:
                            bw0, grad0 = bw, grad
                        else:
                            break
                    # relative = abs((bw - bw0) / bw0)
                    test_threshold = np.abs(grad) #np.mean([relative, abs(grad)])
                    grad = gradient(self.kappa_cross_validation_error, bw0, self.opt_params_['precision'])
                    count += 1
                    collect_bw.append(bw[0])
                    gradients.append(grad[0])
                    pbar.set_description(f"* GD progress: iter: {count} / bw: {np.round(bw[0],3)} / grad: {np.round(grad[0],3)} / stop criter: {np.round(test_threshold,3)} ")
                    pbar.refresh()
            else:
                r0 = self.learning_rate / abs(grad)
                rate = speed_list[self.speed]
                count = 0
                grad0 = grad
                while count < self.max_iter:
                    bw = bw0 - rate(count, r0) * grad
                    if bw < 0 or np.isnan(bw):
                        bw = bw0 * 0.95
                    if count > 3:
                        if np.sign(grad)*np.sign(grad0) < 0:
                            r0 = r0 * 0.99
                        if test_threshold > self.opt_params_['epsilon']:
                            bw0, grad0 = bw, grad
                        else:
                            break
                    # relative = abs((bw - bw0) / bw0)
                    test_threshold = np.abs(grad) #np.mean([relative, abs(grad)])
                    grad = gradient(self.kappa_cross_validation_error, bw0, self.opt_params_['precision'])
                    count += 1
                    collect_bw.append(bw[0])
                    gradients.append(grad[0])
            opt_bw = bw[0]
            opt_risk = self.kappa_cross_validation_error(opt_bw)
            self.optimization_outputs = {
                'opt_method' : 'grad',
                'opt_bandwidth' : opt_bw,
                'bandwidth_collection' : collect_bw,
                'gradients': gradients
            }
        return self

    def predict(self, X, bandwidth = None):
        X = check_array(X)
        if bandwidth is None:
            bandwidth = self.optimization_outputs['opt_bandwidth']
        if self.as_predictions_:
             self.pred_features_x_test = X * self.normalize_constant
        else:
            self.pred_features_test = {}
            for machine in self.estimator_names:
                self.pred_features_test[machine] = self.basic_estimators[machine].predict(X) * self.normalize_constant
            self.pred_features_x_test = np.column_stack([v for v in self.pred_features_test.values()])
        self.distances(x = self.pred_X_l, pred_test = self.pred_features_x_test, p = self.p_)
        if self.kernel in ['cobra', 'naive']:
            D_k = (self.list_kernels[self.kernel](np.float32(self.distance_matrix_test), bandwidth) < 1 - (self.optimization_outputs['number_retained_estimators'])/self.number_estimators)    
        else:
            D_k = self.list_kernels[self.kernel](self.distance_matrix_test, bandwidth)
        D_k_ = np.sum(D_k, axis=0, dtype=np.float32)
        D_k_[D_k_ == 0] = np.inf
        res = np.matmul(self.y_l_, D_k)/D_k_
        res[res == 0] = res[res != 0].mean()
        self.test_prediction = res
        return res
        
    def draw_learning_curve(self, 
                            y_test = None,  
                            fig_type = 'qq', 
                            save_fig = False, 
                            fig_path = None, 
                            dpi = None, 
                            show_fig = True,
                            engine = 'plotly'):
        if (y_test is not None) and (fig_type in ['qq', 'qq-plot', 'qqplot', 'QQ-plot', 'QQplot']):
            if engine == 'plotly':
                df = pd.DataFrame({
                'y_test' : y_test,
                'y_pred' : self.test_prediction})
                fig = go.Figure(data = px.line(df, 
                                               x = "y_test", 
                                               y = "y_test", 
                                               color_discrete_sequence=['red']).data + px.scatter(df, x = "y_pred", 
                                                                                                  y = "y_test").data)
                fig = fig.update_layout(width = 700, 
                                        height = 650, 
                                        title_text = "QQplot of predicted and actual target", 
                                        title_x = .5, 
                                        title_y = 0.925)
                fig.update_xaxes(title_text = "Prediction")
                fig.update_yaxes(title_text = "Actual target")
                if show_fig:
                    fig.show()
                if save_fig:
                    if fig_path is None:
                        fig.write_image("qqplot_aggregation.png")
                    else:
                        fig.write_image(fig_path)
            else:
                fig = plt.figure(figsize=(7, 3))
                plt.plot(y_test, y_test, 'r')
                plt.scatter(y_test, self.test_prediction)
                plt.xlabel('y_test')
                plt.ylabel('prediction')
                plt.title('QQ-plot: actual Vs prediction')
                plt.legend()
                if save_fig:
                    if fig_path is None:
                        plt.savefig("qqplot_aggregation.png", format = 'png', dpi=dpi, bbox_inches='tight')
                    else:
                        plt.savefig(fig_path, format = 'png', dpi=dpi, bbox_inches='tight')
                if show_fig:
                    plt.show()
        else:
            if self.optimization_outputs['opt_method'] == 'grid':
                if self.kernel in ['naive', 'cobra']:
                    if engine == 'plotly':
                        num_estimators, bandwidths = np.meshgrid(list(range(1, self.number_estimators+1,1)), self.bandwidth_list_)
                        err = self.optimization_outputs['kappa_cv_errors']
                        num_opt = self.optimization_outputs['number_retained_estimators']
                        band_opt = self.optimization_outputs['opt_bandwidth']
                        err_opt = self.optimization_outputs['kappa_cv_errors'][self.optimization_outputs['opt_index'], num_opt-1]
                        df_opt = pd.DataFrame({
                            'bandwidth' : [band_opt],
                            'num_estimator' : [num_opt],
                            "error" : [err_opt]})
                        p1 = px.scatter_3d(df_opt, 
                                           x = "bandwidth", 
                                           y = "num_estimator", 
                                           z = "error",  
                                           color_discrete_sequence=["red"]).data
                        fig = go.Figure(data= [go.Surface(z = err,
                                                         x = bandwidths,
                                                         y = num_estimators,
                                                         name="Loss",
                                                         showlegend = False), 
                                                         p1[0]])
                        fig.update_layout(scene = dict(
                                            xaxis_title='Bandwidth',
                                            yaxis_title='Number of retained estimator',
                                            zaxis_title='Error'),
                                          title_text = "Errors vs parameters with "+ str(self.kernel) + " kernel", 
                                          title_x = .5, 
                                          title_y = 0.925,
                                          width = 700,
                                          height = 650)
                        if show_fig:
                            fig.show()
                        if save_fig:
                            if fig_path is None:
                                fig.write_image("learning_curve.png")
                            else:
                                fig.write_image(fig_path)
                    else:
                        num_estimators, bandwidths = np.meshgrid(list(range(1,self.number_estimators+1,1)), self.bandwidth_list_)
                        err = self.optimization_outputs['kappa_cv_errors']
                        num_opt = self.optimization_outputs['number_retained_estimators']
                        band_opt = self.optimization_outputs['opt_bandwidth']
                        fig = plt.figure(figsize=(10,6))
                        axs = fig.add_subplot(projection='3d')
                        surf = axs.plot_surface(bandwidths, num_estimators, err, cmap=cm.coolwarm, linewidth=0, antialiased=False)
                        axs.plot(band_opt, num_opt, self.optimization_outputs['kappa_cv_errors'][self.optimization_outputs['opt_index'], num_opt-1], 'o')
                        axs.set_title("Errors Vs bandwidths and number of estimators with "+ str(self.kernel)+ " kernel")
                        axs.set_xlabel("bandwidth")
                        axs.set_ylabel("number of estimators")
                        axs.set_zlabel("Kappa cross-validation error")
                        axs.view_init(30, 60)
                        if show_fig:
                            plt.show()
                        if save_fig:
                            if fig_path is None:
                                plt.savefig("learning_curve.png", format = 'png', dpi=dpi, bbox_inches='tight')
                            else:
                                plt.savefig(fig_path, format = 'png', dpi=dpi, bbox_inches='tight')
                else:
                    if engine == 'plotly':
                        df_opt = pd.DataFrame({
                            'bandwidth' : self.optimization_outputs['opt_bandwidth'],
                            'error' : self.optimization_outputs['kappa_cv_errors'][self.optimization_outputs['opt_index']]})
                        df_dash = pd.DataFrame({
                            'bandwidth' : [df_opt.bandwidth[0], 
                                           df_opt.bandwidth[0],
                                           0],
                            'error' : [0,
                                       df_opt.error[0],
                                       df_opt.error[0]]})
                        fig = go.Figure([go.Scatter(x = self.bandwidth_list_, 
                                                    y = self.optimization_outputs['kappa_cv_errors'],
                                                    mode = "lines",
                                                    name = "Loss",
                                                    showlegend=False),
                                        go.Scatter(x = df_opt.bandwidth,
                                                   y = df_opt.error,
                                                   showlegend=False,
                                                   mode = "markers",
                                                   name = "Optimal point",
                                                   marker = dict(color = "red", size = 8)),
                                        go.Scatter(x = df_dash.bandwidth, 
                                                   y = df_dash.error, 
                                                   mode = "lines",
                                                   line = dict(color = "red", 
                                                               dash = 'dash'),
                                                   showlegend=False)])
                        fig = fig.update_layout(width = 700, 
                                                height = 650, 
                                                title_text = "Errors vs bandwidths (grid search)", 
                                                title_x = .5, 
                                                title_y = 0.925)
                        fig.update_xaxes(title_text = "Bandwidth")
                        fig.update_yaxes(title_text = "Error")
                        if show_fig:
                            fig.show()
                        if save_fig:
                            if fig_path is None:
                                fig.write_image("learning_curve.png")
                            else:
                                fig.write_image(fig_path)
                    else:
                        plt.figure(figsize=(7, 3))
                        plt.plot(self.bandwidth_list_, self.optimization_outputs['kappa_cv_errors'])
                        plt.title('Errors Vs bandwidths (grid search)')
                        plt.xlabel('bandwidth')
                        plt.ylabel('error')
                        plt.scatter(self.optimization_outputs['opt_bandwidth'], self.optimization_outputs['kappa_cv_errors'][self.optimization_outputs['opt_index']], c = 'r')
                        plt.vlines(x=self.optimization_outputs['opt_bandwidth'], ymin=self.optimization_outputs['kappa_cv_errors'][self.optimization_outputs['opt_index']]/5, ymax=self.optimization_outputs['kappa_cv_errors'][self.optimization_outputs['opt_index']], colors='r', linestyles='--')
                        plt.hlines(y=self.optimization_outputs['kappa_cv_errors'][self.optimization_outputs['opt_index']], xmin=0, xmax=self.optimization_outputs['opt_bandwidth'], colors='r', linestyles='--')
                        if show_fig:
                            plt.show()
                        if save_fig:
                            if fig_path is None:
                                plt.savefig("learning_curve.png", format = 'png', dpi=dpi, bbox_inches='tight')
                            else:
                                plt.savefig(fig_path, format = 'png', dpi=dpi, bbox_inches='tight')
            else:
                if engine == 'plotly':
                    df1 = pd.DataFrame({
                            'iteration' : list(range(len(self.optimization_outputs['bandwidth_collection']))),
                            'parameter' : self.optimization_outputs['bandwidth_collection']})
                    L = {'bandwidth' : np.linspace(self.optimization_outputs['opt_bandwidth']/5, 
                                                       self.optimization_outputs['opt_bandwidth']*5, 20)}
                    L['error'] =  np.array([self.kappa_cross_validation_error(b) for b in L['bandwidth']])
                    df2 = pd.DataFrame(L)
                    df_opt = pd.DataFrame({
                            'error' : [self.kappa_cross_validation_error(self.optimization_outputs['opt_bandwidth'])],
                            'bandwidth' : [self.optimization_outputs['opt_bandwidth']]})
                    df_dash = pd.DataFrame({
                            'bandwidth' : [0, self.optimization_outputs['opt_bandwidth'], self.optimization_outputs['opt_bandwidth']],
                            'error' : [df_opt['error'][0], df_opt['error'][0], 0]})
                        
                    f1 = go.Figure([go.Scatter(x = df1.iteration,
                                               y = df1.parameter,
                                               mode = 'lines',
                                               name = "Loss",
                                               showlegend=False),
                                    go.Scatter(x = [0, df1.iteration.values[-1]],
                                               y = [self.optimization_outputs['bandwidth_collection'][-1], 
                                                    self.optimization_outputs['bandwidth_collection'][-1]],
                                               showlegend=False,
                                               mode = 'lines',
                                               name = "Optimal point",
                                               line=dict(color = "red", dash = 'dash'))])
                    f2 = go.Figure([go.Scatter(x = df2.bandwidth, 
                                               y = df2.error,
                                               mode = "lines",
                                               showlegend=False,
                                               name = "Loss",
                                               line = dict(color = 'blue')),
                                    go.Scatter(x = df_opt.bandwidth,
                                               y = df_opt.error,
                                               showlegend=False, 
                                               mode = "markers",
                                               name = "Optimal point",
                                               marker = dict(color = "red", size = 8)),
                                    go.Scatter(x = df_dash.bandwidth, 
                                               y = df_dash.error, 
                                               mode = "lines", 
                                               line = dict(color = "red", dash = 'dash'),
                                               showlegend=False)])
                    fig = make_subplots(rows=1, 
                                        cols=2, 
                                        print_grid=False, 
                                        subplot_titles=("Bandwidth at each gradient descent step", "Error vs bandwidth"))
                    fig.update_xaxes(title_text="Iteration", row=1, col=1)
                    fig.update_yaxes(title_text="Bandwidth", row=1, col=1)
                    fig.update_xaxes(title_text="Bandwidth", row=1, col=2)
                    fig.update_yaxes(title_text="Error", row=1, col=2)
                    fig.update_layout(width = 1000, height = 500)
                    for trace in f1.data:
                        fig.add_trace(trace, row=1, col=1)
                    for trace in f2.data:
                        fig.add_trace(trace, row=1, col=2)
                    if show_fig:
                        fig.show()   
                    if save_fig:
                        if fig_path is None:
                            fig.write_image("learning_curve.png")
                        else:
                            fig.write_image(fig_path) 
                else:
                    fig = plt.figure(figsize=(10, 3))
                    ax1 = fig.add_subplot(1,2,1)
                    ax1.plot(range(len(self.optimization_outputs['bandwidth_collection'])), self.optimization_outputs['bandwidth_collection'])
                    ax1.hlines(y=self.optimization_outputs['bandwidth_collection'][-1], xmin=0, xmax=self.max_iter, colors='r', linestyles='--')
                    ax1.set_title('Bandwidths at each iteration (gradient descent)')
                    ax1.set_xlabel('iteration')
                    ax1.set_ylabel('bandwidth')
                    
                    ax2 = fig.add_subplot(1,2,2)
                    param_range = np.linspace(self.optimization_outputs['opt_bandwidth']/5, self.optimization_outputs['opt_bandwidth']*5, 20)
                    errors = [self.kappa_cross_validation_error(b) for b in param_range]
                    opt_error = self.kappa_cross_validation_error(self.optimization_outputs['opt_bandwidth'])
                    ax2.plot(param_range, errors)
                    ax2.set_title('Errors Vs bandwidths')
                    ax2.set_xlabel('bandwidth')
                    ax2.set_ylabel('error')
                    ax2.scatter(self.optimization_outputs['opt_bandwidth'], opt_error, c = 'r')
                    ax2.vlines(x=self.optimization_outputs['opt_bandwidth'], ymin=opt_error/5, ymax=opt_error, colors='r', linestyles='--')
                    ax2.hlines(y=opt_error, xmin=0, xmax=self.optimization_outputs['opt_bandwidth'], colors='r', linestyles='--')
                    if show_fig:
                        plt.show()
                    if save_fig:
                            if fig_path is None:
                                plt.savefig("learning_curve.png", format = 'png', dpi=dpi, bbox_inches='tight')
                            else:
                                plt.savefig(fig_path, format = 'png', dpi=dpi, bbox_inches='tight')



# ========== KernelSmoother method =================

class KernelSmoother(GradientCOBRA):
    def __init__(self,
                random_state = None,
                learning_rate = 0.1,
                bandwidth_list = None,
                speed = 'constant',
                opt_method = "grad",
                max_iter = int(300),
                opt_params = None,
                kernel = 'radial', 
                kernel_exponent = 1.0,
                show_progress = True,
                loss_function = None,
                loss_weight = None,
                norm_constant = None):
        
        r"""
        This class implements a Kernel Smoother method $y(x)=\sum_{j=0}^{N}W_j(x)y_j$, with weights $W_j(x) >= 0$ and $\sum W_j(x) = 1$.

        * Parameters:
        ------------
            - `random_state`: (default is `None`) set the random state of the random generators in the class.
            
            - `learning_rate`: (default is `0.01`) the learning rate in gradient descent algorithm for estimating the optimal bandwidth.
            
            - `bandwidth_list`: a list of bandwidth parameters for grid search algorithm (default = np.linspace(0.00001, 10, 300)).
            
            - `speed`: (default is `constant`) the adjusting speed of the learning rate. It is helpful when the cost function is flate around the optimal value, changing the learning speed might help the algorithm to converge faster.
                It should be an element of ['constant', 'linear', 'log', 'sqrt_root', 'quad', 'exp'].
            
            - `opt_method`: (default is "grad") optimization algorithm for estimating the bandwidth parameter. 
                It should be either "grid" (grid search) or "grad" (gradient descent for non-compactly supported kernel). 
                By default, it is set to be "grad" with default "radial" kernel.
                
            - `max_iter`: maximum iteration of gradient descent algorithm (default = 100)
            
            - opt_params: (default is 'None') a dictionary of additional parameters for the optimization algorithm (both grid search and gradient descent). 
                Its should contain some of the following keys:
                - 'epsilon'         : stopping criterion for gradient descent algorithm (default = 10 ** (-2))
                - 'n_tries'         : the number of tries for selecting initial position of gradient descent algorithm (default = 5)
                - 'start'           : the initial value of the bandwidth parameter (default = None)
                - 'n_cv'            : number of cross-validation folds (default = int(5))
                - 'precision'       : the precision to estimate the gradient for gradient descent algorithm (default = 2 * 10 ** (-5)).
            
             - `kernel`: (default is 'radial') the kernel function used for the aggregation. 
                It should be an element of the list ['exponential', 'gaussian', 'radial', 'cauchy', 'reverse_cosh', 'epanechnikov', 'biweight', 'triweight', 'triangular', 'naive'].
                Some options such as 'gaussian' and 'radial' lead to the same radial kernel function. 
                For 'cobra' or 'naive', they correspond to Biau et al. (2016).

            - `kernel_exponent`: (default is 1.0) exponential `alpha` of the exponential and radial kernel function i.e., K(x) = exp(|x|^{\alpha}}). By default, alpha = 2.0,

            - show_progress: (default is `True`) boolean defining whether or not to show the progress of the optimization algorithm for both grid search and gradient descent.

            - `loss_function`: (default is None) a function or string defining the cost function to be optimized for estimating the optimal bandwidth parameter.
                By defalut, the K-Fold cross-validation MSE is used. Otherwise, it must be either:
                - a function of two argumetns (y_true, y_pred) or
                - a string element of the list ['mse', 'mae', 'mape', 'weighted_mse']. If it is `weighted_mse`, one can define the weight for each training point using `loss_weight` argument below.
            
            - `loss_weight`: (default is None) a list of size equals to the size of the training data defining the weight for each individual data point in the loss function. 
                If it is None and the `loss_function = weighted_mse`, then a normalized weight W(i) = 1/PDF(i) is assigned to individual i of the training data.

        * Returns:
        ---------
            self : returns an instance of self. 

        * Methods: 
        ---------
            - fit : fitting the aggregation method on the design features (original data or predicted features).
            - split_data : split the data into D_k = {(X_k,y_k)} and D_l = {(X_l,y_l)} to construct the estimators and perform aggregation respectively.
            - build_basic_estimators : build basic estimators for the aggregation. It is also possible to set the values of (hyper) parameters for each estimators.
            - load_predictions : to make predictions using constructed basic estimators.
            - distances : construct distance matrix according to the kernel function used in the aggregation.
            - kappa_cross_validation_error : the objective function to be minimized.
            - optimize_bandwidth : the optimization method to estimate the optimal bendwidth parameter.
            - predict : for building prediction on the new observations using any given bendwidth or the estimated one.
            - draw_learning_curve : for plotting the graphic of learning algorithm (error vs parameter).
        """
        self.random_state = random_state
        self.learning_rate = learning_rate
        self.bandwidth_list = bandwidth_list
        self.speed = speed
        self.kernel = kernel
        self.show_progress = show_progress
        self.opt_method = opt_method
        self.max_iter = max_iter
        self.opt_params = opt_params
        self.kernel_exponent = kernel_exponent
        self.loss_weight = loss_weight
        self.loss_function = loss_function
        self.norm_constant = norm_constant

    # List of kernel functions
    def reverse_cosh(self, x, y):
        return 1/np.cosh(x*y) ** self.kernel_exponent
        
    def exponential(self, x, y):
        return np.exp(-y*x ** self.kernel_exponent)

    def radial(self, x, y):
        return np.exp(-x*y)
        
    def epanechnikov(self, x, y):
        return (1 - x*y) * (x*y < 1)
        
    def biweight(self, x, y):
        return (1-x*y) ** 2 * (x*y < 1)
        
    def triweight(self, x, y):
        return (1-x*y) ** 3 * (x*y < 1)
        
    def triangular(self, x, y):
        return (1-np.abs(x*y)) * (x*y < 1)
        
    def cauchy(self, x, y):
        return 1/(1 + np.array(x*y))
    
    # List of loss functions
    def mse(self, y_true, pred, id = None):
        return mean_squared_error(y_true, pred)
    def mae(self, y_true, pred, id = None):
        return mean_absolute_error(y_true, pred)
    def mape(self, y_true, pred, id = None):
        return mean_absolute_percentage_error(y_true, pred)
    def wgt_mse(self, y_true, pred, id = None):
        w_err2 = np.dot(self.loss_weight_[id], (y_true - pred) ** 2)/(np.dot(self.loss_weight_[id], y_true) ** 2)
        return w_err2
    def loss_func(self, y_true, pred, id = None):
        return self.loss_function(y_true, pred)

    def fit(self, X, y):
        '''
        This method builds basic estimators and performs optimization algorithm to estimate the bandwidth parameter for the aggregation.
        
        * Parameters:
        -------------
            - `X, y`: the training input and out put.
        '''

        X, y = check_X_y(X, y)
        if X.dtype == object:
            X = X.astype(np.float64)
        if y.dtype == object:
            y = y.astype(np.float64)
        self.X = X
        if self.norm_constant is None:
            self.norm_constant_ = 10 * np.max(np.abs(y))/ np.max(np.max(np.abs(X)))
        else:
            self.norm_constant_ = self.norm_constant * np.max(np.abs(y))/ np.max(np.max(np.abs(X)))
        self.y = y
        opt_param = {'epsilon' : 1e-2,
                     'n_tries' : int(5),
                     'start' : None,
                     'n_cv' : int(5),
                     'precision' : 10 ** (-7)
        }

        if self.bandwidth_list is None:
            self.bandwidth_list_ = np.linspace(0.00001, 10, 300)
        else:
            self.bandwidth_list_ = self.bandwidth_list
        
        # Set optional parameters
        if self.opt_params is not None:
            for obj in self.opt_params:
                opt_param[obj] = self.opt_params[obj]
        self.opt_params_ = opt_param
    
        self.opt_method_ = self.opt_method
        if self.kernel not in ['radial', 'gaussian', 'exponential', 'reverse_cosh']:
            self.opt_method_ = 'grid'

        # Loss function
        if (self.loss_function is None) or (self.loss_function == 'mse') or (self.loss_function == 'mean_squared_error'):
            self.loss = self.mse
        elif (self.loss_function == 'mae') or (self.loss_function == 'mean_absolute_error'):
            self.loss = self.mae
        elif (self.loss_function == "mape") or (self.loss_function == 'mean_absolute_percentage_error'):
            self.loss = self.mape
        elif (self.loss_function == 'weighted_mse') or (self.loss_function == 'weighted_mean_squared_error'):
            if self.loss_weight is None:
                pdf = kde(self.y)(self.y)
                wgt = 1/pdf
                wgt /= np.sum(wgt)
                self.loss_weight_ = wgt
            else:
                self.loss_weight_ = self.loss_weight
            self.loss = self.wgt_mse

        if callable(self.loss_function):
            self.loss = self.loss_func
        gc = GradientCOBRA(
            random_state=self.random_state,
            learning_rate=self.learning_rate,
            bandwidth_list=self.bandwidth_list,
            speed=self.speed,
            opt_method=self.opt_method_,
            max_iter=self.max_iter,
            opt_params=self.opt_params_,
            kernel=self.kernel,
            kernel_exponent=self.kernel_exponent,
            show_progress=self.show_progress,
            loss_function=self.loss_function,
            loss_weight=self.loss_weight,
            norm_constant = self.norm_constant_
        )
        gc_fit = gc.fit(X = self.X,
                        y = self.y,
                        as_predictions=True)
        self.fitted_model = gc_fit
        self.optimization_outputs = gc_fit.optimization_outputs
        return self

    def predict(self, X, bandwidth = None):
        X = check_array(X)
        res = self.fitted_model.predict(X=X, bandwidth=bandwidth)
        return res
    def draw_learning_curve(self, y_test=None, fig_type='qq', save_fig=False, fig_path=None, dpi=None, show_fig=True, engine='plotly'):
        self.fitted_model.draw_learning_curve(y_test=y_test, fig_type=fig_type, save_fig=save_fig, fig_path=fig_path, dpi=dpi, show_fig=show_fig, engine=engine)

