from . import V
import numpy as np
import scipy as sp
from scipy.stats import uniform
from . import random_field as field
from numba import njit

def compute_cbc(c, c_sat, phi, D, dt):
    '''
    compute the average concentration in the boundary cell based on Eulerian flux
    '''
    phi = phi[-2, 1:-1][V.dirichlet_dofs]
    dc_dy = 2*(c[-2, 1:-1][V.dirichlet_dofs] - c_sat)/V.dc_y[-1]
    dc_dx = ((c[-2, 2:] - c[-2, :-2])/(V.dc_x[1:] + V.dc_x[:-1]).T).ravel()
    Dyy = (D[1:-1, 1:-1, -1][-1, V.dirichlet_dofs] + D[:, 1:-1, -1][-1, V.dirichlet_dofs])/2
    Dxy = (D[1:-1, 1:-1, 1][-1, V.dirichlet_dofs]  + D[:, 1:-1, 1][-1, V.dirichlet_dofs])/2
    J = - (Dyy*dc_dy + Dxy*dc_dx[V.dirichlet_dofs])
    # J = - (D[1:-1, 1:-1, -1][-1, V.dirichlet_dofs]*dc_dy + D[1:-1, 1:-1, 1][-1, V.dirichlet_dofs]*dc_dx[V.dirichlet_dofs])
    
    mass = J*V.dx[1:-1][V.dirichlet_dofs].T*dt
    return mass#/(phi*V.dv[-2, 1:-1][V.dirichlet_dofs])
    
@njit
def reflection(plst, bdr=None, axis:str=None):
    # define matrices for reflection along y and x axis
    ry = np.array([[-1, 0], [0, 1]]) 
    rx = np.array([[1, 0], [0, -1]])       
    
    wts, loc = plst[:, 0], plst[:, 1:]
    if bdr is None:
        raise Exception("Boundary must be mentioned for performing reflection")
    elif axis =="x":
        slst = (bdr.reshape(-1, 1) + (rx @ (loc.T - bdr.reshape(-1, 1)))).T
    elif axis == "y":
        slst = (bdr.reshape(-1, 1) + (ry @ (loc.T - bdr.reshape(-1, 1)))).T
    S = np.empty((plst.shape[0], 3))
    S[:, 0] = wts; S[:, 1] = slst[:, 0]; S[:, 1] = slst[:, 1]
    return S

def compute_unit_release_locs(i, A, B, phi, dt, plst, qb, dofs, Ef, En, xf, yf, dv):
    lst = plst[i, :, :].copy()
    lst[:, 1:] += ADSolve(A, B, phi, dt, En, Ef, lst[:, 1:]) 
    lst, _, _ = rwpt_bcs(lst, qb)   
    mu_w, _, _ = np.histogram2d(lst[:, 1], lst[:, 2], bins=(xf[1:-1], yf[1:-1]), density=False, weights=lst[:, 0])
    mu_w = mu_w.T
    return mu_w/(phi[1:-1, 1:-1]*dv[1:-1, 1:-1]), mu_w[-1, dofs], lst
    # return  mu_w[-1, dofs]

def compute_emission_rates(A, B, D, phi, c_sat, c, dt, plst):
    from multiprocessing import Pool
    args = [(i, A, B, phi, dt, plst, V.qb, V.dirichlet_dofs, V.Ef, V.En, V.xf, V.yf, V.dv) for i in range(plst.shape[0])]
    with Pool() as pool:
        results = pool.starmap(compute_unit_release_locs, args)
    res, s, lst = zip(*results)

    C = np.array(res)
    S = np.array(s)
    
    # S = np.array(res)
    S = S.T
    S[np.diag_indices_from(S)] *= 2
    dc = compute_cbc(c, c_sat, phi, D, dt).ravel()
    zero_diag_id = np.where(abs(np.diag(S))<1e-12)[0]
    
    mask = []
    if len(zero_diag_id)!=0:
        mask = np.ones(S.shape[0], dtype=bool)
        mask[zero_diag_id] = False
    
        rMAT = S[np.ix_(mask, mask)]
        rRHS = dc[mask]
        e = np.linalg.solve(rMAT, rRHS)
        lst = [ppos for ppos, status in zip(lst, mask) if status]
    
    else: e = np.linalg.solve(S, dc)
    
    L = np.empty((0, 3))
    for i, l in enumerate(lst):
        # if i in np.where(mask == False)[0]:
        #     print("Its there")
        #     l[:, 0] *= 0
        l[:, 0] *= e[i]
        L = np.vstack((L, l))

    return e, L
    # return e, (C.T@e).T, L#np.vstack(lst)
    # tot_mass_inj = e * dt
    # return tot_mass_inj/(phi[-2, 1:-1][V.dirichlet_dofs]*V.dv[-2, 1:-1][V.dirichlet_dofs]), e # add the concentration to the binned emitter kernels

@njit
def unit_injection_locs(dt, dofs, mpp, H, L, dy):
    """
    Calculate the emission rates for each emitter based on the Dirichlet boundary conditions.
    The emission rate is calculated as the product of the Dirichlet value and the area of the emitter.
    """
    tot_moles = dt # considering a unit release rate, so in dt time dt mass is released
    mpp = int(tot_moles/50) # particle count for each emitter
    PL = np.empty((len(dofs), 50, 3))
    for i, k in enumerate(dofs):
        for j in range(50):
            px = np.random.uniform(V.xf[1:-1][k], V.xf[1:-1][k+1])
            py = np.random.uniform(H-dy, H)
            PL[i, j, 0] = mpp 
            if py > H:
                py = 2*H - py
            if px > L:
                px = 2*L - px
            if px < 0.:
                px = -px
            PL[i, j, 1] = px; PL[i, j, 2] = py
    return PL

def generate_particle_cloud(c, phi, ppc):
    # id = (c[1:-1, 1:-1]).ravel().astype("bool")
    # loc = V.En_int[id]
    id = np.where((V.En_int[:, 0]>=V.extent[0]) & (V.En_int[:, 0]<=V.extent[1]) & (V.En_int[:, 1]>=V.H-V.dy[-2][0]) & (V.En_int[:, 1]<=V.H))[0]
    loc = V.En_int[id]
    dim = V.dvg[id]
    mpp = (c[1:-1, 1:-1][-1, V.dirichlet_dofs].ravel()*V.dv[1:-1, 1:-1][-1, V.dirichlet_dofs].ravel()*phi[1:-1, 1:-1][-1, V.dirichlet_dofs].ravel())/ppc
    # loc = V.En_int[]
     
    points = np.empty((0, 3))
    for l, a, m in zip(loc, dim, mpp):
        xp = uniform.rvs(l[0]-a[1]/2, a[1], int(ppc))
        yp = uniform.rvs(l[1]-a[0]/2, a[0], int(ppc))
        plst = np.stack([np.full(len(xp), m), xp, yp], axis=-1)
        points = np.vstack([points, plst])
    return points

def resample(plst, w0):
    from scipy.spatial import cKDTree
    from scipy.stats import uniform
    
    w0 = w0.reshape(-1, 1)
    tree = cKDTree(V.En_int)
    _, ii = tree.query(plst, k=1)
    ii_unq, p2g = np.unique(ii, return_inverse=True)

    w = np.empty([0, 1])
    Ln = np.empty([0, 2])

    for i in range(len(ii_unq)):
        p_id = np.where(p2g==i)[0]
        if len(plst[p_id]) > V.ppc:
            loc = V.En_int[ii_unq[i]]
            dim = V.dvg[ii_unq[i]]
            mpp = w0[p_id].sum()/V.ppc
            xp = uniform.rvs(loc[0]-dim[1]/2, dim[1], int(V.ppc))
            yp = uniform.rvs(loc[1]-dim[0]/2, dim[0], int(V.ppc))
            P = np.stack([np.full(len(xp), mpp), xp, yp], axis=-1)
            
            Ln = np.concatenate((Ln, P[:, 1:])); w = np.concatenate((w, P[:, 0].reshape(-1, 1)))
        else:
            w = np.concatenate((w, w0[p_id])); Ln = np.concatenate((Ln, plst[p_id])) 
    
    P = np.stack([w.ravel(), Ln[:, 0], Ln[:, 1]], axis=1)
    return P

def ADSolve(A, B, phi, dt, En, Ef, plst):
    Ai = np.stack([field.Field.interpolation(Ef, A[:, i], plst).ravel() for i in range(2)], axis=1)
    Bi = np.stack([field.Field.interpolation(En, B[:, :, i].ravel(), plst) for i in range(4)], axis=2).reshape(-1, 2, 2)
    phi_p = field.Field.interpolation(En, phi, plst).ravel()
    N = np.random.normal(0, 1, size=plst.shape)
    dx = 1/phi_p*Ai[:, 0]*dt + np.einsum('ij, ij->i', Bi[:, :, 0], N) * np.sqrt(dt)
    dy = 1/phi_p*Ai[:, 1]*dt + np.einsum('ij, ij->i', Bi[:, :, 1], N) * np.sqrt(dt)
    return np.stack((dx, dy), axis=-1)

def generate_bin_counts(plst):
    mu_w, _, _ = np.histogram2d(plst[:, 1], plst[:, 2], bins=(V.xf[1:-1], V.yf[1:-1]), density=False)
    return mu_w.T

def binned_concentration(plst):
    mu_w, _, _ = np.histogram2d(plst[:, 1], plst[:, 2], bins=(V.xf[1:-1], V.yf[1:-1]), density=False, weights=plst[:, 0])
    return mu_w.T

def rwpt_bcs(plst, qb):
    nb_top = ((plst[:, 2]>V.H) & ((plst[:, 1]<V.extent[0]) | (plst[:, 1]>V.extent[1]))) 
    nb_bottom = (plst[:, 2] < 0.) 
    plst[nb_top] = field.Field.reflection(plst[nb_top], np.array(V.H), "x")
    plst[nb_bottom] = field.Field.reflection(plst[nb_bottom], np.array(0.), "x")
    db_L = np.where(plst[:, 1]>V.L)[0]
    db_0 = np.where(plst[:, 1]<0.)[0]
    
    tm_adv = 0.0
    if qb == 0.0:
        if len(db_L)!=0:
            plst[db_L] = field.Field.reflection(plst[db_L], np.array(V.L), "y")
        if len(db_0)!=0:
            plst[db_0] = field.Field.reflection(plst[db_0], np.array(0.), "y")
    else:
        tm_adv += plst[db_L][:, 0].sum()
        plst = np.delete(plst, np.concatenate((db_L, db_0)), axis=0)

    db_top = np.where((plst[:, 2]>V.H) & ((plst[:, 1]>=V.extent[0]) & (plst[:, 1]<=V.extent[1])))
    tm_diff = plst[db_top][:, 0].sum()
    plst = np.delete(plst, db_top, axis=0)
    return plst, tm_diff, tm_adv
        
    

    

    



    
