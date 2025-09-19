# Import all the libraries 
# ========================
from sklearn.cluster import KMeans
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, AdaBoostRegressor, ExtraTreesRegressor
from sklearn.linear_model import RidgeCV, LassoCV, BayesianRidge, SGDRegressor, LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.svm import SVR
from sklearn.utils import shuffle
from sklearn.utils.validation import check_X_y, check_array
from scipy import spatial, optimize
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


class MixCOBRARegressor(BaseEstimator):
    def __init__(self,
                random_state = None,
                learning_rate = 0.01,
                speed = 'constant',
                estimator_list = None, 
                estimator_params = None, 
                opt_method = "grid",
                opt_params = None,
                kernel = 'radial', 
                kernel_exponent = 2.0,
                alpha_list = None,
                beta_list = None,
                bandwidth_list = None,
                max_iter =int(300),
                show_progress = True,
                loss_function = None,
                loss_weight = None,
                norm_constant_x = None,
                norm_constant_y = None):
        """
        This is a class of the implementation of MixCOBRA aggregation method for regression by A. Fischer and M. Mougeot (2019).

        * Parameters:
        ------------
            - `random_state` : (default is `None`) set the random state of the random generators in the class.

            - `learning_rate` : (default is `0.01`) the learning rate in gradient descent algorithm for estimating the optimal bandwidth.

            - `speed`: (default is `constant`) the adjusting speed of the learning rate. It is helpful when the cost function is flate around the optimal value, changing the learning speed might help the algorithm to converge faster.
                It should be an element of ['constant', 'linear', 'log', 'sqrt_root', 'quad', 'exp'].

            - `estimator_list` : (default is None) the list of intial estimators (machines as addressed in Biau et al. (2016)). 
                If it is None, intial estimators: 'knn', 'ridge', 'lasso', 'tree', 'random_forest' and 'svm' are used with default parameters.
                It should be a sublist of the following list: ['knn', 'ridge', 'lasso', 'tree', 'random_forest', 'svm', 'sgd', 'bayesian_ridge', 'adaboost', 'gradient_boost'].
            
            - `estimator_params`: (default is `None`) a dictionary containing the parameters of the basic estimators given in the `estimator_list` argument. 
                It must be a dictionary with:
                - `key`     : the name of the basic estimator defined in `estimator_list`, 
                - `value`   : a dictionary with (key, value) = (parameter, value).

            - `opt_method` : (default is "grad") optimization algorithm for estimating the bandwidth parameter. 
                It should be either "grid" (grid search) or "grad" (gradient descent for non-compactly supported kernel). 
                By default, it is set to be "grad" with default "radial" kernel.
            
            - `opt_params` : (default is 'None') a dictionary of additional parameters for the optimization algorithm (both grid search and gradient descent). 
                Its should contain some of the following keys:
                - 'epsilon'         : stopping criterion for gradient descent algorithm (default = 10 ** (-2))
                - 'n_tries'         : the number of tries for selecting initial position of gradient descent algorithm (default = 5)
                - 'start'           : the initial value of the bandwidth parameter (default = None)
                - 'n_cv'            : number of cross-validation folds (default = int(5))
                - 'precision'       : the precision to estimate the gradient for gradient descent algorithm (default = 10 ** (-7)).
            
             - `kernel`: (default is 'radial') the kernel function used for the aggregation. 
                It should be an element of the list ['exponential', 'gaussian', 'radial', 'cauchy', 'reverse_cosh', 'epanechnikov', 'biweight', 'triweight', 'triangular'].
                Some options such as 'gaussian' and 'radial' lead to the same radial kernel function. 
                For 'cobra' or 'naive', they correspond to Biau et al. (2016).

            - `kernel_exponent`: (default is None) a dictionary of the following keys:
            
            - `alpha_list` and `beta_list` : (default are None) lists or arrays of `alpha` and `beta` (the first and second smoothing parameter) of MixCOBRA method. By default = None, the values of `np.linspace(0.00001, 5, 100)` are used

            - 'bandwidth_list'  : (default is None) a list of bandwidth parameters for grid search algorithm. By default = None, the values of `np.linspace(0.00001, 10, 100)` is used.

            - `max_iter` : (default is int(300)) maximum iteration of gradient descent algorithm (default = 300).

            - `show_progress` : (default is `True`) boolean defining whether or not to show the progress of the optimization algorithm for both grid search and gradient descent.

            - `loss_function` : (default is None) a function or string defining the cost function to be optimized for estimating the optimal bandwidth parameter.
                By defalut, the K-Fold cross-validation MSE is used. Otherwise, it must be either:
                - a function of two argumetns (y_true, y_pred) or
                - a string element of the list ['mse', 'mae', 'mape', 'weighted_mse']. If it is `weighted_mse`, one can define the weight for each training point using `loss_weight` argument below.
            
            - `loss_weight` : (default is None) a list of size equals to the size of the training data defining the weight for each individual data point in the loss function. 
                If it is None and the `loss_function = weighted_mse`, then a normalized weight W(i) = 1/PDF(i) is assigned to individual i of the training data.

            - `norm_constant_x`, `norm_constant_y` : (default is None) the normalize constant of inputs and output resp. This allows to scale the range of the bandwidth parameters $(\alpha, \beta)$.
        
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
            - kappa_cross_validation_error : the objective function to be minimized for one parameter only.
            - kappa_cross_validation_error2 : the objective function to be minimized for two parameters.
            - optimize_bandwidth : the optimization method to estimate the optimal bendwidth parameter.
            - predict : for building prediction on the new observations using any given bendwidth or the estimated one.
            - draw_learning_curve : for plotting the graphic of learning algorithm (error vs parameter).
        """

        self.random_state = random_state
        self.learning_rate = learning_rate
        self.speed = speed
        self.kernel = kernel
        self.estimator_list = estimator_list
        self.show_progress = show_progress
        self.estimator_params = estimator_params
        self.opt_method = opt_method
        self.opt_params = opt_params
        self.kernel_exponent = kernel_exponent
        self.alpha_list = alpha_list
        self.beta_list = beta_list
        self.bandwidth_list = bandwidth_list
        self.max_iter = max_iter
        self.loss_weight = loss_weight
        self.loss_function = loss_function
        self.norm_constant_x = norm_constant_x
        self.norm_constant_y = norm_constant_y

    # List of kernel functions
    def reverse_cosh(self, x, y = 0, al = 1, be = 0):
        return 1/np.cosh(al*x+be*y)
    
    def exponential(self, x, y = 0, al = 1, be = 0):
        return np.exp(-(al*x+be*y) ** self.kernel_exponent)

    def radial(self, x, y = 0, al = 1, be = 0):
        return np.exp(-(al*x+be*y))
        
    def epanechnikov(self, x, y = 0, al = 1, be = 0):
        return (1 - (al*x+be*y)) * (al*x+be*y < 1)
        
    def biweight(self, x, y = 0, al = 1, be = 0):
        return (1-(al*x+be*y)) ** 2 * ((al*x+be*y) < 1)
        
    def triweight(self, x, y = 0, al = 1, be = 0):
        return (1-(al*x+be*y)) ** 3 * ((al*x+be*y) < 1)
        
    def triangular(self, x, y = 0, al = 1, be = 0):
        return (1-np.abs(al*x+be*y)) * ((al*x+be*y) < 1)
        
    def cauchy(self, x, y = 0, al = 1, be = 0):
        return 1/(1 + np.array(al*x+be*y))
    
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
            Pred_features = None,
            split = .5, 
            overlap = 0,
            one_parameter = False):
        '''
        This method builds basic estimators and performs optimization algorithm to estimate the bandwidth parameter for the aggregation.
        
        * Parameters:
        -------------
            - `X, y`                : the training input and out put. If the argument `as_predictions = True`, then these two inputs should be the pretrained predicted features and its corresponding target, and the optimization algorithm is performed directly on it.
            - `X_l, y_l`            : optional aggregation part of the training data (`(X_l, y_l)` in the paper). By default, they are `None`, if given, the argument `(X, y)` will be treated as `(X_k, y_k)` for building basic estimators, and the given (X_l, y_l) will be used for aggregation.
                                      If (X_l, y_l) is not `None`, then the argument `as_predictions` is automatically set to be `False` because both parts of the training data are provided.
            - `Prd_features`        : predicted features of `X_l` given by the basic estimators. In MixCOBRA, if one wants to combine pretrained data, both input data and its predictions must be given. 
            - `split`               : the proportion of `(X_k, y_k)` for training basic estimators. By default, it is equal to 0.5.
            - `overlap`             : the proportion of overlapping data between `(X_k, y_k)` and `(X_l, y_l)`. It is 0 by default.
            - `one_parameter`       : a boolean type controlling whether or not the input-predicted feature `(X, Predict(X))` should be treated as a single feature, i.e., only one smoothing parameter is used.
        '''
        X, y = check_X_y(X, y)
        if X.dtype == object:
            X = X.astype(np.float64)
        if y.dtype == object:
            y = y.astype(np.float64)
        self.X_ = X
        self.y_ = y
        if self.norm_constant_x is None:
            self.normalize_constant_x =  5 / (np.max(np.abs(X), axis=0) * X.shape[1])
        else:
            self.normalize_constant_x = self.norm_constant_x / (np.max(np.abs(X), axis=0) * X.shape[1])
        if self.estimator_list is None:
            M = 6
        else:
            M = len(self.estimator_list)
        if self.norm_constant_y is None:
            self.normalize_constant_y = 50 / (np.max(np.abs(y)) * M)
        else:
            self.normalize_constant_y = self.norm_constant_y / (np.max(np.abs(y)) * M)
        self.as_predictions_ = False
        self.shuffle_input_ = True
        if (X_l is not None) and (y_l is not None):
            X_l, y_l = check_X_y(X_l, y_l)
            self.X_k_, self.X_l_ = X, X_l
            self.y_k_, self.y_l_ = y, y_l
            self.shuffle_input_ = False
            self.iloc_l = np.array(range(len(self.y_l_)), dtype = np.int64)
        if Pred_features is not None:
            self.X_l_ = X
            self.y_l_ = y
            self.Pred_X_l_ = check_array(Pred_features) * self.normalize_constant_y
            self.as_predictions_ = True
            self.iloc_l = np.array(range(len(self.y_l_)), dtype = np.int64)
            self.feature_dim = self.Pred_X_l_
        self.input_dim = self.X_

        # Parameter grid
        if self.bandwidth_list is None:
            self.bandwidth_list_ = np.linspace(0.0001, 10, 300)
        else:
            self.bandwidth_list_ = self.bandwidth_list

        if self.alpha_list is None:
            self.alpha_list_ = np.linspace(0.00001, 10, 50)
        else:
            self.alpha_list_ = self.alpha_list

        if self.beta_list is None:
            self.beta_list_ = np.linspace(0.00001, 10, 50)
        else:
            self.beta_list_ = self.beta_list
        
        # Optimization parameters
        self.basic_estimtors = {}
        opt_param = {'epsilon' : 10 ** (-2),
                     'n_tries' : int(5),
                     'start' : None,
                     'n_cv' : int(5),
                     'precision' : 10 ** (-7)}
        
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
            'cauchy' : self.cauchy}

        # Loss function to be optimized 
        if (self.loss_function is None) or (self.loss_function == 'mse') or (self.loss_function == 'mean_squared_error'):
            self.loss = self.mse
        elif (self.loss_function == 'mae') or (self.loss_function == 'mean_absolute_error'):
            self.loss = self.mae
        elif (self.loss_function == "mape") or (self.loss_function == 'mean_absolute_percentage_error'):
            self.loss = self.mape
        elif (self.loss_function == 'weighted_mse') or (self.loss_function == 'weighted_mean_squared_error'):
            if self.loss_weight is None:
                pdf = kde(self.y_)(self.y_)
                wgt = 1 / pdf
                wgt /= np.sum(wgt)
                self.loss_weight_ = wgt
            else:
                self.loss_weight_ = self.loss_weight
            self.loss = self.wgt_mse

        if callable(self.loss_function):
            self.loss = self.loss_func
        self.one_parameter = one_parameter
        if not self.as_predictions_:
            self.split_data(split = split, 
                            overlap=overlap, 
                            shuffle_data=self.shuffle_input_)
            self.build_baisc_estimators()
            self.load_predictions()
            self.optimize_bandwidth(params = self.opt_params_, 
                                    one_parameter = one_parameter)
        else:
            self.optimize_bandwidth(params = self.opt_params_, 
                                    one_parameter = one_parameter)
        return self
    
    def split_data(self, 
                   split, 
                   overlap = 0, 
                   shuffle_data = True):
        if shuffle_data:
            self.shuffled_index = shuffle(range(len(self.y_)), 
                                          random_state=self.random_state)
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
            self.pred_features[machine] = self.basic_estimators[machine].predict(self.X_l_) * self.normalize_constant_y
        self.Pred_X_l_ = np.column_stack([v for v in self.pred_features.values()])
        return self

    def distances(self, x, pred_test = None, p = 2, type_ = None):
        if pred_test is None:
            ids = np.array(range(self.opt_params_['n_cv']))
            size_each = x.shape[0] // self.opt_params_['n_cv']
            size_remain = x.shape[0] - size_each * self.opt_params_['n_cv']
            self.shuffled_index_cv = shuffle(
                np.concatenate([np.repeat(ids, size_each), 
                                np.random.choice(ids, size_remain)]),
                random_state=self.random_state
            )
            if type_ is None:
                self.distance_matrix = spatial.distance_matrix(x,x,p) ** 2
            elif type_ == "input":
                self.input_distance_matrix = spatial.distance_matrix(x,x,p) ** 2
            elif type_ == "pred":
                self.pred_distance_matrix = spatial.distance_matrix(x,x,p) ** 2
        else:
            if type_ is None:
                self.distance_matrix_test = spatial.distance_matrix(x,pred_test,p) ** 2
            elif type_ == "input":
                self.input_distance_matrix_test = spatial.distance_matrix(x,pred_test,p) ** 2
            elif type_ == "pred":
                self.pred_distance_matrix_test = spatial.distance_matrix(x,pred_test,p) ** 2

    def kappa_cross_validation_error(self, bandwidth = 1):
        list_kernels = self.list_kernels
        cost = np.full(self.opt_params_['n_cv'], 
                       fill_value = np.float32)
        for i in range(self.opt_params_['n_cv']):
            D_k = list_kernels[self.kernel](
                x = self.distance_matrix[self.shuffled_index_cv != i,:][:,self.shuffled_index_cv == i], 
                y = 0,
                al = bandwidth)
            D_k_ = np.sum(D_k, axis=0, dtype=np.float32)
            D_k_[(D_k_ == 0) | np.isnan(D_k_)] = np.inf
            res = np.matmul(self.y_l_[self.shuffled_index_cv != i], D_k)/D_k_
            res[np.isnan(res)] = 0
            temp = self.loss(self.y_l_[self.shuffled_index_cv == i], 
                             res, 
                             id = self.iloc_l[self.shuffled_index_cv == i])
            if np.isnan(temp):
                cost[i] = np.inf
            else:
                cost[i] = temp
        return cost.mean()
    
    def kappa_cross_validation_error2(self, alpha = 1, beta = 1):
        list_kernels = self.list_kernels
        cost = np.full(self.opt_params_['n_cv'], 
                       fill_value = np.float32)
        for i in range(self.opt_params_['n_cv']):
            D_k = list_kernels[self.kernel](
                x = self.input_distance_matrix[self.shuffled_index_cv != i,:][:,self.shuffled_index_cv == i], 
                y = self.pred_distance_matrix[self.shuffled_index_cv != i,:][:,self.shuffled_index_cv == i],
                al = alpha,
                be = beta)
            D_k_ = np.sum(D_k, axis=0, dtype=np.float32)
            D_k_[(D_k_ == 0) | np.isnan(D_k_)] = np.inf
            res = np.matmul(self.y_l_[self.shuffled_index_cv != i], D_k)/D_k_
            res[np.isnan(res)] = 0
            temp = self.loss(self.y_l_[self.shuffled_index_cv == i],
                             res, 
                             id = self.iloc_l[self.shuffled_index_cv == i])
            if np.isnan(temp):
                cost[i] = np.inf
            else:
                cost[i] = temp
        return cost.mean()
        
    def optimize_bandwidth(self, 
                           params, 
                           one_parameter = False):
        def norm1(x):
            return np.sum(np.abs(x))
        def select_best_index1(arr):
            if len(arr) > 1:
                return arr[arr.shape[0]//2]
            else:
                return arr
            
        def gradient(f, x0, eps = params['precision']):
            return np.array([(f(bandwidth = x0 + eps) - f(bandwidth = x0 - eps))/(2*eps)])
        
        def gradient2(f, x0, y0, eps = params['precision']):
            return np.array([(f(alpha = x0 + eps, beta = y0) - f(alpha = x0 - eps, beta = y0))/(2*eps), 
                             (f(alpha = x0, beta = y0 + eps) - f(alpha = x0, beta = y0 - eps))/(2*eps)])

        kernel_to_dist = {'reverse_cosh' : 'l2',
                          'inverse_cosh' : 'l2',
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
        if self.distance in ['l1']:
            self.p_ = 1
        else:
            self.p_ = 2
        self.X_l_normalized = self.X_l_ * self.normalize_constant_x
        if self.opt_method_ in ['grid', 'grid_search', 'grid search']:
            if one_parameter:
                self.Mix_X_l_ = np.column_stack([self.X_l_normalized, self.Pred_X_l_])
                self.distances(x = self.Mix_X_l_, 
                               p = self.p_)
                n_iter = len(self.bandwidth_list_)
                errors = np.full(n_iter, np.float32)
                if self.show_progress:
                    for i in tqdm(range(n_iter), "* 1D-grid search"):
                        errors[i] = self.kappa_cross_validation_error(bandwidth = self.bandwidth_list_[i])
                else:
                    for i in range(n_iter):
                        errors[i] = self.kappa_cross_validation_error(bandwidth = self.bandwidth_list_[i])
                opt_risk = np.min(errors)
                opt_id = select_best_index1(np.where(errors == opt_risk))
                self.optimization_outputs = {
                    'opt_method' : 'grid',
                    'opt_bandwidth' : self.bandwidth_list_[opt_id[0]][0],
                    'opt_alpha' : None,
                    'opt_beta' : None,
                    'opt_error' : opt_risk,
                    'opt_index': opt_id[0],
                    'kappa_cv_errors': errors}
            else:
                self.distances(x = self.X_l_normalized, p = self.p_, type_= "input")
                self.distances(x = self.Pred_X_l_, p = self.p_, type_= "pred")
                n_iter = len(self.alpha_list_) * len(self.beta_list_)
                errors = np.full((len(self.alpha_list_), len(self.beta_list_)), np.float32)
                if self.show_progress:
                    for i in tqdm(range(len(self.alpha_list_)), "* 2D-grid search"):
                        for j in range(len(self.beta_list_)):
                            errors[i,j] = self.kappa_cross_validation_error2(alpha=self.alpha_list_[i],
                                                                             beta=self.beta_list_[j])
                else:
                    for i in range(len(self.alpha_list_)):
                        for j in range(len(self.beta_list_)):
                            errors[i,j] = self.kappa_cross_validation_error2(alpha=self.alpha_list_[i],
                                                                             beta=self.beta_list_[j])
                opt_risk = np.min(np.min(errors))
                opt_id = np.where(errors == opt_risk)
                opt_id = (opt_id[0][0], opt_id[1][0])
                self.optimization_outputs = {
                    'opt_method' : 'grid',
                    'opt_bandwidth' : None,
                    'opt_error' : opt_risk,
                    'opt_alpha' : self.alpha_list_[opt_id[0]],
                    'opt_beta' : self.beta_list_[opt_id[1]],
                    'opt_index': (opt_id[0], opt_id[1]),
                    'kappa_cv_errors': errors}
        if self.opt_method_ in ['grad', 'gradient descent', 'gd', 'GD']:
            speed_list = {
                    'constant' : lambda x, y: y,
                    'linear' : lambda x, y: x*y,
                    'log' : lambda x, y: np.log(1+x) * y,
                    'sqrt_root' : lambda x, y: np.sqrt(1+x) * y,
                    'quad' : lambda x, y: (1+x ** 2) * y,
                    'exp' : lambda x, y: np.exp(x) * y
            }
            if one_parameter:
                self.Mix_X_l_ = np.column_stack([self.X_l_normalized, self.Pred_X_l_])
                self.distances(x = self.Mix_X_l_, 
                               p = self.p_)
                n_iter = len(self.bandwidth_list_)
                errors = np.full(n_iter, float)
                collect_bw = []
                gradients = []
                if params['start'] is None:
                    bws = np.linspace(0.01, 3, num = params['n_tries'])
                    initial_tries = [self.kappa_cross_validation_error(bandwidth=b) for b in bws]
                    bw0 = bws[np.argmin(initial_tries)]
                else:
                    bw0 = params['start']
                grad = gradient(self.kappa_cross_validation_error, bw0, params['precision'])
                grad0 = grad
                test_threshold = np.inf
                if self.show_progress:
                    r0 = self.learning_rate / abs(grad)    
                    rate = speed_list[self.speed]
                    count = 1
                    pbar = trange(self.max_iter, desc="* 1D-GD:  iter: %d / bw: %.3f / grad: %.3f / stop criter: %.3f " %(count, bw0, grad[0], test_threshold), leave=True)
                    for count in pbar:
                        bw = bw0 - rate(count, r0) * grad
                        if bw < 0 or np.isnan(bw):
                            bw = bw0 * 0.95
                        if count > 3:
                            if np.sign(grad)*np.sign(grad0) < 0:
                                r0 = r0 * 0.9
                            if test_threshold > self.opt_params_['epsilon']:
                                bw0, grad0 = bw, grad
                            else:
                                break
                        # relative = abs((bw - bw0) / bw0)
                        test_threshold = abs(grad) #np.mean([relative, abs(grad)])
                        grad = gradient(self.kappa_cross_validation_error, bw0, params['precision'])
                        collect_bw.append(bw[0])
                        gradients.append(grad[0])
                        pbar.set_description("* 1D-GD:  iter: %d / bw: %.3f / grad: %.3f / stop at: %.3f " %(count, bw[0], grad[0], params['epsilon']))
                        pbar.refresh()
                else:
                    r0 = self.learning_rate / abs(grad)
                    rate = speed_list[self.speed]
                    count = 0
                    while count < self.max_iter:
                        bw = bw0 - rate(count, r0) * grad
                        if bw < 0 or np.isnan(bw):
                            bw = bw0 * 0.95
                        if count > 3:
                            if np.sign(grad)*np.sign(grad0) < 0:
                                r0 = r0 * 0.9
                            if test_threshold > params['epsilon']:
                                bw0, grad0 = bw, grad
                            else:
                                break
                        # relative = abs((bw - bw0) / bw0)
                        test_threshold = abs(grad) #np.mean([relative, abs(grad)])
                        grad = gradient(self.kappa_cross_validation_error, bw0, params['precision'])
                        count += 1
                        collect_bw.append(bw[0])
                        gradients.append(grad[0])
                opt_bw = bw[0]
                opt_risk = self.kappa_cross_validation_error(opt_bw)
                self.optimization_outputs = {
                    'opt_method' : 'grad',
                    'opt_bandwidth' : opt_bw,
                    'opt_alpha' : None,
                    'opt_beta' : None,
                    'opt_error' : opt_risk,
                    'param_collection' : collect_bw,
                    'gradients': gradients
                }
            else:
                self.distances(x = self.X_l_normalized, p = self.p_, type_= "input")
                self.distances(x = self.Pred_X_l_, p = self.p_, type_= "pred")
                n_iter = len(self.alpha_list_) * len(self.beta_list_)
                errors = np.full((len(self.alpha_list_), len(self.beta_list_)), float)
                collect_bw = []
                gradients = []
                if params['start'] is None:
                    alpha_ = np.linspace(0.01, 5, num = params['n_tries'])
                    beta_ = np.linspace(0.01, 5, num = params['n_tries'])
                    initial_tries = [[self.kappa_cross_validation_error2(alpha = a, beta = b) for b in beta_] for a in alpha_]
                    id_ = np.where(initial_tries == np.min(initial_tries))
                    alp0, bet0 = alpha_[id_[0]], beta_[id_[1]]
                else:
                    alp0, bet0 = params['start'][0], params['start'][1]
                grad = gradient2(self.kappa_cross_validation_error2, x0=alp0, y0=bet0, eps=params['precision'])
                grad0 = grad
                test_threshold = np.inf
                if self.show_progress:
                    r0 = self.learning_rate / norm1(grad)      
                    r1 = r0
                    rate = speed_list[self.speed]  
                    count = 0
                    pbar = trange(self.max_iter, desc="* 2D-GD: iter: %d / (a,b): (%.3f,%.3f) / |grad|: %.3f / stop at: %.3f" %(count, alp0, bet0, norm1(grad), params['epsilon']))
                    for count in pbar:
                        alp, bet = alp0 - rate(count, r0) * grad[0], bet0 - rate(count, r1) * grad[1]
                        if alp < 0 or np.isnan(alp):
                           alp = alp0 * 0.95
                        if bet < 0 or np.isnan(bet):
                            bet = bet0 * 0.95
                        if count > 3:
                            if np.sign(grad[0])*np.sign(grad0[0]) < 0:
                                r0 *= 0.9
                            if np.sign(grad[1])*np.sign(grad0[1]) < 0:
                                r1 *= 0.9
                            if test_threshold > params['epsilon']:
                                alp0, bet0, grad0 = alp, bet, grad
                            else:
                                break
                        test_threshold = norm1(grad)
                        grad = gradient2(self.kappa_cross_validation_error2, x0=alp0, y0=bet0, eps=params['precision'])
                        collect_bw.append([alp0, bet0])
                        gradients.append(grad)
                        pbar.set_description("* 2D-GD: iter: %d / (a,b): (%.3f,%.3f) / |grad|: %.3f / stop at: %.3f" %(count, alp0, bet0, norm1(grad), params['epsilon']))
                        pbar.refresh()
                else:
                    r0 = self.learning_rate / norm1(grad)        # make the first step exactly equal to `learning-rate`.
                    r1 = r0
                    rate = speed_list[self.speed]            # the learning rate can be varied, and speed defines this change in learning rate.
                    count = 0
                    while count < self.max_iter:
                        alp, bet = alp0 - rate(count, r0) * grad[0], bet0 - rate(count, r1) * grad[1]
                        if alp < 0 or np.isnan(alp):
                            alp = alp0 * 0.95
                        if bet < 0 or np.isnan(bet):
                            bet = bet0 * 0.95
                        if count > 3:
                            if np.sign(grad[0])*np.sign(grad0[0]) < 0:
                                r0 *= 0.9
                            if np.sign(grad[1])*np.sign(grad0[1]) < 0:
                                r1 *= 0.9
                            if test_threshold > params['epsilon']:
                                alp0, bet0, grad0 = alp, bet, grad
                            else:
                                break
                        test_threshold = norm1(grad) 
                        grad = gradient2(self.kappa_cross_validation_error2, x0=alp0, y0=bet0, eps=params['precision'])
                        count += 1
                        collect_bw.append([alp0, bet0])
                        gradients.append(grad)
                opt_risk = self.kappa_cross_validation_error2(alpha=alp0, beta=bet0)
                if hasattr(alp0, "__len__"):
                    alp = alp0[0]
                    bet = bet0[0]
                else:
                    alp = alp0
                    bet = bet0
                self.optimization_outputs = {
                    'opt_method' : 'grad',
                    'opt_bandwidth' : None,
                    'opt_alpha' : alp,
                    'opt_beta' : bet,
                    'opt_error' : opt_risk,
                    'param_collection' : np.array(collect_bw),
                    'gradients': np.array(gradients)}
        return self
    
    def predict(self, X, Pred_X = None, alpha = None, beta = None, bandwidth = None):
        X = check_array(X)
        X_normalized = X * self.normalize_constant_x
        if self.as_predictions_:
            try:
                self.Pred_X_test = Pred_X * self.normalize_constant_y
            except TypeError:
                print("There is no basic estimator built. `Pred_X` must NOT be `None`!")
        else:
            self.pred_features_test = {}
            for machine in self.estimator_names:
                self.pred_features_test[machine] = self.basic_estimators[machine].predict(X) * self.normalize_constant_y
            self.Pred_X_test = np.column_stack([v for v in self.pred_features_test.values()])
        if self.one_parameter:
            if bandwidth is None:
                bandwidth = self.optimization_outputs['opt_bandwidth']
            self.Mix_feature_test = np.column_stack([X_normalized, self.Pred_X_test])
            self.distances(x = self.Mix_X_l_,
                           pred_test = self.Mix_feature_test,
                           p = self.p_)
            D_k = self.list_kernels[self.kernel](x = self.distance_matrix_test, 
                                                 y = 0,
                                                 al = bandwidth)
        else:
            if (alpha is None) and (beta is None):
                alpha = self.optimization_outputs['opt_alpha']
                beta = self.optimization_outputs['opt_beta']
            self.distances(x = self.X_l_normalized, 
                    pred_test = X_normalized, 
                    p = self.p_, 
                    type_="input")
            self.distances(x = self.Pred_X_l_, 
                    pred_test = self.Pred_X_test, 
                    p = self.p_,
                    type_="pred")
            D_k = self.list_kernels[self.kernel](x = self.input_distance_matrix_test,
                                                 y = self.pred_distance_matrix_test,
                                                 al = alpha,
                                                 be = beta)
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
                            show_fig = True, 
                            dpi = 300,
                            engine = "plotly"):
        # sns.set()
        opt_color = "#FF0234" # "#21D129"
        path_color = "#259EF8"
        if (y_test is not None) and (fig_type in ['qq', 'qq-plot', 'qqplot', 'QQ-plot', 'QQplot']):
            if engine == "plotly":
                df = pd.DataFrame({
                'y_test' : y_test,
                'y_pred' : self.test_prediction})
                fig = go.Figure(data = px.line(df, 
                                               x = "y_test", 
                                               y = "y_test", 
                                               color_discrete_sequence=['red']).data + px.scatter(df, x = "y_pred", y = "y_test").data)
                fig = fig.update_layout(width = 500, 
                                        height = 450, 
                                        title_text = "QQplot of predicted and actual values", 
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
                fig = plt.figure(figsize=(6, 4))
                plt.plot(y_test, y_test, 'r')
                plt.scatter(y_test, self.test_prediction)
                plt.xlabel('y_test')
                plt.ylabel('prediction')
                plt.title('QQ-plot: actual vs prediction')
                plt.legend()
                if save_fig:
                    if fig_path is not None:
                        fig.savefig("qqplot_aggregation.png", format = 'png', dpi=dpi, bbox_inches='tight')
                    else:
                        fig.savefig(fig_path, format = 'png', dpi=dpi, bbox_inches='tight')
                if show_fig:
                    fig.show()
        else:
            if self.optimization_outputs['opt_method'] in ['grid', 'grid_search', 'grid search']:
                if self.one_parameter:
                    if engine == "plotly":
                        fig = go.Figure(data=[go.Scatter(x = self.bandwidth_list_,
                                                         y = self.optimization_outputs['kappa_cv_errors'],
                                                         mode = 'lines',
                                                         name = "Loss",
                                                         showlegend=False),
                                              go.Scatter(x = [self.optimization_outputs['opt_bandwidth']],
                                                         y = [self.optimization_outputs['opt_error']],
                                                         mode = "markers",
                                                         marker=dict(color = opt_color, 
                                                                     size = 8),
                                                         name="Optimal point"),
                                              go.Scatter(x = [self.optimization_outputs['opt_bandwidth'], 
                                                              self.optimization_outputs['opt_bandwidth'],
                                                              0],
                                                         y = [0,
                                                              self.optimization_outputs['opt_error'],
                                                              self.optimization_outputs['opt_error']],
                                                         mode = "lines",
                                                         line=dict(color = opt_color, 
                                                                   dash = "dash"),
                                                         showlegend=False)])
                        fig = fig.update_layout(width = 500, 
                                                height = 450, 
                                                title_text = "Loss vs bandwidths (grid search)", 
                                                title_x = .5, 
                                                title_y = 0.9)
                        fig.update_xaxes(title_text = "Bandwidth")
                        fig.update_yaxes(title_text = "Loss")
                        if show_fig:
                            fig.show()
                        if save_fig:
                            if fig_path is None:
                                fig.write_image("learning_curve.png")
                            else:
                                fig.write_image(fig_path)
                    else:
                        plt.figure(figsize=(6, 4))
                        plt.plot(self.bandwidth_list_, self.optimization_outputs['kappa_cv_errors'])
                        plt.title('Loss vs bandwidths (grid search)')
                        plt.xlabel('Bandwidth')
                        plt.ylabel('Loss')
                        plt.scatter(self.optimization_outputs['opt_bandwidth'], 
                                    self.optimization_outputs['opt_error'], 
                                    c = opt_color)
                        plt.vlines(x=[self.optimization_outputs['opt_bandwidth']], 
                                   ymin=[self.optimization_outputs['opt_error']/5], 
                                   ymax=[self.optimization_outputs['opt_error']],
                                   colors=opt_color, 
                                   linestyles='--')
                        plt.hlines(y=[self.optimization_outputs['opt_error']], 
                                   xmin=[0], 
                                   xmax=[self.optimization_outputs['opt_bandwidth']], 
                                   colors=opt_color, 
                                   linestyles='--')
                        if show_fig:
                            plt.show()
                        if save_fig:
                            if fig_path is not None:
                                fig.savefig("learning_curve.png", format = 'png', dpi=dpi, bbox_inches='tight')
                            else:
                                fig.savefig(fig_path, format = 'png', dpi=dpi, bbox_inches='tight')
                else:
                    if engine == 'plotly':
                        alpha_, beta_, error_ = self.alpha_list_, self.beta_list_, self.optimization_outputs['kappa_cv_errors']
                        opt_alpha = self.optimization_outputs['opt_alpha']
                        opt_beta = self.optimization_outputs['opt_beta']
                        opt_error = self.optimization_outputs['opt_error']
                        fig = go.Figure(data=[go.Surface(x = alpha_,
                                                         y = beta_,
                                                         z = error_.transpose(),
                                                         name = "Loss",
                                                         showlegend = False,
                                                         opacity=0.8)])
                        fig.add_trace(go.Scatter3d(x = [opt_alpha], 
                                                   y = [opt_beta], 
                                                   z = [opt_error],
                                                   showlegend=False,
                                                   name="Optimal point",
                                                   mode = 'markers',
                                                   marker = dict(color = "#27B629",
                                                   size = 7)))
                        fig.update_layout(scene = dict(
                                            xaxis_title='Alpha',
                                            yaxis_title='Beta',
                                            zaxis_title='Loss'),
                                          title_text = "Loss vs parameters (alpha, beta) with "+ str(self.kernel) + " kernel", 
                                          title_x = .5, 
                                          title_y = 0.925,
                                          width = 500,
                                          height = 450)
                        if show_fig:
                            fig.show()
                        if save_fig:
                            if fig_path is None:
                                fig.write_image("learning_curve.png")
                            else:
                                fig.write_image(fig_path)
                    else:
                        alpha_, beta_ = np.meshgrid(self.alpha_list_, self.beta_list_)
                        error_ = self.optimization_outputs['kappa_cv_errors']
                        opt_alpha = self.optimization_outputs['opt_alpha']
                        opt_beta = self.optimization_outputs['opt_beta'], 
                        opt_error = self.optimization_outputs['opt_error']

                        fig = plt.figure(figsize=(6, 4))
                        axs = fig.add_subplot(projection='3d')
                        surf = axs.plot_surface(X=alpha_, 
                                                Y=beta_, 
                                                Z=error_.transpose(), 
                                                cmap=cm.coolwarm, 
                                                linewidth=0,
                                                antialiased=False)
                        axs.scatter3D([opt_alpha], 
                                      [opt_beta], 
                                      [opt_error],
                                      c = opt_color)
                        axs.set_title("Loss vs parameters (alpha, beta) with "+ str(self.kernel)+ " kernel")
                        axs.set_xlabel("Alpha")
                        axs.set_ylabel("Beta")
                        axs.set_zlabel("Kappa cross-validation error")
                        axs.view_init(30, 120)
                        if show_fig:
                            plt.show()
                        if save_fig:
                            if fig_path is not None:
                                fig.savefig("learning_curve.png", format = 'png', dpi=dpi, bbox_inches='tight')
                            else:
                                fig.savefig(fig_path, format = 'png', dpi=dpi, bbox_inches='tight')
            else:
                if self.one_parameter:
                    if engine == 'plotly':
                        L = {'bandwidth' : np.linspace(self.optimization_outputs['opt_bandwidth']/5, 
                                                       self.optimization_outputs['opt_bandwidth']*5, 20)}
                        L['error'] =  np.array([self.kappa_cross_validation_error(b) for b in L['bandwidth']])
                        df2 = pd.DataFrame(L)
                        
                        f1 = go.Figure([go.Scatter(x = list(range(len(self.optimization_outputs['param_collection']))),
                                                   y = self.optimization_outputs['param_collection'],
                                                   mode = 'lines',
                                                   showlegend=False),
                                        go.Scatter(x = [0, len(self.optimization_outputs['param_collection'])],
                                                   y = [self.optimization_outputs['opt_bandwidth'],
                                                        self.optimization_outputs['opt_bandwidth']],
                                                   showlegend=False,
                                                   line=dict(color = opt_color, 
                                                             dash = "dash"))])
                        f2 = go.Figure([go.Scatter(x = df2.bandwidth, 
                                                   y = df2.error,
                                                   mode = "lines",
                                                   showlegend=False,
                                                   line = dict(color = 'blue')),
                                        go.Scatter(x = [self.optimization_outputs['opt_bandwidth']],
                                                   y = [self.optimization_outputs['opt_error']],
                                                   showlegend=False, 
                                                   mode = "markers",
                                                   marker = dict(color = opt_color, 
                                                                 size = 10)),
                                        go.Scatter(x = [0, 
                                                        self.optimization_outputs['opt_bandwidth'], 
                                                        self.optimization_outputs['opt_bandwidth']], 
                                                   y = [self.optimization_outputs['opt_error'], 
                                                        self.optimization_outputs['opt_error'], 
                                                        0], 
                                                   mode = "markers+lines", 
                                                   line = dict(color = opt_color, 
                                                               dash = 'dash'),
                                                   showlegend=False)])
                        fig = make_subplots(rows=1, 
                                            cols=2, 
                                            print_grid=False, 
                                            subplot_titles=("Bandwidth at each gradient descent step", 
                                                            "Loss vs bandwidth"))
                        fig.update_xaxes(title_text="Iteration", row=1, col=1)
                        fig.update_yaxes(title_text="Bandwidth", row=1, col=1)
                        fig.update_xaxes(title_text="Bandwidth", row=1, col=2)
                        fig.update_yaxes(title_text="Loss", row=1, col=2)
                        fig.update_layout(width = 900, 
                                          height = 450)
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
                        fig = plt.figure(figsize=(12, 4))
                        ax1 = fig.add_subplot(1,2,1)
                        iter_, param_ = list(range(len(self.optimization_outputs['param_collection']))), self.optimization_outputs['param_collection']
                        ax1.plot(iter_, param_)
                        ax1.set_title('Bandwidths at each iteration (gradient descent)')
                        ax1.set_xlabel('Iteration')
                        ax1.set_ylabel('Bandwidth')
                        ax1.hlines(y=self.optimization_outputs['param_collection'][-1], 
                                xmin=0,
                                xmax=self.max_iter, 
                                colors=opt_color, linestyles='--')
                        ax2 = fig.add_subplot(1,2,2)
                        param_range = np.linspace(self.optimization_outputs['opt_bandwidth']/5, 
                                                  self.optimization_outputs['opt_bandwidth']*5, 20)
                        errors = [self.kappa_cross_validation_error(b) for b in param_range] 
                        opt_error = self.kappa_cross_validation_error(self.optimization_outputs['opt_bandwidth']) 
                        ax2.plot(param_range, errors)
                        ax2.set_title('Errors vs bandwidths')
                        ax2.set_xlabel('Bandwidth')
                        ax2.set_ylabel('Error')
                        ax2.scatter(self.optimization_outputs['opt_bandwidth'], opt_error, c = opt_color)
                        ax2.vlines(x=self.optimization_outputs['opt_bandwidth'], 
                                   ymin=opt_error/5, 
                                   ymax=opt_error, 
                                   colors=opt_color, 
                                   linestyles='--')
                        ax2.hlines(y=opt_error,
                                   xmin=0, 
                                   xmax=self.optimization_outputs['opt_bandwidth'], 
                                   colors=opt_color, 
                                   linestyles='--')
                        if show_fig:
                            plt.show()
                        if save_fig:
                            if fig_path is not None:
                                fig.savefig("learning_curve.png", format = 'png', dpi=dpi, bbox_inches='tight')
                            else:
                                fig.savefig(fig_path, format = 'png', dpi=dpi, bbox_inches='tight')
                else:
                    if engine == 'plotly':
                        n = len(self.optimization_outputs['param_collection'][:,0])
                        fig_n = 20
                        al_m, al_M = np.min(self.optimization_outputs['param_collection'][:,0]), np.max(self.optimization_outputs['param_collection'][:,0])
                        be_m, be_M = np.min(self.optimization_outputs['param_collection'][:,1]), np.max(self.optimization_outputs['param_collection'][:,1])
                        alpha_, beta_ = np.meshgrid(np.linspace(al_m, al_M, fig_n), np.linspace(be_m, be_M, fig_n))
                        error =  np.array([[self.kappa_cross_validation_error2(alpha_[i,j], beta_[i,j]) for j in range(len(alpha_[0]))] for i in range(len(alpha_))])
                        opt_alpha, opt_beta = self.optimization_outputs['opt_alpha'], self.optimization_outputs['opt_beta']
                        opt_error = self.optimization_outputs['opt_error']
                        err_path = np.array([self.kappa_cross_validation_error2(a, b) for a,b in zip(self.optimization_outputs['param_collection'][:,0][range(0,n, 5)], 
                                                                                                      self.optimization_outputs['param_collection'][:,1][range(0,n, 5)])])                                                        
                        col_path = np.concatenate([np.repeat("#0E94F7", len(range(0, n, 5))-1)])
                        col_size = np.concatenate([np.repeat(7, len(range(0, n, 5))-1)])
                        fig = go.Figure()
                        fig.add_trace(go.Surface(z = error,
                                                 x = alpha_,
                                                 y = beta_,
                                                 opacity=0.8,
                                                 showlegend=False,
                                                 name="Loss"))
                        fig.add_trace(go.Scatter3d(x=self.optimization_outputs['param_collection'][:,0][range(0,n, 5)].reshape(-1)[:-1], 
                                                   y=self.optimization_outputs['param_collection'][:,1][range(0,n, 5)].reshape(-1)[:-1], 
                                                   z=err_path[:-1],
                                                   name="Gradient path",
                                                   mode = "markers+lines",
                                                   showlegend=False,
                                                   marker=dict(size=col_size,
                                                               color = col_path),
                                                   line=dict(color=col_path,
                                                             width=5)))
                        fig.add_trace(go.Scatter3d(x=[opt_alpha], 
                                                   y=[opt_beta], 
                                                   z=[opt_error],
                                                   name="Optimal point",
                                                   mode = "markers",
                                                   showlegend=False,
                                                   marker=dict(size=7,
                                                               color = "#27B629")))
                        fig.update_layout(scene = dict(
                                            xaxis_title='Alpha',
                                            yaxis_title='Beta',
                                            zaxis_title='Loss'),
                                          title_text = "Loss vs parameters (alpha, beta) with "+ str(self.kernel) + " kernel", 
                                          title_x = .5,
                                          title_y = 0.925,
                                          width = 500,
                                          height = 450)
                        if show_fig:
                            fig.show()
                        if save_fig:
                            if fig_path is None:
                                fig.write_image("learning_curve.png")
                            else:
                                fig.write_image(fig_path)
                    else:
                        n = len(self.optimization_outputs['param_collection'][:,0])
                        fig_n = 20
                        al_m, al_M = np.min(self.optimization_outputs['param_collection'][:,0]), np.max(self.optimization_outputs['param_collection'][:,0])
                        be_m, be_M = np.min(self.optimization_outputs['param_collection'][:,1]), np.max(self.optimization_outputs['param_collection'][:,1])
                        alpha_, beta_ = np.meshgrid(np.linspace(al_m, al_M, fig_n), 
                                                    np.linspace(be_m, be_M, fig_n))
                        
                        err =  np.array([[self.kappa_cross_validation_error2(alpha_[i,j],beta_[i,j]) for j in range(len(alpha_[0]))] for i in range(len(beta_))])
                        opt_alpha, opt_beta = self.optimization_outputs['opt_alpha'], self.optimization_outputs['opt_beta']
                        opt_error = self.optimization_outputs['opt_error']
                        fig = plt.figure(figsize=(13, 5))
                        axs = fig.add_subplot(projection='3d')
                        err_path = np.array([self.kappa_cross_validation_error2(a, b) for a,b in zip(self.optimization_outputs['param_collection'][:,0][range(0,n, 5)], 
                                                                                            self.optimization_outputs['param_collection'][:,1][range(0,n, 5)])])
                        axs.plot_surface(alpha_, beta_, err, cmap=cm.coolwarm, linewidth=0, antialiased=False, label = "Loss")
                        axs.scatter(opt_alpha, opt_beta, opt_error, c = opt_color, label = "Optimal point")
                        axs.scatter(self.optimization_outputs['param_collection'][:,0][range(0,n,5)].reshape(-1),
                                    self.optimization_outputs['param_collection'][:,1][range(0,n,5)].reshape(-1),
                                    err_path, '-o', c = opt_color)
                        axs.set_title("Loss vs parameters (alpha, beta) with "+ str(self.kernel)+ " kernel")
                        axs.set_xlabel("Alpha")
                        axs.set_ylabel("Beta")
                        axs.set_zlabel("Kappa cross-validation error")
                        axs.view_init(30, 150)
                        if save_fig:
                            if fig_path is not None:
                                fig.savefig("learning_curve.png", format = 'png', dpi=dpi, bbox_inches='tight')
                            else:
                                fig.savefig(fig_path, format = 'png', dpi=dpi, bbox_inches='tight')
                        if show_fig:
                            plt.show()