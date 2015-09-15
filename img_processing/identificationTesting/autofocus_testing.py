# autofocus
# Rememer that the microscope classes does -1*focus score 

import numpy as np
import dwt
import urllib.request
import ssl
import cv2
import time

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
    
def golden_section_interval_reduction(interval, f, min_tolerance = 5, max_iter = 10000):
    """ Carry out golden section interval reduction 
        interval is a tuple (a, d) 
        f is the function 
    """
    a = interval[0]
    d = interval[1]
    b = golden_section(a,d)
    
    f1 = f(a)
    f2 = f(b)
    f3 = f(c)
    
    tolerance = f3-f1
    iterations = 1
    
    while(min_tolerance < tolerance or max_iter > iterations):
        c = golden_section(b,d)
        f2 = f(c)

        print('iter: %d' % iterations, 'b: %f' % b)
        
        if f2 < f3:
            d = c
            f4 = f3
            tolerance = abs(f3 - f1)
            
        elif f2 > f3 :
            a = b
            b = c
            f1 = f2
            f2 = f3
            tolerance = abs(f2 - f4)
            
        elif f2 == f3:
            d = c
            f4 = f3
            tolerance = abs(f3 - f1)
       
        iterations += 1
        if max_iter < iterations :
            print ("Max iterations reached \n Minimum at %f" % b)
        if tolerance < min_tolerance:
            print ("Min tolerance reached \n Minimum at %f" % b)
        
    return b    
            
def old_golden_section_interval_reduction(interval, f, finterval,  tolerance = 50, iterations = 0, iter_max = 1000, min_tolerance = 5):
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

def older_gradient_descent(z_initial, f, tolerance = 50, max_iter = 100000, alpha = 0.1):
    """ Carry out steepest descent to find minimum of a unimodal R^1 function 
    gradient_descent(z_initial, f , tolerance = 50, max_iter = 100000, alpha = 0.1)
    z_initial    : inital search postion
    f            : function to find minimum of 
    tolerance    : difference of function evaluations in each iteration
    max_iter     : maximum no: of iterations
    alpha        : learning rate
    """
       
    # Initial calculations
    #f = -1*f
    delta_z = -alpha
    z = z_initial + 5
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
        print('Score :%f' % f_current)
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

    """ Carry out steepest descent to find minimum of a unimodal R^1 function 
    gradient_descent(z_initial, f , tolerance = 50, max_iter = 100000, alpha = 0.1)
    z_initial    : inital search postion
    f            : function (microscope class) to find minimum of 
    tolerance    : difference of function evaluations in each iteration
    max_iter     : maximum no: of iterations
    alpha        : learning rate
    """
       
    # Initial calculations
    #f = -1*f
    delta_z = -alpha
    z = z_initial + 5
    f_current = f.focus()
    f_next = f.move_motor(z).focus()
    gradient = (f_next - f_current)/alpha
    converged = False
    iterations = 1
    
    # Steepest descent
    while (not converged and max_iter > iterations):
        delta_z = -alpha * gradient
        z = z + delta_z   # update search position
        f_previous = f_current      # update search history
        f_nearby = f.move_motor(alpha).focus()       # check nearby position to evaluate greadient
        f_current = f.move_motor(delta_z).focus()           # update current search value
        print('Score :%f' % f_current)
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

def gradient_descent(z_initial, f, tolerance = 50, max_iter = 100000, alpha = 5):
    """ Carry out steepest descent to find minimum of a unimodal R^1 function 
    gradient_descent(z_initial, f , tolerance = 50, max_iter = 100000, alpha = 0.1)
    z_initial    : inital search postion
    f            : function (microscope class) to find minimum of 
    tolerance    : difference of function evaluations in each iteration
    max_iter     : maximum no: of iterations
    alpha        : learning rate
    """
       
    # Initial calculations
    #f = -1*f
    delta_z = -alpha
    z = z_initial + 5
    f_current = f.focus()
    f_next = f.move_motor(z).focus()
    gradient = (f_next - f_current)/alpha
    converged = False
    iterations = 1
    
    # Steepest descent
    while (not converged and max_iter > iterations):
        delta_z = -alpha * gradient
        z = z + delta_z   # update search position
        f_previous = f_current      # update search history
        f_nearby = f.move_motor(alpha).focus()       # check nearby position to evaluate greadient
        f_current = f.move_motor(delta_z).focus()           # update current search value
        print('Score :%f' % f_current)
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
        
class microscope_control:
    """ Microscope class to control motors and read images """

    def __init__(self):
        """ Set up HTTP request stuff """
        username = 'admin'
        password = 'test'
        #theurl = 'https://172.29.9.20:9000/_webshell/control/motor/%d/%d' % (2,0)

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode  = ssl.CERT_NONE
        https_handler = urllib.request.HTTPSHandler(context=ctx)

        top_level_url = 'https://172.29.9.20:9000/'
        pmgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        pmgr.add_password(None, top_level_url, username, password)
        handler = urllib.request.HTTPBasicAuthHandler(pmgr)
        opener = urllib.request.build_opener(https_handler, handler)
        opener.open(top_level_url)
        urllib.request.install_opener(opener)
        #pagehandle = urllib.request.urlopen(theurl)
        #print(pagehandle.read())
        
    def move_motor(self,steps,axis = 2):
        """ Control motos """
        pagehandle = urllib.request.urlopen('https://172.29.9.20:9000/_webshell/control/motor/%d/%d' %(axis, steps))
        #print(pagehandle.read())
        print('Motor %d move %d' %(axis,steps))
        time.sleep(2)
        return self
        
    def get_image(self):
        """ Control motors via the web and return image """
        # pagehandle = urllib.request.urlopen('https://172.29.9.20:9000/_webshell/control/motor/%d/%d' %(axis, steps))
        # #print(pagehandle.read())
        # print('Motor %d move %d' %(axis,steps))
        # time.sleep(15)
        uro = urllib.request.urlopen('https://172.29.9.20:9000/_stream/?action=snapshot')
        raw = uro.read()
        nparr = np.fromstring(raw, np.uint8)
        img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
    
    def focus(self):
        """ Return focus score """
        return -1*dwt.focus_score(self.get_image())
        
 

    
if __name__ == '__main__':
    # a = -5
    # d = 10
    #b = golden_section(a,d)
    #x = golden_section_interval_reduction((a, b , d), test_function, (test_function(a), test_function(b), test_function(d)), min_tolerance = 0.5)
    
    #x = gradient_descent (5, test_function, tolerance = 0.001, alpha = 0.1)
    m = microscope_control()
    gradient_descent(0,m)
     
