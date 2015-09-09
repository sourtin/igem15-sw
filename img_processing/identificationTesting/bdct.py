# An implementation of the image processing method developed in the paper :
# An effective image segmentation method for noisy low-contrast unbalanced
# background in Mura defects using balanced discrete-cosine-transfer (BDCT)
# Liang-Chia Chena, Chih-Hung Chien and Xuan-Loc Nguyenb
# Link to the paper : http://www.sciencedirect.com/science/article/pii/S0141635912001432



# Import stuff
import cv2
import numpy as np
import scipy.fftpack as fftpack

# Contrast stretch function, takes in image I and repeats the process N times
def contrast_stretch(I, N):
    """
    contrast_stretch(I,N) 
    where I is BW image matrix and N is a integer.
    
    Carries out contrast enhancement of the image using the method described
    in the paper by L.Chen et al(2013) :
    'An effective image segmentation method for noisy low-contrast unbalanced
    background in Mura defects using balanced discrete-cosine-transfer (BDCT)'
    
    """
    # Set the upper threshold (T_up) and lower threshold (T_low)
    T_up = 254
    T_low = 1
    for i in range(N):
        # Find the max (G_max) and the min (G_min) pixel in image
        if I.max()<T_up:
            G_max = I.max()
        else: 
            G_max = T_up
        if I.min()>T_low:
            G_min = I.min()
        else: 
            G_min = T_low
            
        # Set the Gain and Offset value
        Gain = T_up/G_max 
        Offset = G_min*Gain
                
        # Get the enhanced image
        I = I*Gain - Offset*np.ones_like(I)
        #cv2.imwrite('stage_1.png',I)
    return I
    
# Brightness-direction balancing function
def brightness_direction_balance(I):
    """
    brightness_direction_balance(I)     where I is a BW image matrix.
    Carries out brightness direction balancing as described by the paper by L.Chen et al(2013) :
    'An effective image segmentation method for noisy low-contrast unbalanced
    background in Mura defects using balanced discrete-cosine-transfer (BDCT)'
    
    """
    M = I.shape[0] # number of columns in image matrix
    N = I.shape[1] # number of rows in image matrix
    
    Wx_matrix = np.reshape(np.mean(I, axis = 0), (1,N)) # mean grey value of each column
    Wy_matrix = np.reshape(np.mean(I, axis = 1), (1,M)) # mean grey value of each row
    
    ############# Old stuff ################
    # Wx_max_matrix = np.reshape(np.max(I, axis = 0), (1,N)) # max grey values of each column
    # Wy_max_matrix = np.reshape(np.max(I, axis = 1), (1,M)) # max grey values of each row

    # # Arrange the values into a matrix
    # Wx = np.repeat((Wx_max_matrix/Wx_matrix), M, axis = 0)
    # Wy = np.transpose(np.repeat((Wy_max_matrix/Wy_matrix), N, axis = 0))
    
        # # Filter the image
    # I = np.rint(0.5 * np.multiply( I , (Wx + Wy)))
    ##########################################
    
   ############ New stuff ########################## 
    Wx_max = np.max(Wx_matrix)
    Wy_max = np.max(Wy_matrix)
    Wx_matrix = 0.5 * Wx_max / Wx_matrix
    Wy_matrix = 0.5 * Wy_max / Wy_matrix
  
    for i in range(0,N):
        for j in range(0,M):
            #print(i,j)
            #print(i)
            I[j,i] = I[j,i] * 0.5 * (Wx_matrix[0,i] + Wy_matrix[0,j])

    ####################################

    #cv2.imwrite('stage_2.png',I)
    return(np.float32(I))
  
# Background reconstruction using DCT-II function
def background_reconstruction_dct(I):
    """
    background_reconstruction_dct(I)      where I is a BW image matrix
    Reconstructs the background image by the DCT method proposed in the paper by 
    L.Chen et al (2008) :
    'Automatic TFT-LCD mura defect inspection using discrete cosine transform-based background filtering and ‘just noticeable difference’ quantification strategies'
    
    """
    # Type II DCT is used, the inverse is the Type-III DCT according to SF2 handout
    M = I.shape[0] # number of columns in image matrix
    N = I.shape[1] # number of rows in image matrix
    
    X = fftpack.dct(fftpack.dct(I,  type = 2, norm = 'ortho').T, type = 2, norm = 'ortho').T
    X[1:,:][:,1:]= 0;
    Y =fftpack.idct( fftpack.idct(X, type = 2, norm = 'ortho').T, type =2, norm = 'ortho').T
    Y = np.uint8(Y)
    #cv2.imwrite('stage_3.png', Y)
    return Y
    
# Carry out the BDCT
def bdct(img, N = 20):
    
    """ Do contrast stretch """
    img = contrast_stretch(img, int(N))
    
    """ Gaussian blur"""
    img = cv2.GaussianBlur(img, (3,3),0)
        
    """ Do brightness correction """
    img = brightness_direction_balance(img) # <- returns it as float64
    
    """ DCT to get background """
    #img = np.float64(img)
    img_bg = background_reconstruction_dct(img)
    
    """ Image difference classification """
    img_idc = img_bg - img
    #cv2.imwrite('stage_4.png', img_idc)
    
    """ Otsu thresholding """ # <-- this did not work as well as the paper suggested, normal thresholding using a slider would be better
    
    #img_idc = cv2.convertScaleAbs(img_idc)
    #ret2,img = cv2.threshold(img_idc,img_idc.min(),img_idc.max(),cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    """ Return processed image"""
    # Output final image
    img_out = cv2.convertScaleAbs(img_idc)
    return img_out
    #return cv2.bitwise_not(img_out,img_out)
    #cv2.threshold(img_out, 0, 255, cv2.THRESH_BINARY)
    #print(img_out)
    #cv2.imwrite("stage_final.png", img_idc)    
    


if __name__ == '__main__':
    
    """ Read in image """
    image_name = input("Type in picture name, eg. 'marchantia5.jpg' \n")
    # Default image 
    if image_name == "" :
        image = cv2.imread('C:\\Users\\RAK\\Documents\\iGEM\\Software\\focusedMarchantia_small.jpg')
    else:
        image = cv2.imread(image_name)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) # Convert to black and white
        
    """ BDCT """ 
    img = bdct(img=image)
    
    """ Display image """
    # Resize picture
    if img.shape[0] > 500 | img.shape[1] > 500 :
       cv2.resize(image, (0,0), fx=0.125, fy=0.125)
    cv2.namedWindow("Press any key to close", flags = cv2.WINDOW_NORMAL)
    cv2.moveWindow("Press any key to close", 500,0)
    #print(img.dtype, img.shape)
    #print(img)
    #ret2,img = cv2.threshold(img,img.min(),img.max(),cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    cv2.imshow('Press any key to close', img)
    cv2.waitKey()
    cv2.destroyAllWindows()
