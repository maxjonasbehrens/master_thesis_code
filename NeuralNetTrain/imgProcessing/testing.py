#%%
import numpy as np

a = np.array([[[1,2,3],[2,4,1],[3,3,6],[2,7,2]],[[1,1,2],[2,4,1],[3,5,6],[2,5,7]],[[2,5,4],[3,5,6],[4,2,2],[6,4,1]]])
b = np.array([[[2,4,2],[3,6,3],[4,2,2],[6,2,4]],[[2,4,4],[3,3,6],[4,2,3],[6,2,4]],[[2,4,2],[3,5,6],[4,2,6],[6,2,4]]])
print(a.shape)
print(b.shape)
x = np.hstack((a,b))
print(x.shape)

# %%
h_temp = a[:1,:1,:]
h_temp = np.hstack((h_temp,b[:1,:1,:]))
print(h_temp.shape[2])

# %%
np.any(np.isnan(a))

# %%
len(a[0])

# %%
