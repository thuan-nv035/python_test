luoi = [0,1,2,3,4,5,6,7,8]
def inluoi():
    for i in range(0,9,3):
        print(luoi[i], '|', luoi[i+1], '|', luoi[i+2])
        print('----------')
inluoi()