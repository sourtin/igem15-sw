import numpy as np
import dwt
import urllib.request
import ssl
import cv2
import time


def test_function(x):
    return (x-2)**2
  

    """ Return the Nth fibonacci number
        Using the formula from Wikipidea article on Fibonacci_number
    """ 
    
    phi = (1 + 5 ** 0.5)/2 # Golden ratio
    return int((phi**n - (-phi)**(-n))/(5 ** 0.5))
  
def fibonacci_search(interval, f ):
    """ Carry out the fibonacci search method according* to the paper:
        'Autofocusing for tissue microscopy' by T.T.E.Yeo et al
        
        fibonacci_search(interval, f)
        interval = (a, b)
        f is the microscope control class
        
        
        * The paper made two mistakes, the evaluations should be if (y1 > y2) not the other way round 
        """

    # ################### Functions #######################
    
    phi = 0.5 * (1 + 5 ** 0.5) # Golden ratio
    
    def fibs(n=None):
        """ A generator, (thanks to W.J.Earley) that returns the fibonacci series """
        a, b = 0, 1
        yield 0
        yield 1
        if n is not None:
            for _ in range(1,n):
                b = b + a
                a = b - a
                yield(b)
        else:
            while True:
                b = b + a
                a = b - a
                yield(b)
            
    def smallfib(m):
        """ Return N such that fib(N) >= m """
        n = 0
        for fib in fibs(m):
            if fib >= m:
                return n
            n = n + 1

    def fib(n):
        """ Evaluate the n'th fibonacci number """
        return (phi ** n - (-phi) ** (-n))/(5 ** 0.5)

    # ################# Fibonacci search #########################
    a = interval[0]
    b = interval[1]
    N = smallfib(b-a)
    delta = (fib(N-2)/fib(N))*(b-a)
        
    x1 = a + delta
    x2 = b - delta
    y1 = f(x1)
    y2 = f(x2)
           
    for n in range(N-1, 1, -1):
        #print ((x1,x2),(a,b))
        if y1 > y2 :
            a = x1
            x1 = x2
            y1 = y2
            x2 = b - (fib(n-2)/fib(n))*(b-a)
            y2 = f(x2)
        else:
            b = x2
            x2 = x1
            y2 = y1
            x1 = a + (fib(n-2)/fib(n))*(b-a)
            y1 = f(x1)
    
    if y1 < y2:
        return x1
    else:
        return x2

def gaussian_fitting(z , f):
    """Fit the autofocus function data according to the equation 16.5 in the 
        textbook : 'Microscope Image Processing' by Q.Wu et al'
        gaussian_fitting((z1, z2, z3), (f1, f2 f3))
        where z1, z2 , z3 are points where the autofocus functions 
        values f1, f2, f3 are measured """
        
    z1 = z[0];z2 = z[1];z3 = z[2];    
    f1 = f[0];f2 = f[1];f3 = f[2];
    
    B = (np.log(f2) - np.log(f1))/(np.log(f3) - np.log(f2))
    
    if (z3 - z2)==(z2 - z1):
        return 0.5 * (B * (z3 + z2) - (z2 + z1))/(B-1)
    else:
        return 0.5 * (B * (z3**2 - z2**2) - (z2**2 - z1**2))/(B * (z3 - z2) - (z2 - z1))

def parabola_fitting(z , f):
    """Fit the autofocus function data according to the equation 16.5 in the 
        textbook : 'Microscope Image Processing' by Q.Wu et al'
        parabola_fitting((z1, z2, z3), (f1, f2 f3))
        where z1, z2 , z3 are points where the autofocus functions 
        values f1, f2, f3 are measured """
            
    z1 = z[0];z2 = z[1];z3 = z[2];    
    f1 = f[0];f2 = f[1];f3 = f[2];
    
    E = (f2 - f1)/(f3 - f2)
    
    if (z3 - z2) == (z2 - z1):
        return 0.5 * (E * (z3 + z2) - (z2 + z1))/(E - 1)
    else:
        return 0.5 * (E * (z3 ** 2 - z2 ** 2) - (z2 ** 2 - z1 ** 2))/(E * (z3 - z2) - (z2 - z1))
             
    
    

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
        # top_level_url = 'https://192.168.0.1:9000/'
        pmgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        pmgr.add_password(None, top_level_url, username, password)
        handler = urllib.request.HTTPBasicAuthHandler(pmgr)
        opener = urllib.request.build_opener(https_handler, handler)
        opener.open(top_level_url)
        urllib.request.install_opener(opener)
        #pagehandle = urllib.request.urlopen(theurl)
        #print(pagehandle.read())
        
    def move_motor(self,steps,pause = None, axis = 2):
        """ Control motors 
            move_motor(steps, pause = False, axis = 2)
            steps : number of steps for the motor to move
            pause : wait after moving motor? 
            axis  : 0 = x, 1 = y, 2 = z
            """
        if abs(steps)>=100:
            pagehandle = urllib.request.urlopen('https://172.29.9.20:9000/_webshell/control/motor/%d/%d' %(axis, steps))
            if (pause != None):
                time.sleep(pause)
                
            # pagehandle = urllib.request.urlopen('https://192.168.0.1:9000/_webshell/control/motor/%d/%d' %(axis, steps))
        else:
            pagehandle = urllib.request.urlopen('https://172.29.9.20:9000/_webshell/control/motor/%d/%d' %(axis, steps + 300))
            time.sleep(1)
            pagehandle = urllib.request.urlopen('https://172.29.9.20:9000/_webshell/control/motor/%d/%d' %(axis, - 300))
            if (pause != None):
                time.sleep(pause)
        
        #print(pagehandle.read())
        print('Moving %d' %steps)
        #time.sleep(10)
        return self
        
    def get_image(self):
        """Return image captured"""
        
        uro = urllib.request.urlopen('https://172.29.9.20:9000/_stream/?action=snapshot') # When Pi is connected to the internet
        # uro = urllib.request.urlopen('https://192.168.0.1:9000/_stream/?action=snapshot')   # When connected to Pi
        # uro = urllib.request.urlopen('https://192.168.0.1:9000/_stream/?action=stream')
        
        
        raw = uro.read()
        # print (raw)
        nparr = np.fromstring(raw, np.uint8)
        img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
    
    def focus_score(self, image):
        """ Return -1*variance(image)"""
        #return -1*dwt.focus_score(self.get_image())
        #a = dwt.nleveldwt(3,self.get_image())
        #return -1*dwt.focus_score(a)
        #return -1*dwt.focus_score(self.get_image())
        return -1*np.var(image)
        
    
    

if __name__ == "__main__":
    #print(smallfib(50))
    x = fibonacci_search((-5, 10), test_function)
    print(x)