# Carries out an autofocus algorithm from the textbook
#  Microscope Image Processing by Qiang Wu (2008)
# The implementation below is from section 16.3.3 (DWT is unstested and commented out)
# 'Multiresolution Search for In-Focus Position'


from hw.ledmotorcontrol import driver
import numpy as np
#import matplotlib.pyplot as plt
#import dwt
import requests
import ssl
import cv2
import time

score_history = []


def low_res_score(IMAGE):

    def dwt(X, h1 = np.array([-1, 2, 6, 2, -1])/8 , h2 = np.array([-1, 2 -1])/4):
        """ 
        From 3rd year engineering project SF2
        DWT Discrete Wavelet Transform 
        Y = dwt(X, h1, h2) returns a 1-level 2-D discrete wavelet
        transform of X.
        
        If filters h1 and h2 are given, then they are used, 
        otherwise the LeGall filter pair are used.
        """
        m = X.shape[0] # no: of rows in image X
        n = X.shape[1] # no: of columns in image X
        Y = np.zeros((m,n))
        #print('Output image is of shape ',Y.shape)

        n2 = int(n/2)
        t = np.array(range(n2))
        #print('Editing this part of Y: ',Y[:,t].shape)
        #print(X.shape, h1.shape)
        
        Y[:,t] = rowdec(X, h1)
        Y[:,t+n2] = rowdec2(X, h2)

        X = Y.T
        m2 = int(m/2)
        t = np.array(range(m2))
        # print(Y[t,:].shape)
        # print(X.shape)
        Y[t,:] = rowdec(X, h1).T
        Y[t+m2, :] = rowdec2(X, h2).T
        return Y
        
    def rowdec(X, h):
        """"
        ROWDEC Decimate rows of a matrix
        Y = ROWDEC(X, H) Filters the rows of image X using H, and
        decimates them by a factor of 2.
        If length(H) is odd, each output sample is aligned with the first of
        each pair of input samples.
        If length(H) is even, each output sample is aligned with the mid point
        of each pair of input samples.
        """
        c = X.shape[1]
        r = X.shape[0]
        m = h.size
        m2 = int(m/2)
          
        if np.remainder(m,2)>0:
            # Odd h: symmetrically extend indices without repeating end samples.
            xe = np.array([x for y in [range(m2, 0, -1), range(c), range(c-2,c-m2-2, -1)]  for x in y])
        else:
            # Even h: symmetrically extend with repeat of end samples.
            xe = np.array([x for y in [range(m2,-1,-1), range(c+1), range(c-1,c-m2-2,-1)] for x in y])
        
        t = np.array(range(0, c-1, 2))
       
        Y = np.zeros((r, t.size))
        # Loop for each term in h.
        for i in range(m):
            Y = Y + h[i] * X[:,xe[t+i]];
            
        return Y
        
    def rowdec2(X, h):
        """"
        ROWDEC2 Decimate rows of a matrix
        Y = ROWDEC2(X, H) Filters the rows of image X using H, and
        decimates them by a factor of 2.
        If length(H) is odd, each output sample is aligned with the first of
        each pair of input samples.
        If length(H) is even, each output sample is aligned with the mid point
        of each pair of input samples.
        """
        c = X.shape[1]
        r = X.shape[0]
        m = h.size
        m2 = int(m/2)
        
        if np.remainder(m,2)>0:
            # Odd h: symmetrically extend indices without repeating end samples.
            xe = np.array([x for y in [range(m2, 0, -1), range(c), range(c-2,c-m2-2, -1)]  for x in y])
        else:
            # Even h: symmetrically extend with repeat of end samples.
            xe = np.array([x for y in [range(m2,-1,-1), range(c+1), range(c-1,c-m2-2,-1)] for x in y])
        
        t = np.array(range(1, c, 2))
        
        Y = np.zeros((r, t.size))
        # Loop for each term in h.
        for i in range(m):
            Y = Y + h[i] * X[:,xe[t+i]];
        
        return Y

    def nleveldwt(X, N = 3):
        """ N level DWT of image
        Returns an array of the smaller resolution images
        """
        #print('N = ', N)
        Xs = [X]
        if N > 0:
            h, w = X.shape[:2]
            Xs += nleveldwt( dwt(X)[:h//2, :w//2], N-1)
        return Xs
        
    def focus_score(X):
        """ Focus score is the sum of the squared values of the low resolution images.
        """
        score = 0
        for i in X:
            i += 1
            score += np.var(i)
        return score
     
    return focus_score(nleveldwt(IMAGE))
     

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
    c = np.mean((a,b)) # current position of z is inbetween the interval
    N = smallfib(int(b-a))
    delta = (fib(N-2)/fib(N))*(b-a)
        
    x1 = a + delta
    x2 = b - delta
    y1 = f.move_motor(x1-c,1).eval_score()
    y2 = f.move_motor(x2-x1,1).eval_score()
    score_history.append(y1)
    score_history.append(y2)
    older_pos = 0
    old_pos = x1
    curr_pos = x2
    iterations = 1
              
    for n in range(N-1, 1, -1):
        #print ('Interval is (%f, %f)' % (a,b) )
        # if (abs(a-b) <=20):
            # print(a, b)
            # print('Bye')
            # return (a,b,x1)
        if iterations >5: # Only 5 iterations for speed
            break
        elif y1 < y2 :
            a = x1
            x1 = x2
            y1 = y2
            x2 = b - (fib(n-2)/fib(n))*(b-a)
            y2 = f.move_motor(x2-curr_pos,2).eval_score()
            score_history.append(y2)
            #print ('Score: ',y2)
            older_pos = old_pos
            old_pose = curr_pos
            curr_pos = x2
        else:
            b = x2
            x2 = x1
            y2 = y1
            x1 = a + (fib(n-2)/fib(n))*(b-a)
            y1 = f.move_motor(x1-curr_pos, 2).eval_score()
            score_history.append(y1)
            #print('Score: ',y1)
            older_pos = old_pos
            old_pos = curr_pos
            curr_pos = x1
        iterations += 1
    
    if y1 > y2:
        print('Finished Fibonacci search') #(Limited to 5 iterations) \n Max at %f' %x1)
        #f.move_motor(x1 - curr_pos, 6).eval_score()
        return (a,b,x1, older_pos, old_pos, curr_pos)
    else:
        print('Finished Fibonacci search')# (Limited to 5 iterations) \n Max at %f' %x2)
        #f.move_motor(x2 - curr_pos, 6).eval_score()
        return (a,b,x2, older_pos, old_pos, curr_pos)
     
        
class microscope_control:
    """ Microscope class to control motors and read images """

    def __init__(self, timeout=None):
        """ Set up HTTP request stuff """
        self.begin = time.time()
        self.timeout = timeout

        # Set the urls
        self.motor_url_request = 'http://127.0.0.1:9001/control/motor/%d/%d'
        self.img_url_request = 'http://127.0.0.1:9002/?action=snapshot'
        
        #pagehandle = urllib.request.urlopen(theurl)
        #print(pagehandle.read())

    def check_time(self):
        if self.timeout is not None:
            if time.time() - self.begin > self.timeout:
                raise Exception("timed out")
        
    def move_motor(self,steps,pause = None, axis = 2):
        """ Control motors 
            move_motor(steps, pause = False, axis = 2)
            steps : number of steps for the motor to move
            pause : wait after moving motor? 
            axis  : 0 = x, 1 = y, 2 = z
            """
        self.check_time()

        #print('Moving %d' %steps)
        if abs(steps)>=100:
            #pagehandle = urllib.request.urlopen('https://172.29.9.20:9000/_webshell/control/motor/%d/%d' %(axis, steps))
            #pagehandle = urllib.request.urlopen('https://192.168.0.1:9000/_webshell/control/motor/%d/%d' %(axis, steps))
            driver.move_motor(axis, steps)
            
            if (pause != None):
                time.sleep(pause)
                
            # pagehandle = urllib.request.urlopen('https://192.168.0.1:9000/_webshell/control/motor/%d/%d' %(axis, steps))
        elif steps != 0:
            #print('Moving up then down')
            driver.move_motor(axis, steps + 300)
            time.sleep(2)
            driver.move_motor(axis, -300)
            if (pause != None):
                time.sleep(pause)
        else :
            pass
        
        #print(pagehandle.read())
        
        #time.sleep(10)
        return self
        
    def get_image(self):
        """Return image captured"""
        self.check_time()
        
        raw = requests.get(self.img_url_request).content
        # When Pi is connected to the internet
        # uro = urllib.request.urlopen('https://192.168.0.1:9000/_stream/?action=snapshot')   # When connected to Pi
        # uro = urllib.request.urlopen('https://192.168.0.1:9000/_stream/?action=stream')
        
        
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
        self.check_time()
        return np.var(image)
    
    def eval_score(self):
        self.check_time()
        return self.focus_score(self.get_image())

# moosd's simple autofocus search implementation
def naive_autofocus(f, step_size = 500):
    print("Is simple better?")
    prev = f.eval_score()    

    f.move_motor(step_size, 1)
    time.sleep(1)
    curr = f.eval_score()
    print(prev)
    print(curr)

    # check direction to climb
    diff = curr - prev
    direction = 1 if diff > 0 else -1

    # climb in smaller increments until theshold
    step_thresh = 150

    # for sanity
    timeout = 100
    tprogress = 0

    # climb, baby, climb!
    while step_size > step_thresh:
        while tprogress < timeout:
            prev = curr
            f.move_motor(direction * step_size, 1)
            time.sleep(1)
            curr = f.eval_score()
            print(curr)
            if curr > 1000:
                print("tres focused")
                return

            diff = curr - prev
            curdir = 1 if diff > 0 else -1
            direction = curdir * direction
            if curdir == -1:
                print("back back back")
                break
            tprogress = tprogress + 1
        tprogress = 0
        step_size = step_size / 2

    print("Done naive hill climb")

def hill_climbing(f, step_size = 500):
    """ Climb to a higher place, find a smaller interval containing focus position
    (z1, z2, z3),(f1, f2, f3) = hill_climbing(f)
    
    """
    global scan_direction
    print('Starting hill climbing')
    f1 = f.eval_score()
    z1 = 0
    f2 = f.move_motor(step_size, 1).eval_score()
    z2 = step_size
    score_history.append(f1)
    score_history.append(f2)
    iterations = 0 
    
    while(1):
        #print(f1,f2)
        if(f2 > f1):
            f0 = f1
            f1 = f2
            f2 = f.move_motor(step_size,1).eval_score()
            score_history.append(f2)
            z2 += step_size
            iterations += 1
            
        elif(iterations <=1):
            #print(iterations, f1, f2)
            print('Found a dip, assuming it is wrong and continuing')
            f0 = f1
            f1 = f2
            f2 = f.move_motor(step_size,1).eval_score()
            score_history.append(f2)
            z2 += step_size
            iterations +=1
            
        elif(iterations <= 2):
            print('Changing search direction')
            return hill_climbing(f, -step_size)
            
         
      
            
        else:
            print ('Finised hill climbing') 
            return ((z2 - 2 * step_size -2 , z2 - step_size, z2), (f0, f1, f2))
        
  
def untested_hill_climbing(f, step_size = 500):
    """ Climb to a higher place, find a smaller interval containing focus position
    (z1, z2, z3),(f1, f2, f3) = hill_climbing(f)
    
    """
    global scan_direction
    print('Starting hill climbing')
    #f1 = f.eval_score()
    f1 = low_res_score(f.get_image())
    z1 = 0
    #f2 = f.move_motor(step_size, 1).eval_score()
    f.move_motor(step_size, 1)
    f2 = low_res_score(f.get_image())
    
    z2 = step_size
    score_history.append(f1)
    score_history.append(f2)
    iterations = 0 
    
    while(1):
        #print(f1,f2)
        if(f2 > f1):
            f0 = f1
            f1 = f2
            #f2 = f.move_motor(step_size,1).eval_score()
            f.move_motor(step_size, 1)
            f2 = low_res_score(f.get_image())
            score_history.append(f2)
            z2 += step_size
            iterations += 1
            
        elif(iterations <=1):
            #print(iterations, f1, f2)
            print('Found a dip, assuming it is wrong and continuing')
            f0 = f1
            f1 = f2
            f.move_motor(step_size,1)
            f2 = low_res_score(f.get_image())
            score_history.append(f2)
            z2 += step_size
            iterations +=1
            
        elif(iterations <= 2):
            return hill_climbing(f, -step_size)
            
         
      
            
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
    
def test_autofocus(timeout=90):
    global score_history
    start_time = time.time()
    
    score_history = [] # Clear history
    m = microscope_control(timeout=timeout)
    
    try:
        naive_autofocus(m)
        return score_history
        # Find small interval containing focus position
        z,f = hill_climbing(m) # uses the raw variance score
        #z,f = untested_hill_climbing(m) # using DWT low resolution images, should have less noise!
        #print('Peak in between', z)
        #time.sleep(5)
        
        # Gaussian prediction
        print('Gaussian prediction')
        mu = gaussian_fitting(z,f)
        #print('Moving to predicted position: %f' %mu)
        m.move_motor(-z[2]+mu, 2)
        score_history.append(m.eval_score())
        #print('Prediction Score : %f' % score_history[-1])
        interval = (mu-600, mu + 600)
        
        #print('Interval for fibonacci search', interval)
        #time.sleep(5)
        
        # Fibonacci search
        (a,b,x, z1, z3, z2) = fibonacci_search(interval, m)
        #print('Interval for parabola fitting: (%f, %f, %f)' %(a,x,b) )
        print('Parabola prediction')
        # # Parabola prediction
        mu = parabola_fitting((z1,z2,z3), (-score_history[-2],-score_history[-1],-score_history[-3]))
        #print ('Moving to predicted position: %f' % mu)
        m.move_motor(-x+mu, pause = 3)
        score_history.append(m.eval_score())
        print('Final Score: %f' %score_history[-1])
        
        
        end_time = time.time()
        print('Time takes is %f' %(end_time-start_time))
        
        #plt.plot(score_history)
        #plt.xlabel('Iterations')
        #plt.ylabel('Score')
        #plt.title('Score history')
        #plt.grid()
        #plt.show()

    except Exception:
        print("timeout")
    
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
    
        
