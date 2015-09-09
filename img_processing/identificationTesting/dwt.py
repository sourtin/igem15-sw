# Calculate N-level DWT of an image and store the low resolution images in an array

import numpy as np
import cv2

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
    
# def nleveldwt_old(N, shape, X):
    # """ N Level DWT of image """
    # if N>0:
        # print (N)
        # m = np.array(range(shape[0]))
        # n = np.array(range(shape[1]))
        # #print(Y[m,:][:,n].shape)
        # Y[m,:][:,n] = dwt(X[m,:][:,n])
        # return nleveldwt(N-1, (int(shape[0]/2),int(shape[1]/2)), Y)
    # else:
        # pass
        
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
    score = 0
    for i in X:
        i += 1
        score += np.var(i)
    return score
    
if __name__ == '__main__':
    X = cv2.imread('C:\\Users\\RAK\\Documents\\iGEM\\Software\\lighthouse.jpg', cv2.IMREAD_GRAYSCALE)
    print('Image read is of shape ', X.shape)
    #Y = dwt(X)
    Ys = nleveldwt(3, X)
    print('Finished DWT decomposition of image')
    print('Output image size is ', Ys[0].shape)
    i = 0
    # for Y in Ys:
        # cv2.imwrite('Ys%d.png' % i, Y)
        # i += 1
    print (focus_score(Ys[1:]))