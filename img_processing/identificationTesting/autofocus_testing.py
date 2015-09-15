# autofocus
# Rememer that the microscope class does -1*focus_score 

import numpy as np
import dwt
import urllib.request
import ssl
import cv2
import time
    
def new_golden_section(A,D):
    """ Return delta_x which is in golden ration with the interval input """
    golden = (1 + 5 ** 0.5) / 2     # Golden ratio
    d = abs(D-A)
    delta_x = d * (1 - 1/golden)
    
    return delta_x 
    
def old_golden_section_interval_reduction(interval, f, min_tolerance = 5, max_iter = 10000):
    """ Carry out golden section interval reduction 
        interval is (a, d) 
        f is the function 
    """
    a = interval[0]
    d = interval[1]
    b = a + new_golden_section(a,d)
    c = d - new_golden_section(a,d)
    
    f1 = f(a)
    f2 = f(b)
    f3 = f(c)
    f4 = f(d)
        
    tolerance = f4-f1
    iterations = 1

    while(min_tolerance < tolerance and max_iter > iterations):

        #print('iter: %d' % iterations, '(%f,%f,%f,%f)' % (a,b,c,d))
        
        if f2 <= f3:
            d = c
            c = b
            b = a + new_golden_section(a,d)
            f4 = f3
            f3 = f2
            f2 = f(b)
            
        elif f2 > f3 :
            a = b
            b = c
            c = d - new_golden_section(a,d)
            f1 = f2
            f2 = f3
            f3 = f(c)
       
        iterations += 1
        tolerance = abs(f4 - f1)
        #time.sleep(1)
        
        if max_iter <= iterations :
            print ("Max iterations reached \n Minimum at %f" % b)
        if tolerance <= min_tolerance:
            print ("Min tolerance reached \n Minimum at %f" % b)
        
    return (a, b, c, d)

def golden_section_interval_reduction(interval, f, min_tolerance = 5, max_iter = 10000):
    """ Carry out golden section interval reduction 
        interval is (a, d) 
        f is the microscope class focus function 
        Assumes that the microscope is in position (a) at the start 
    """
    a = interval[0]
    d = interval[1]
    delta_x = new_golden_section(a,d)
    b = a + delta_x
    c = d - delta_x
    
    f1 = f.move_motor(a).focus()
    f2 = f.move_motor(delta_x).focus()
    f3 = f.move_motor(b-c).focus()
    f4 = f.move_motor(delta_x).focus()
    # motor_positions : a  b  c  d 
    #                   0  1  2  3
    motor_position = 3
        
    tolerance = f4-f1
    iterations = 1

    while(min_tolerance < tolerance and max_iter > iterations):

        #print('iter: %d' % iterations, '(%f,%f,%f,%f)' % (a,b,c,d))
        
        curr_range = (a,b,c,d)
        
        
        if f2 <= f3:
            # Update interval 
            d = c
            c = b
            delta_x = new_golden_section(a,d)
            b = a + delta_x
            f4 = f3
            f3 = f2
            
            # Move motor to position 'b' depending on current position
            if motor_position != 0 :
                f2 = f.move_motor(b - curr_range[motor_position]).focus()
            elif motor_position == 0:
                f2 = f.move_motor(delta_x).focus()
            else:
                raise Exception('Motor position lost. Current position is:' , motor_position)
            
            motor_position = 1    # update motor position to 'b'
            
        elif f2 > f3 :
            # Update interval
            a = b
            b = c
            delta_x = new_golden_section(a,d)
            c = d - delta_x
            f1 = f2
            f2 = f3
            
            # Move motor to position 'b' depending on current position
            if motor_position != 3:
                f3 = f.move_motor(curr_range[3] - curr_range[motor_position]- delta_x).focus()
            elif motor_position == 1:
                f3 = f.move_motor(-1*delta_x).focus()
            else:
                raise Exception('Motor position lost. Current position is:', motor_position)
            
            motor_position = 2    # update motor position 
            
            #f3 = f(c) # need to think about how to move motors
       
        iterations += 1
        tolerance = abs(f4 - f1)
        #time.sleep(1)
        
        if max_iter <= iterations :
            print ("Max iterations reached \n Minimum at %f" % b)
        if tolerance <= min_tolerance:
            print ("Min tolerance reached \n Minimum at %f" % b)
        
    return (a, b, c, d)    
   
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
        
        if abs(f_current-f_previous)<=tolerance:
            print ('Reached minimum tolerance')
            converged = True
        elif iterations>=max_iter:
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
    
    # a = -6; b = 40; 
    # x = golden_section_interval_reduction((a,b), test_function, min_tolerance = 0.01)
    # print(x)
    
    # ################# Testing the autofocus ##################3
    m = microscope_control()
    # gradient_descent(0,m)
    golden_section_interval_reduction(interval, m, min_tolerance = 100, max_iter = 1000): 
