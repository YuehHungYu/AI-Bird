import pandas as pd 
import pickle

f=open(r"C:/Users/88691/Desktop/pyth/pygame/bird/best.pickle","rb")
print(f)
c=pickle.load(f)
print(c)
f.close()

a=pd.read_pickle(r"C:/Users/88691/Desktop/pyth/pygame/bird/best.pickle")
print(a)
