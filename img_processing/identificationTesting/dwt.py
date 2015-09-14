# Calculate N-level DWT of an image and store the low resolution images in an array

import numpy as np
import cv2
import time

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

def nleveldwt(N, X):
    """ N level DWT of image
    Returns an array of the smaller resolution images
    """
    Xs = [X]
    if N > 0:
        h, w = X.shape[:2]
        Xs += nleveldwt(N-1, dwt(X)[:h//2, :w//2])
    return Xs
    
def focus_score(X):
    """ Focus score is the sum of the squared values of the low resolution images.
    """
    score = 0
    for i in X:
        i += 1
        score += np.var(i)
    return score

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
    z = z_initial + alpha
    f_current = f(z_initial)
    f_next = f(z)
    gradient = (f_next - f_current)/alpha
    converged = False
    iterations = 1
    
    # Steepest descent
    while (not converged and max_iter > iterations):
    
        z = z - alpha * gradient    # update search position
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
            
    
def z_position(z_current, z_min, z_max):
    """ Intepret z_position requests as motor steps"""
    pass

    
   
# if __name__ == '__main__':

    # X = cv2.imread('C:\\Users\\RAK\\Documents\\iGEM\\Software\\lighthouse.jpg', cv2.IMREAD_GRAYSCALE)
    # print('Image read is of shape ', X.shape)
    # #Y = dwt(X)
    # Ys = nleveldwt(3, X)
    # print('Finished DWT decomposition of image')
    # print('Output image size is ', Ys[0].shape)
    # i = 0
    # # for Y in Ys:
        # # cv2.imwrite('Ys%d.png' % i, Y)
        # # i += 1
    # print (focus_score(Ys[1:]))
    
if __name__ == '__main__':
    a = -5
    d = 10
    b = golden_section(a,d)
  
    #x = golden_section_interval_reduction((a, b , d), test_function, (test_function(a), test_function(b), test_function(d)), min_tolerance = 0.5)
    
    x = gradient_descent (5, test_function, tolerance = 0.001, alpha = 0.1)
        
# htttps://172.29.9.20:9000/_webshell/control/motor/2/50
    