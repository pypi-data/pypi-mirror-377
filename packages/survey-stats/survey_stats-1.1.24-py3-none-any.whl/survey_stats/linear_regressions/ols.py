'''
In this version, the regression is estimated solely based on the variables in the data, and there is no possibility to write formulas on it. However, it is possible to add dependent variable intercepts to the model'''

import pickle, math, copy
import numpy as np
import scipy.stats as scipy_stats
from survey_stats.data_process import Data, Sample
from survey_stats.basic_model import Formula
from survey_stats.functions import subsets, number_to_str, merge_lists
import warnings
warnings.filterwarnings('ignore')



class Model:
    ''''''
    def __init__(self, dep_var:str, indep_vars:str=[], lags:list[int]=[], has_constant:bool=True):
        self.dep_var = dep_var
        self.indep_vars = sorted(set(indep_vars),
                                    key=lambda x:indep_vars.index(x))
        self.lags = lags
        self.has_constant = has_constant

    def __str__(self):
        res = f'{self.dep_var} = c(0) + '
        i = 0
        for lag in self.lags:
            if i == 0:
                res += f'c({i+1})*l{lag}.{self.dep_var}'
            else:
                res += f' + c({i+1})*l{lag}.{self.dep_var}'
            i += 1
        for var in self.indep_vars:
            if i == 0:
                res += f'c({i+1})*{var}'
            else:
                res += f' + c({i+1})*{var}'
            i += 1
        return res


    def estimate(self, sample:Sample, print_result:bool=False, indent:int=0, max_lenght:int=-1):
        #region vars
        vars = [self.dep_var]
        #lags
        data, index = sample.data, sample.data.index()
        laggeds = []
        if self.lags != []:
            for lag in self.lags:
                lagged = f'l{lag}.{self.dep_var}'
                if lagged not in data.variables():
                    data.values[lagged] = {}
                    for j, i in enumerate(index):
                        if j>=lag:
                            data.values[lagged][i] = data.values[self.dep_var][index[j-lag]]
                        else:
                            data.values[lagged][i] = math.nan
                vars.append(lagged)
                laggeds.append(lagged)
        #indeps
        vars += self.indep_vars
        #weights
        if sample.weights != '1':
            if sample.weights in data.variables():
                vars.append(sample.weights)
            else:
                sample.weights = '1'
        #select index
        data = data.select_variables(vars).select_index(sample.index)
        #endregion
        
        data.dropna()
        
        # add constant
        if self.has_constant:
            data.add_a_variable('1', [1 for i in data.index()])
            indep_vars = ['1']+laggeds+self.indep_vars
        else:
            indep_vars = laggeds+self.indep_vars
        
        # y and x matrix
        y_arr = data.select_variables([self.dep_var]).to_numpy()
        x_arr = data.select_variables(indep_vars).to_numpy()
        

        # estimate
        if sample.weights == '1':
            w = 1
            try:
                indep_coefs = np.dot(x_x_inv:=np.linalg.inv(x_x:=np.dot(x_arr.T, x_arr)),
                                                    x_y:=np.dot(x_arr.T, y_arr))
            except Exception as e:
                raise ValueError(f"Error! Near-singular matrix! {e}")
        else:
            w = np.diag([w for _,w in data.values[sample.weights].items()])
            try:
                indep_coefs = np.dot(x_x_inv:=np.linalg.inv(x_x:=np.dot(np.dot(x_arr.T,w),x_arr)),
                                                    x_y:=np.dot(np.dot(x_arr.T,w),y_arr))
            except Exception as e:
                raise ValueError(f"Error! Near-singular matrix! {e}")
        
        # coefs
        indep_coefs = [float(x) for x in indep_coefs]
        eq = Equation(self.dep_var, laggeds, indep_vars, self.lags, self.has_constant, indep_coefs,
                                                x_arr, y_arr, x_x, x_x_inv, x_y, w, data)
        if print_result:
            if max_lenght==-1 or max_lenght<3:
                print(' '*indent+str(eq))
            else:
                print(' '*indent+str(eq)[:max_lenght-3]+'...')
        return eq

    def estimate_skip_collinear(self, sample:Sample, print_progress:bool=False, indent:int=0, subindent:int=5, max_lenght:int=-1):
        if print_progress:
            print(' '*indent+'estimating model of '+self.dep_var)
        if self.formula != '':
            vars_number = len(vars:=self.formula.split('+'))
            if vars_number<=25:
                subvars = sorted(subsets(vars), key=lambda x:len(x), reverse=True)
                for i, regressors in enumerate(subvars):
                    try:
                        return Model(self.dep_var, '+'.join(regressors)).estimate(sample, print_progress, indent+subindent, max_lenght)
                    except:
                        if print_progress:
                            print(' '*(indent+subindent)+f'{i} of {len(subvars)}. number of variables: {len(regressors)}')
            else:
                subvars = sorted(subsets(vars,deep=len(vars),randomly=True), key=lambda x:len(x), reverse=True)
                for i, regressors in enumerate(subvars):
                    try:
                        return Model(self.dep_var, '+'.join(regressors)).estimate(sample, print_progress, indent+subindent, max_lenght)
                    except:
                        if print_progress:
                            print(' '*(indent+subindent)+f'{i} of {len(subvars)}. number of variables: {len(regressors)}')
        elif self.indep_vars != []:
            vars_number = self.has_constant + len(vars:=self.indep_vars)
            if vars_number<=25:
                subvars = sorted(subsets(vars), key=lambda x:len(x), reverse=True)
                for i, regressors in enumerate(subvars):
                    try:
                        return Model(self.dep_var, indep_vars=regressors, has_constant=self.has_constant).estimate(sample, print_progress, indent+subindent, max_lenght)
                    except:
                        if print_progress:
                            print(' '*(indent+subindent)+f'{i} of {len(subvars)}. number of variables: {len(regressors)}')
            else:
                subvars = sorted(subsets(vars,deep=len(vars),randomly=True), key=lambda x:len(x), reverse=True)
                for i, regressors in enumerate(subvars):
                    try:
                        return Model(self.dep_var, indep_vars=regressors, has_constant=self.has_constant).estimate(sample, print_progress, indent+subindent, max_lenght)
                    except:
                        if print_progress:
                            print(' '*(indent+subindent)+f'{i} of {len(subvars)}. number of variables: {len(regressors)}')
        else:
            raise ValueError(f"Error! formula or indep_vars are not defined!")
        
        return 

    def estimate_most_significant(self, sample:Sample, min_significant = 1,
                                  print_progress = True, indent:int=0,subindent:int=5, max_lenght:int=-1):
        if print_progress:
            print(' '*indent+'estimating most significant models of '+self.dep_var)
        indep_vars, lags, has_constant = self.indep_vars.copy(), self.lags.copy(), copy.copy(self.has_constant)
        while len(indep_vars)>0:
            eq = Model(self.dep_var, indep_vars, lags,has_constant
            ).estimate(sample, False, indent+subindent, max_lenght)
            p_values = eq.params.p_values()
            var_droped, prob_droped = sorted([(eq.indep_vars[j] , p) for j, p in enumerate(p_values)],
                                key=lambda x: x[1], reverse=True)[0]
            if prob_droped<=min_significant:
                if print_progress:
                    if max_lenght==-1 or max_lenght<3:
                        print(' '*(indent+subindent)+str(eq))
                    else:
                        print(' '*(indent+subindent)+str(eq)[:max_lenght-3]+'...')
                return eq
                break
            if print_progress:
                print(' '*(indent+subindent)+f'droped: {var_droped}. number of parameters: {len(indep_vars)}.')
            lag = var_droped[1:len(var_droped)-len(self.dep_var)-1]
            if self.dep_var in var_droped and \
                var_droped[0]=='l' and lag.isdigit():
                lags.remove(int(lag))
            elif var_droped == '1':
                has_constant = False
            else:
                indep_vars.remove(var_droped)
        else:
            raise ValueError(f"Error! there isn't any model with minimum significant of {min_significant}.")

class Equation:
    def __init__(self, dep_var:str, laggeds:list[str], indep_vars:list[str], lags:list[int], has_constant:bool,
                    indep_coefs:list[float], x_arr:np.ndarray=None, y_arr:np.ndarray=None,
                    x_x:np.ndarray=None, x_x_inv:np.ndarray=None, x_y:np.ndarray=None,
                    w:np.ndarray=None, data:list=None) -> None:
        self.dep_var = dep_var
        self.laggeds = laggeds
        self.indep_vars = indep_vars
        self.lags = lags
        self.has_constant = has_constant
        self.indep_coefs = indep_coefs
        self.x_arr = x_arr
        self.y_arr =y_arr
        self.x_x = x_x
        self.x_x_inv = x_x_inv
        self.x_y = x_y
        self.w = w
        self.data = data
        self.params =self.params(self.indep_coefs, x_arr, y_arr, x_x, x_x_inv, x_y, w)

    class params:
        def __init__(self, indep_coefs:list[float],
                x_arr:np.ndarray=None, y_arr:np.ndarray=None,
                x_x:np.ndarray=None, x_x_inv:np.ndarray=None,
                x_y:np.ndarray=None, w:np.ndarray=None) -> None:
            self.indep_coefs = indep_coefs
            self.x_arr = x_arr
            self.y_arr =y_arr
            self.x_x = x_x
            self.x_x_inv = x_x_inv
            self.x_y = x_y
            self.w = w

        def obs(self):
            return self.y_arr.shape[0]

        def tss(self):
            if self.w == 1:
                return float(np.dot(self.y_arr.T,self.y_arr)-(np.sum(self.y_arr)**2)/len(self.y_arr))
            else:
                n = len(self.y_arr)
                ys, ys2, n = 0, 0, 0
                for i, y in enumerate(self.y_arr):
                    ys += y * self.w[i][i]
                    ys2 += (y ** 2) * self.w[i][i]
                    n += self.w[i][i]
                return float(ys2 - (ys ** 2)/n)
        
        def df_total(self):
            return self.y_arr.shape[0] - 1
        
        def mst(self):
            return self.tss()/self.df_total()

        def rss(self):
            yf = np.dot(self.x_arr, self.indep_coefs)
            if self.w == 1:
                return float(np.dot(yf.T,yf)-(np.sum(yf)**2)/len(yf))
            else:
                n = len(self.y_arr)
                yfs, yfs2, n = 0, 0, 0
                for i, y in enumerate(self.y_arr):
                    yfs += yf[i] * self.w[i][i]
                    yfs2 += (yf[i] ** 2) * self.w[i][i]
                    n += self.w[i][i]
                return float(yfs2 - (yfs ** 2)/n)

        def df_reg(self):
            return self.x_arr.shape[1] - 1

        def msr(self):
            try:
                return self.rss()/self.df_reg()
            except:
                return math.nan
  
        def ess(self):
            return self.tss() - self.rss()
        
        def df_err(self):
            return self.df_total() - self.df_reg()
        
        def mse(self):
            try:
                return float(self.ess() / self.df_err())
            except:
                return math.nan
        
        def cov_var_coefs(self):
            try:
                return np.dot(self.mse(), self.x_x_inv)
            except:
                n = len(self.indep_coefs)
                return np.array([[math.nan]*n]*n)
        
        def r2(self):
            try:
                return float(self.rss()/self.tss())
            except:
                return math.nan

        def df(self):
            return self.df_total()-self.df_reg()-1
        
        def r2adj(self):
            try:
                return 1-(1-self.r2())*self.df_total()/self.df()
            except:
                return math.nan

        def p_values(self):
            try:
                return [(1 - float(scipy_stats.t.cdf(abs(coefi / self.cov_var_coefs()[i][i]**0.5), self.df())))*2
                            for i, coefi in enumerate(self.indep_coefs)]
            except:
                return math.nan

        def f(self):
            try:
                return self.msr()/self.mse()
            except:
                return math.nan

        def f_prob(self):
            try:
                return 1 - scipy_stats.f.cdf(self.f(), self.df_reg(), self.df_err())
            except:
                return math.nan


    def to_str(self, decimals:int=4):
        res = f'{self.dep_var} = '
        for j, var in enumerate(self.indep_vars):
            coef = self.indep_coefs[j]
            if j==0:
                if coef >=0:
                    res += f'{number_to_str(coef, decimals)}' if var=='1' else f'{number_to_str(coef, decimals)}*{var}'
                else:
                    res += f'-{number_to_str(-coef, decimals)}' if var=='1' else f'-{number_to_str(-coef, decimals)}*{var}'
            else:
                if coef >=0:
                    res += f' + {number_to_str(coef, decimals)}*{var}'
                else:
                    res += f' - {number_to_str(-coef, decimals)}*{var}'
        return res.strip()

    def __str__(self):
        return self.to_str()

    def anova(self):
        def format_floats(x:float):
            if abs(x)<.1 or abs(x)>1000:
                x = f'{x:.2e}'
            else:
                x = f'{x:.2f}'
            return x
        def format_ints(x:int):
            return f'{x:,d}'
        len_title = len('regression')
        # ss
        rss, ess = self.params.rss(), self.params.ess()
        tss = rss + ess
        # df
        df_reg, df_err= self.params.df_reg(), self.params.df_err()
        df_total = df_reg + df_err
        # ms
        msr, mse = rss/df_reg, ess/df_err
        # f
        f = msr/mse
        f_prob = 1 - scipy_stats.f.cdf(f, df_reg, df_err)

        # to string format
        rss, ess, tss = format_floats(rss), format_floats(ess), format_floats(tss)
        df_reg, df_err, df_total = format_ints(df_reg), format_ints(df_err), format_ints(df_total)
        msr, mse = format_floats(msr), format_floats(mse)
        f, f_prob = f'f={format_floats(f)}', f'p-value={format_floats(f_prob)}'
        # length
        len_ss = max(len('sum of squares'), len(rss), len(ess), len(tss))
        len_df = max(len('df.'), len(df_reg), len(df_err), len(df_total))
        len_ms = max(len('mean of squares'), len(msr), len(mse))
        len_f = max(len(f), len(f_prob))
        len_total = 1 + len_title + 1 + len_ss + 1 + len_df + 1 + len_ms + 1 + len_f + 1

        # res
        res = ' ' + 'ANOVA'.center(len_total) + ' \n'
        res += ' ' + '-'*len_total + ' \n'
        res += '|' + ''.center(len_title) + '|' + 'sum of squares'.center(len_ss) + '|' + 'df.'.center(len_df) + '|' + 'mean of squares'.center(len_ms) + '|' + ''.center(len_f) + '|\n'
        res += ' ' + '-'*len_total + ' \n'
        res += '|' + 'regression'.center(len_title) + '|' + rss.center(len_ss) + '|' + df_reg.center(len_df) + '|' + msr.center(len_ms) + '|' + f.center(len_f) + '|\n'
        res += '|' + 'error'.center(len_title) + '|' + ess.center(len_ss) + '|' + df_err.center(len_df) + '|' + mse.center(len_ms) + '|' + f_prob.center(len_f) + '|\n'
        res += ' ' + '-'*len_total + ' \n'
        res += '|' + 'total'.center(len_title) + '|' + tss.center(len_ss) + '|' + df_total.center(len_df) + '|' + ''.center(len_ms) + '|' + ''.center(len_f) + '|\n'
        res += ' ' + '-'*len_total + ' \n'
        return res

    def table(self, decimals:int=4):
        def format_ints(x:int):
            return f'{x:,d}'
        res = f'Method: Ordinary Least Square (OLS)\n'
        res += f'Number of observations: {format_ints(self.params.obs())}\n'
        res += f'Degrees of freedom: {format_ints(self.params.df())}\n'
        res += f'R2: {number_to_str(self.params.r2(),decimals)}\n'
        res += f'Adjusted R2: {number_to_str(self.params.r2adj(), decimals)}\n'
        res += f'\nDependent variable: {self.dep_var}'
        len_var = max([len(var) for var in self.indep_vars]) if self.indep_vars != [] else 9
        coefs = [number_to_str(c, decimals) for c in self.indep_coefs]
        len_coefs = len(max(coefs))
        cov_vars = self.params.cov_var_coefs()
        sds = [number_to_str(cov_vars[i][i]**.5, decimals) for i in range(len(cov_vars))]
        len_sd = len(max(sds))
        ts = [number_to_str(self.indep_coefs[i]/cov_vars[i][i]**.5, decimals) for i in range(len(cov_vars))]
        len_t = len(max(ts))
        p_values = self.params.p_values()
        ps = [number_to_str(p, decimals) for p in p_values]
        len_p_value = len(max(ps))
        
        len_var, len_coefs, len_sd, len_t, len_p_value = [
            i+5 for i in [len_var, len_coefs, len_sd, len_t, len_p_value]]
        len_total = len_var + len_coefs + len_sd + len_t + len_p_value + 4
        res += '\n'
        res += 'Results of Linear Regression\n'
        res += ' ' + '-'*len_total + ' \n'
        res += '|' + 'Variables'.center(len_var) + '|' + 'Coefs.'.center(len_coefs) + '|' + 'std.'.center(
            len_sd) + '|' + 't'.center(len_t) + '|' + 'p-value'.center(len_p_value) + '|\n'
        res += ' ' + '-'*len_total + ' \n'

        for i, var in enumerate(self.indep_vars):
            res += '|' + str(var).center(len_var) + '|' + f'{coefs[i]}'.center(len_coefs) + '|' + f'{sds[i]}'.center(
                len_sd) + '|' + f'{ts[i]}'.center(len_t) + '|' + f'{ps[i]}'.center(len_p_value) + '|\n'
        res += ' ' + '-'*len_total + ' \n'
        res += '\n'
        return res

    def save(self, file_path:str):
        with open(file_path, 'wb') as f:
            pickle.dump(self, f)
        print('Results were saved successfully')

    @classmethod
    def load(cls, file_path:str):
        with open(file_path, 'rb') as f:
            eq = pickle.load(f)
        return eq
    
    def wald_test(self, conditions:dict):
        '''
        condition = {0:0, 3:1, ...}\n
        H0: coef[0] = 0 & coef[3] = 1 & ...\n
        *\n
        return {'wald':w, 'p_value':p, 'result':result}\n

        '''
        R = []
        n = len(self.indep_coefs)
        for cond in conditions:
            row = []
            for i in range(n):
                if cond == i:
                    row.append(1)
                else:
                    row.append(0)
            R.append(row)
        R = np.array(R)
        r = np.array([list(conditions.values())]).T
        coefs = np.array([[c]for c in self.indep_coefs])
        V = np.array(self.params.cov_var_coefs())
        A = np.dot(R,coefs) - r
        B = np.linalg.inv(np.dot(np.dot(R, V/n),np.transpose(R)))
        W = float(np.dot(np.dot(np.transpose(A), B), A))
        p_value = float(1-scipy_stats.chi2.cdf(W, n))
        result = ''
        if 0.05<p_value<=.1:
            result = f'At the 90% confidence level, the coefficients are significantly different from the determined values at the same time.'
        elif 0.01<p_value<=.05:
            result = f'At the 95% confidence level, the coefficients are significantly different from the determined values at the same time.'
        elif p_value<=.01:
            result = f'At the 99% confidence level, the coefficients are significantly different from the determined values at the same time.'
        else:
            result = f'the coefficients are not significantly different from the determined values at the same time.'

        return {'wald':W, 'p_value':p_value, 'result':result}

    def forecast(self, sample:Sample)->Data:
        # lagged
        if self.lags != []:
            index = sample.data.index()
            for lag in self.lags:
                lagged = f'l{lag}.{self.dep_var}'
                sample.data.values[lagged] = {}
                for j, i in enumerate(index):
                    if j>=lag:
                        sample.data.values[lagged][i] = sample.data.values[self.dep_var][index[j-lag]]
                        
                    else:
                        sample.data.values[lagged][i] = math.nan
        # constant
        if self.has_constant:
            sample.data.add_a_variable('1', [1 for i in sample.data.index()])
        # forecast
        forecast_data = Data(self.data.type, {})
        forecast_data.values[self.dep_var + '_f'] = {}
        for j, i in enumerate(sample.index):
            f = sum([sample.data.values[var][i] * self.indep_coefs[j]
                                    for j, var in enumerate(self.indep_vars)])
            forecast_data.values[self.dep_var + '_f'][i] = f
            # adding laggeds to data
            if self.lags != []:
                for lag in self.lags:
                    lagged = f'l{lag}.{self.dep_var}'
                    try:
                        sample.data.values[lagged][sample.index[j+lag]] = f
                    except:
                        pass
        return forecast_data
