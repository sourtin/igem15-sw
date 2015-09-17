import numpy as np
import matplotlib.pyplot as plt
#import dwt
import urllib.request
import ssl
import cv2
import time

score_history = []

def test_function(x):
    return (x-1)**2

def plot_score(f, points = 10):
    imgs = []
    score = []
    #f.move_motor()

    for i in range(points):
        f.move_motor(200, pause = 1)
        imgs.append(f.get_image())
        #time.sleep(2)
    
    for i in imgs:
        score.append(f.focus_score(i))
        #print(score)
        
    plt.plot(range(len(score)),score)
    plt.ylabel('Variance')
    plt.xlabel('Position')
    plt.title('Focus score varying with position')
    plt.show()

def gaussian_fitting(z , f):
    """Fit the autofocus function data according to the equation 16.5 in the 
        textbook : 'Microscope Image Processing' by Q.Wu et al'
        z_max = gaussian_fitting((z1, z2, z3), (f1, f2 f3))
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
        
def old_fibonacci_search(interval, f ):
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
        
def fibonacci_search(interval, f ):
    """ Carry out the fibonacci search method according* to the paper:
        'Autofocusing for tissue microscopy' by T.T.E.Yeo et al
        
        (a,b,x) = fibonacci_search(interval, f)
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
    print('Starting Fibonacci search')
    a = interval[0]
    b = interval[1]
    c = np.mean((a,b))
    N = smallfib(int(b-a))
    delta = (fib(N-2)/fib(N))*(b-a)
        
    x1 = a + delta
    x2 = b - delta
    y1 = f.move_motor(x1-c,2).eval_score()
    y2 = f.move_motor(x2-x1,2).eval_score()
    score_history.append(y1)
    score_history.append(y2)
    curr_pos = x2
              
    for n in range(N-1, 1, -1):
        print ('Interval is (%f, %f)' % (a,b) )
        if (abs(a-b) <=20):
            print(a, b)
            print('Bye')
            return (a,b,x1)
        elif y1 > y2 :
            a = x1
            x1 = x2
            y1 = y2
            x2 = b - (fib(n-2)/fib(n))*(b-a)
            y2 = f.move_motor(x2-curr_pos,2).eval_score()
            score_history.append(y2)
            curr_pos = x2
        else:
            b = x2
            x2 = x1
            y2 = y1
            x1 = a + (fib(n-2)/fib(n))*(b-a)
            y1 = f.move_motor(x1-curr_pos, 2).eval_score()
            score_history.append(y1)
            curr_pos = x1
    
    if y1 < y2:
        print('Max at %f' %x1)
        #f.move_motor(x1 - curr_pos, 6).eval_score()
        return (a,b,x1)
    else:
        print('Max at %f' %x2)
        #f.move_motor(x2 - curr_pos, 6).eval_score()
        return (a,b,x2)
     
        
class microscope_control:
    """ Microscope class to control motors and read images """

    def __init__(self, connection = 0):
        """ Set up HTTP request stuff 
        Connected to internet : connection = 0
        Connected to OpenScope: connection = 1
        """
        username = 'admin'
        password = 'test'

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode  = ssl.CERT_NONE
        https_handler = urllib.request.HTTPSHandler(context=ctx)

        # Set the urls
        if connection == 0:
            top_level_url = 'https://172.29.9.20:9000/' # Connected to internet           
        elif connection == 1:

            top_level_url = 'https://192.168.0.1:9000/' # Connected to OpenScope
        else:
            raise Exception(' connection = 0 for internet, 1 for OpenScope')
        self.motor_url_request = top_level_url + '_webshell/control/motor/%d/%d'
        self.img_url_request = top_level_url + '_stream/?action=snapshot'
        
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
        print('Moving %d' %steps)
        if abs(steps)>=100:
            #pagehandle = urllib.request.urlopen('https://172.29.9.20:9000/_webshell/control/motor/%d/%d' %(axis, steps))
            #pagehandle = urllib.request.urlopen('https://192.168.0.1:9000/_webshell/control/motor/%d/%d' %(axis, steps))
            pagehandle = urllib.request.urlopen(self.motor_url_request %(axis, steps))
            
            if (pause != None):
                time.sleep(pause)
                
            # pagehandle = urllib.request.urlopen('https://192.168.0.1:9000/_webshell/control/motor/%d/%d' %(axis, steps))
        elif steps != 0:
            print('Moving up then down')
            pagehandle = urllib.request.urlopen(self.motor_url_request %(axis, steps + 300))
            time.sleep(2)
            pagehandle = urllib.request.urlopen(self.motor_url_request%(axis, - 300))
            if (pause != None):
                time.sleep(pause)
        else :
            pass
        
        #print(pagehandle.read())
        
        #time.sleep(10)
        return self
        
    def get_image(self):
        """Return image captured"""
        
        uro = urllib.request.urlopen(self.img_url_request)
        # When Pi is connected to the internet
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
        return np.var(image)
    
    def eval_score(self):
        return self.focus_score(self.get_image())

def hill_climbing(f, step_size = 500):
    """ Climb to a higher place, find a smaller interval containing focus position
    (z1, z2, z3),(f1, f2, f3) = hill_climbing(f)
    
    """
    
    f1 = f.eval_score()
    z1 = 0
    f2 = f.move_motor(step_size, 1).eval_score()
    z2 = step_size
    score_history.append(f1)
    score_history.append(f2)
    
    while(1):
        print(f1,f2)
        if(f2 > f1):
            f0 = f1
            f1 = f2
            f2 = f.move_motor(step_size,1).eval_score()
            score_history.append(f2)
            z2 += step_size
        else:
            print ('Finised hill climbing') 
            return ((z2 - 2 * step_size -2 , z2 - step_size, z2), (f0, f1, f2))
        
  
    
                
def old_test_autofocus():
    # Get 3 points that encompass the focused position
    # I am assuming that the microscope starts below focus and then moves up
    # the middle value must be bigger than either of the endpoints
    m = microscope_control()
    z1 = 0
    print('Evaluating f1')
    f1 = m.eval_score()
    z2 = 500
    print('Evaluating f2')
    f2 = m.move_motor(z2, 5).eval_score()
    while(True):
        if f2 < f1:
            f2 = m.move_motor(200, 5).eval_score()
            z2 += 200
        else :
            break
    z3 = z2 + 500
    print('Evaluating f3')
    f3 = m.move_motor(500, 5).eval_score()
    while(True):
        if f2 < f3:
            f3 = m.move_motor(200, 5).eval_score()
            z3 += 200
        else :
            break
    
    #print(f1, f2, f3)
    
    # Gaussian prediction
    print('Gaussian fitting')
    mu = gaussian_fitting((z1, z2, z3), (f1, f2, f3))
    
    #print(mu)
    # Move motor to predicted position from z3
    m.move_motor(mu-z3)
    
def test_z_axis_repeatability():
    m = microscope_control()
    scores = []
    distance = 500
    for i in range(50):
        print('Iteration % d' % i)
        m.move_motor(distance, 5)
        m.move_motor(-distance, 5)
        #scores.append(m.move_motor(-distance, 5).eval_score())
        scores.append(m.eval_score())
        
    
    plt.plot(range(len(scores)),scores)
    plt.ylabel('Variance')
    plt.xlabel('Iteration')
    plt.title('Focus score varying repeated movements')
    plt.show()      
    
def test_autofocus():
    global score_history
    start_time = time.time()
    
    score_history = [] # Clear history
    m = microscope_control()
    
    # Find small interval containing focus position
    z,f = hill_climbing(m)
    
    # Gaussian prediction
    mu = gaussian_fitting(z,f)
    print('Moving to predicted position: %f' %mu)
    m.move_motor(-z[2]+mu, 1)
    score_history.append(m.eval_score())
    print('Prediction Score : %f' % score_history[-1])
    interval = (mu-500, mu, mu +500)
    
    # Fibonacci search
    (a,b,x) = fibonacci_search(interval, m)
    print('Interval: (%f, %f, %f)' %(a,x,b) )
    
    # # Parabola prediction
    mu = parabola_fitting((a,x,b), (score_history[-2],score_history[-1],score_history[-3]))
    print ('Moving to predicted position: %f' % mu)
    m.move_motor(-x+mu)
    score_history.append(m.eval_score())
    # print('Can you plaese do so manually?')
    
    end_time = time.time()
    print('Time takes is %f' %(end_time-start_time))
    return(score_history)
    
    
    
if __name__ == '__main__':
    #m = microscope_control()
    # plot_score(m)
    # z1 = -5; z2 = 5; z3 = 10;
    # f = test_function;
    # x = gaussian_fitting((z1, z2, z3), (f(z1), f(z2), f(z3)))
    # print(x)
    # x = parabola_fitting((z1, z2, z3), (f(z1), f(z2), f(z3)))
    # print(x)
    #test_autofocus()
    
    # ###########################################################33
    #m = microscope_control()
    #z, f = hill_climbing(m)
    # mu = gaussian_fitting(z,f)
    # print(z , f)
    # print('Moving to predicted position: %f' %mu)
    # m.move_motor(-z[2]+mu, 8)
    # print('Final Score : %f' % m.eval_score())
    # ###############################################################
    #fibonacci_search((z[0],z[1]), m)
    
    # ########### Testing repeatability of microscope #############
    #test_z_axis_repeatability()
    history = test_autofocus()
    
        