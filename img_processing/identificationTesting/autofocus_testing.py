# autofocus

import numpy as np
import dwt


def golden_section(a,d):
    """Given an interval, returns the next two intervals using the golden ratio
    The interval is arranged as [a, b, c, d]
    """
    golden = (1 + 5 ** 0.5) / 2     # Golden ratio

    # New interval point to test
    delta_x = d * (1 - 1/golden)
    b = a + delta_x
    #c = d - delta_x
    
    return b

def golden_section_interval_reduction(interval, f, finterval,  tolerance = 50, iterations = 0, iter_max = 1000, min_tolerance = 5):
    """ Carry out optimization to find position of minimum value for 'f'
        interval = (a, b, d) is the interval to search within
        finterval = (f(a), f(b), f(d)) is the function value for each interval
        f(x) is the function to be minimized
    """
    a = interval[0]
    b = interval[1]
    d = interval[2]
    
    f1 = finterval[0]
    f2 = finterval[1]
    f4 = finterval[2]
    
    if (tolerance > min_tolerance or iter_max < iterations):
        
        # Evaluate values
        c = golden_section(b, d)
        f3 = f(c)

        print('iter: %d' % iterations, 'b: %f' % b)
        
        if f2 < f3:
            d = c
            f4 = f3
            tolerance = abs(f3 - f1)
            golden_section_interval_reduction((a, b, d), f, (f1, f2, f4), tolerance, iterations+1, iter_max, min_tolerance)
        
        elif f2 > f3 :
            a = b
            b = c
            f1 = f2
            f2 = f3
            tolerance = abs(f2 - f4)
            golden_section_interval_reduction((a, b, d), f, (f1, f2, f4), tolerance, iterations+1, iter_max, min_tolerance)
            
        elif f2 == f3:
            d = c
            f4 = f3
            tolerance = abs(f3 - f1)
            golden_section_interval_reduction((a, b, d), f, (f1, f2, f4), tolerance, iterations+1, iter_max, min_tolerance)

    return b
    
def test_function(x):
    return (x-10)**2

def gradient_descent(z_initial, f, tolerance = 50, max_iter = 100000, alpha = 0.1):
    """ Carry out steepest descent to find minimum of a unimodal R^1 function 
    gradient_descent(z_initial, f , tolerance = 50, max_iter = 100000, alpha = 0.1)
    z_initial    : inital search postion
    f            : function to find minimum of 
    tolerance    : difference of function evaluations in each iteration
    max_iter     : maximum no: of iterations
    alpha        : learning rate
    """
       
    # Initial calculations
    delta_z = -alpha
    z = z_initial + delta_z
    f_current = f(z_initial)
    f_next = f(z)
    gradient = (f_next - f_current)/alpha
    converged = False
    iterations = 1
    
    # Steepest descent
    while (not converged and max_iter > iterations):
        delta_z = -alpha * gradient
        z = z + delta_z   # update search position
        f_previous = f_current      # update search history
        f_nearby = f(z+alpha)       # check nearby position to evaluate greadient
        f_current = f(z)            # update current search value
        gradient = (f_nearby - f_current)/alpha     # calculate approx. gradient 
        iterations += 1             # update no of iterations
        
        if abs(f_current-f_previous)<tolerance:
            print ('Reached minimum tolerance')
            converged = True
        elif iterations>max_iter:
            print('Reached max no: of iterations')
     
    # Return results
    print('Minimum at z = %f' % z)
    return z
    
class microscope:
    """ Microscope class to control motors and read images """

    def __init__(self):
        pass
        
    def motor(self, steps):
        """ Control motors via the web and return image """
        #return I
        pass
            
    def focus(self, steps, function):
        """ Get focus score """
        img = self.motor(steps) # read image I at motor 
        return function(img) # Calculate focus score
    
 

    
if __name__ == '__main__':
    a = -5
    d = 10
    #b = golden_section(a,d)
    #x = golden_section_interval_reduction((a, b , d), test_function, (test_function(a), test_function(b), test_function(d)), min_tolerance = 0.5)
    
    x = gradient_descent (5, test_function, tolerance = 0.001, alpha = 0.1)
        
# htttps://172.29.9.20:9000/_webshell/control/motor/2/50
     