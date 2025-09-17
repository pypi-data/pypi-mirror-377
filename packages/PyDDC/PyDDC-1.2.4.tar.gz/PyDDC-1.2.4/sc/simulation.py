
import numpy as np
import co2br
from . random_field import Field
from . import flow_solver as fs
from . transport_solver import *
import json
from . import V
import tables
from tqdm import tqdm 
import logging
import time
import os
import warnings
warnings.filterwarnings("ignore")

def _MeshRefinement(param, type):
    xf = np.linspace(0, V.L, V.nx+1, endpoint="True")
    yf = np.linspace(0, V.H, V.ny+1, endpoint="True")
    dy = V.H/V.ny
    num_cells = param["refine_levels"]
    fac = param["res_levels"]

    if type=="refined":
        yf = np.unique(np.concatenate((yf[:-num_cells], np.arange(yf[-num_cells], V.H, dy/fac))))
        yf = np.append(yf, V.H)
        dy = yf[1:] - yf[:-1]
        V.ny = len(yf)-1

    V.xf = np.zeros(len(xf)+2); V.yf = np.zeros(len(yf)+2)
    V.xf[1:-1] = xf[:]; V.yf[1:-1] = yf[:]
    V.xf[0] = xf[0] - xf[1]; V.xf[-1] = xf[-1] + (xf[-1] - xf[-2])
    V.yf[0] = yf[0] - yf[1]; V.yf[-1] = yf[-1] + (yf[-1] - yf[-2])

    x_f1, x_f2 = np.meshgrid(V.xf[1:-1], V.yf[1:-1])
    V.Ef = np.vstack([x_f1.ravel(), x_f2.ravel()]).T

    V.y = (V.yf[1:] + V.yf[:-1])/2.0
    V.x = (V.xf[1:] + V.xf[:-1])/2.0

    xxf1, xxf2 = np.meshgrid(V.xf[1:-1], V.y[1:-1]) 
    V.Ex = np.vstack([xxf1.ravel(), xxf2.ravel()]).T
    yyf1, yyf2 = np.meshgrid(V.x[1:-1], V.yf[1:-1])
    V.Ey = np.vstack([yyf1.ravel(), yyf2.ravel()]).T

    V.dx = (V.xf[1:] - V.xf[:-1]).reshape(-1, 1)
    V.dy = (V.yf[1:] - V.yf[:-1]).reshape(-1, 1)
    V.dv = np.outer(V.dy, V.dx)
    V.dyg = V.dv/V.dx.T
    V.dxg = V.dv/V.dy
    V.dvg = np.stack([V.dyg[1:-1, 1:-1].ravel(), V.dxg[1:-1, 1:-1].ravel()], axis=1)

    V.dc_x = (V.x[1:] - V.x[:-1]).reshape(-1, 1); V.dc_y = (V.y[1:] - V.y[:-1]).reshape(-1, 1)
 
    V.xx, V.yy = np.meshgrid(V.x, V.y)
    V.En = np.vstack([V.xx.ravel(), V.yy.ravel()]).T # Eulerian nodes
    V.En_int = np.vstack([V.xx[1:-1, 1:-1].ravel(), V.yy[1:-1, 1:-1].ravel()]).T
 
    # facet weights to be used for linear interpolation
    V.gy = V.dy[:-1]/(V.dy[1:]+V.dy[:-1])
    V.gx = V.dx[:-1]/(V.dx[1:]+V.dx[:-1])

    V.gn = V.dy[1:-1]/(V.dy[2:]+V.dy[1:-1])
    V.gs = V.dy[1:-1]/(V.dy[:-2]+V.dy[1:-1])
    V.ge = V.dx[1:-1]/(V.dx[2:]+V.dx[1:-1])
    V.gw = V.dx[1:-1]/(V.dx[:-2]+V.dx[1:-1])


def ModelInitialization(file):
    '''
    Initializes the model and stores global info in V.py
    file : ".json" file provided by the user
    '''
    
    with open(file, "r") as f:
        param = json.load(f)

    V.L = param["Length"]
    V.H = param["Height"]
    V.nx = param["NumCellsX"]
    V.ny = param["NumCellsY"]
    
    if param["refine_levels"] and param["res_levels"]:
        mesh_type = "refined"
    else:
        mesh_type = "default"
    _MeshRefinement(param, type=mesh_type)

    V.P = param["Pressure"]# MPa
    V.T = param["Temperature"]# degree celcius
    V.m = {
        "NaCl":param["NaCl"],
        "KCl":param["KCl"],
        "CaCl2":param["CaCl2"],
        "MgCl2":param["MgCl2"],
        "K2SO4":param["K2SO4"],
        "MgSO4":param["MgSO4"],
    }
    V.rw = param["BrineDensity"]
    V.rs = param["CO2SaturatedBrineDensity"]
    V.mu_co2br = param["CO2SaturatedBrineViscosity"]
    V.mu_br = param["BrineViscosity"]
    V.D = param["DiffusionCoefficient"]
    V.c_sat = param["CO2SaturatedConcentration"]

    V.g = 9.8 #m/s

    V.k_mean = param["Mean"]
    V.lnk_var = param["lnVariance"]
    V.k_corr = np.append(param["CorrelationLengthX"], param["CorrelationLengthY"])
    V.d = param["GrainSize"]
    V.phi = param["porosity"]

    V.al = param["SubgridLongitudinalDispersion"]
    V.at = param["SubgridTransverseDispersion"]   
    V.qb = param["BackgroundFlow"] * 3.17e-8
    V.ST = param["SimulationTime"]
    V.dt = param["TimeIncrement"]

    V.extent = np.append(param["HorizontalExtentLower"], param["HorizontalExtentUpper"])

    V.ppc = param["ParticlesPerBin"]
    V.mpp = param["MolesPerParticle"]

    V.dirichlet_dofs = np.arange(int(V.extent[0]/V.dx[0]), int(V.extent[1]/V.dx[0])) # concentration boundary conditions: c=c_sat
    V.neumann_dofs = np.setdiff1d(np.arange(V.nx), V.dirichlet_dofs)

class Simulate:
    def __init__(self, inp_file:str=None, out_file:str=None, group_name:str=None, process=0, realization_id=1):

        ModelInitialization(inp_file)
        self.attr = {"c": np.zeros([V.ny+2, V.nx+2]), 
                     "rho": np.zeros([V.ny+2, V.nx+2]), 
                     "mu": np.zeros([V.ny+2, V.nx+2])
                    }
        
        self.pid = str(process)
        self.logger = logging.getLogger(self.pid)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            lf = os.path.join("./logs", "{}.log".format(self.pid))
            hdl = logging.FileHandler(lf, encoding='utf8')
            fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            hdl.setFormatter(fmt); self.logger.addHandler(hdl)
        self.logger.info("Param list: ".format(group_name))
        
        self.kf, self.phif = Field.compute_field_variables()
        if out_file is not None and group_name is not None:
            self.df = tables.open_file(out_file + "_" + str(realization_id) + ".h5", mode='a') # initialize the binary file to write data into
            self.data = group_name
            self.group_name = group_name
            self.process = int(process)
            self.r_id = realization_id

    def _Dirichlet_bcs(self, f, bval):
        f[:, 1:-1][-1, V.neumann_dofs] = f[:, 1:-1][-2, V.neumann_dofs]
        f[:, 1:-1][-1, V.dirichlet_dofs] = 2.0*bval - f[:, 1:-1][-2, V.dirichlet_dofs]
        f[:, 0] = f[:, 1]; f[:, -1] = f[:, -2]; f[0, :] = f[1, :]
        return f
    
    def __compute_phase_bcs(self, P, T):
        if V.c_sat is None:
            self.c_sat = co2br.Solubility(P, T).CO2Solubility(V.m)
        else:
            self.c_sat = V.c_sat
        self.r_sat, self.rw = co2br.Density(P, T).BrineDensity(V.m, self.c_sat)
        self.mu_sat = co2br.SolutionViscosity(T, V.m).Co2BrineViscosity(self.rw, self.c_sat)
        self.mu_ref = co2br.SolutionViscosity(T, V.m).Co2BrineViscosity(self.rw, 0)
        self.r_sat = self.r_sat.mean(); self.c_sat = self.c_sat.mean(); self.rw = self.rw.mean(); self.mu_sat = self.mu_sat.mean()
        self.c_sat = self.c_sat * self.r_sat # convert c_sat form moles/kg -> moles/m3
    
    def compute_phase_attributes(self, P, T):
        if isinstance(P, np.ndarray) and P.ndim == 2:
            self.__compute_phase_bcs((P[:, 1:-1][-2, V.dirichlet_dofs] + P[:, 1:-1][-1, V.dirichlet_dofs])/2, T)
        else:
            self.__compute_phase_bcs(P, T)

        self.attr["rho"][1:-1, 1:-1] = self.density(self.attr["c"][1:-1, 1:-1], self.c_sat, self.r_sat, self.rw) # the density field computed from the linear model
        
       
        # self.attr["rho"][1:-1, 1:-1], self.rw = co2br.Density(P[1:-1, 1:-1], T).BrineDensity(V.m, self.attr["c"][1:-1, 1:-1])
        self.attr["mu"][1:-1, 1:-1] = co2br.SolutionViscosity(T, V.m).Co2BrineViscosity(self.rw, self.attr["c"][1:-1, 1:-1]/self.attr["rho"][1:-1, 1:-1])
        # self.mu_ref = co2br.SolutionViscosity(T, V.m).Co2BrineViscosity(self.rw, np.zeros_like(self.attr["c"][1:-1, 1:-1]))
        # self.mu_ref = co2br.SolutionViscosity(T, V.m).Co2BrineViscosity(self.rw, np.zeros_like(self.attr["c"][1:-1, 1:-1])) # reference viscosity for the brine without CO2    
        # self.attr["c"][1:-1, 1:-1]*=self.attr["rho"][1:-1, 1:-1] # concentration in moles/m3

        self.attr["rho"], self.attr["mu"], self.attr["c"] = list(map(self._Dirichlet_bcs, [self.attr["rho"], self.attr["mu"], self.attr["c"]], 
                                                                     [self.r_sat, self.mu_sat, self.c_sat]))

    def _configure_init_condition(self):
        self.compute_phase_attributes(np.ones([V.ny+2, V.nx+2])*V.P, V.T)
        self.logger.info("Saturated Concentration: {} [moles/kg]".format(self.c_sat/self.r_sat))
        self.logger.info("Saturated Brine Density: {} [kg/m3]".format(self.r_sat))
        self.logger.info(" Brine Density: {} [kg/m3]".format(self.rw))
        self.logger.info("Saturated Brine Viscosity: {} [Pa s]".format(self.mu_sat))
        
        # self.logger.info("Saturated Concentration: {} [moles/kg]".format((self.c_sat/self.r_sat).max()))
        # self.logger.info("Saturated Brine Density: {} [kg/m3]".format(self.r_sat.max()))
        # self.logger.info(" Brine Density: {} [kg/m3]".format(self.rw.max()))
        # self.logger.info("Saturated Brine Viscosity: {} [Pa s]".format(self.mu_sat.max()))
        F = fs.FlowSolver(self.kf, self.phif)
        # self.PL, self.PR = F._pressure_DirichletBC(self.attr["rho"], self.mu_ref)
        F.solve(self.attr["rho"], self.attr["mu"], self.mu_ref)
        return F
    
    def density(self, c, c_sat, rs, rw):
        return rw + (rs - rw)*c/c_sat
    
    def RWPT(self): # Random Walk Particle Tracking 
        # from . transport_solver import ScalarTransport as st
        from multiprocessing import Pool

        progress = tqdm(total=V.ST, position=int(self.pid), desc=self.pid, bar_format="{l_bar}{bar}| {postfix}", ncols=100, disable=False)
        self.WriteDataObj()
        F = self._configure_init_condition()

        t = 0
        t_arr = []
        self.Ln = np.empty((0, 3))
        while t<=V.ST:
            counter = time.time()
            A, D = F.DeterministicDrift()
            B = F.CellwiseDisplacementMatrix()
            if V.dt is None:
                dt = F._globalCFL(D, self.phif[1:-1, 1:-1])
            else:
                dt = V.dt

            # solve Lagrangian mass matrix 
            self.Ln[:, 1:] += ADSolve(A, B, self.phif, dt, V.En, V.Ef, self.Ln[:, 1:]) 
            self.Ln, tm_diff, tm_adv = rwpt_bcs(self.Ln, V.qb) 
            # self.attr["c"][1:-1, 1:-1] = binned_concentration(self.Ln)/(V.dv[1:-1, 1:-1]*self.phif[1:-1, 1:-1])

            plst = unit_injection_locs(dt, V.dirichlet_dofs, V.mpp, V.H, V.L, V.dy[-2][0])  # unit release responses 
            e, lst = compute_emission_rates(A, B, D, self.phif, self.c_sat, self.attr["c"], dt, plst)
            # e, self.attr["c"][1:-1, 1:-1], lst = compute_emission_rates(A, B, D, self.phif, self.c_sat, self.attr["c"], dt, plst) # this is the incremental concentration needed to be added due to the mass deficit at the boundary emitters
            # e, c_ur, lst = compute_emission_rates(A, B, D, self.phif, self.c_sat, self.attr["c"], dt, plst)
            # self.attr["c"][1:-1, 1:-1] += c_ur
            # self.attr["c"][1:-1, 1:-1] += binned_concentration(self.Ln)/(V.dv[1:-1, 1:-1]*self.phif[1:-1, 1:-1])
            self.Ln = np.concatenate((self.Ln, lst))
            self.attr["c"][1:-1, 1:-1] = binned_concentration(self.Ln)/(V.dv[1:-1, 1:-1]*self.phif[1:-1, 1:-1])

            self.logger.info("num particels:{}".format(len(self.Ln)))
            
            bin_counts = generate_bin_counts(self.Ln)
            
            if np.any(bin_counts > V.ppc):
                self.logger.info("Resampling particles")
                self.Ln = resample(self.Ln[:, 1:], self.Ln[:, 0])

            
            TM = np.sum(self.attr["c"][1:-1, 1:-1]*self.phif[1:-1, 1:-1]*V.dv[1:-1, 1:-1], axis=(0, 1)) + tm_adv# total moles in the domain
           
            self.logger.info("max concentration:{} [mol/kg]".format((self.attr["c"][1:-1, 1:-1]/self.density(self.attr["c"][1:-1, 1:-1], self.c_sat, self.r_sat, self.rw)).max()))
            self.logger.info("Particle extent: x[{}, {}], y[{}, {}]".format(self.Ln[:, 1].min(), self.Ln[:, 1].max(), self.Ln[:, 2].min(), self.Ln[:, 2].max()))
            self.compute_phase_attributes(F.p/1e6, V.T)
            F.solve(self.attr["rho"], self.attr["mu"], self.mu_ref)

            step_update = dt/3.154e7
            progress.update(round(step_update,2))
            progress.set_postfix_str(f"{t:.2f}/{V.ST} y/Ty" + f", {(time.time()-counter):.3f} s/it")
            
            t += step_update
            if int(t) not in t_arr:
                t_arr.append(int(t))
                self.df_t.append(np.array([t]))
                # self.df_e.append(e[np.newaxis, :])
                self.df_M.append(np.array([TM]))
                self.df_c.append(self.attr["c"][np.newaxis, :, :])
                self.df_mu.append(self.attr["mu"][np.newaxis, :, :])
                self.df_rho.append(self.attr["rho"][np.newaxis, :, :])
                self.df_p.append(F.p[np.newaxis, :, :])
                self.df_v.append(F.Q[np.newaxis, :, :])
                self.df_D.append(D[np.newaxis, :, :, :])
                self.df_ppos.append(self.Ln) 

        progress.close()

    def WriteDataObj(self):
        self.dg = self.df.create_group("/", "{}".format(self.data), "data")
        filters = tables.Filters(complevel=5, complib='zlib')
        self.df_t = self.df.create_earray(self.dg, "time", atom=tables.Float32Atom(), shape=(0, ), filters=filters)
        # self.df_e = self.df.create_earray(self.dg, "ParticleFlux", atom=tables.Float32Atom(), shape=(0, len(V.dirichlet_dofs)), filters=filters)
        self.df_M = self.df.create_earray(self.dg, "total_moles", atom=tables.Float32Atom(), shape=(0, ), filters=filters)
        self.df_v = self.df.create_earray(self.dg, "drift", atom=tables.Float32Atom(), shape=(0, (V.ny+2)*(V.nx+2), 2), filters=filters)
        self.df_c = self.df.create_earray(self.dg, "concentration", atom=tables.Float32Atom(), shape=(0, V.ny+2, V.nx+2), filters=filters)
        self.df_mu = self.df.create_earray(self.dg, "viscosity", atom=tables.Float32Atom(), shape=(0, V.ny+2, V.nx+2), filters=filters)
        self.df_rho = self.df.create_earray(self.dg, "density", atom=tables.Float32Atom(), shape=(0, V.ny+2, V.nx+2), filters=filters)
        self.df_p = self.df.create_earray(self.dg, "pressure", atom=tables.Float32Atom(), shape=(0, V.ny+2, V.nx+2), filters=filters)
        self.df_D = self.df.create_earray(self.dg, "dispersion", atom=tables.Float32Atom(), shape=(0, V.ny+2, V.nx+2, 4), filters=filters)
        self.df_ppos = self.df.create_vlarray(self.dg, "plume_config", atom=tables.Float32Atom(shape=(3, )), filters=filters)
        self.df_ddofs = self.df.create_array(self.dg, "dirichlet_dofs", V.dirichlet_dofs)
        self.df_ndofs = self.df.create_array(self.dg, "neumann_dofs", V.neumann_dofs)
        self.df_en = self.df.create_array(self.dg, "eulerian_nodes", V.En)
        self.df_ef = self.df.create_array(self.dg, "eulerian_facets", V.Ef)
        self.df_k = self.df.create_array(self.dg, "permeability", self.kf)
        self.df_phi = self.df.create_array(self.dg, "porosity", self.phif)
        self.df_var = self.df.create_array(self.dg, "lnVariance", V.lnk_var)
        self.df_mean = self.df.create_array(self.dg, "mean", V.k_mean)
        self.df_corr = self.df.create_array(self.dg, "correlation_length", V.k_corr)
        self.df_bg = self.df.create_array(self.dg, "background_flow", V.qb)
        

         
if __name__ == "__main__":
    import argparse as ap

    parser = ap.ArgumentParser()
    parser.add_argument("inpf", type=ap.FileType('r'))
    parser.add_argument("outf")
    parser.add_argument("data")
    parser.add_argument("pid")
    parser.add_argument("realization_id")
    args = parser.parse_args()
    
    Simulate(inp_file=args.inpf.name, out_file=args.outf, group_name=args.data, process=args.pid, realization_id=int(args.realization_id)).RWPT()