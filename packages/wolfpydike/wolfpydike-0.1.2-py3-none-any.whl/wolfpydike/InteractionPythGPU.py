# %matplotlib ipympl # Allow to interact with figures in Jupyter Notebooks (Alternative = %matplotlib widget)
#%%

import sys
print(sys.version)
import math
import os
import scipy.io as spio
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.gridspec as gridspec
from math import sqrt, atan, sin, cos, tan

import DLBreach_Modules
import PointsCoordinates

from wolfhece.PyTranslate import _

class dike_coupled():
    '''Represents a dike that will be eroded'''

    def __init__(self, interpMatrix, XMINTOPO, YMINTOPO, dxy, dike_origin, rotation, riverbank, simu_duration, t_end_idx = 10**5, dikeCrest_nCells = 0):
        self.t = 0 # Time index
        self.t_end_idx = t_end_idx
        self.simu_duration = simu_duration
        self.time = np.zeros((t_end_idx)) # Time for reconstructions

        self.interpMatrix = interpMatrix
        self.dxy = dxy
        self.dike_origin = dike_origin
        self.xmin_topo, self.ymin_topo = XMINTOPO, YMINTOPO
        self.riverbank = riverbank
        self.horiz_rotation = -rotation
        self.dikeCrest_nCells = dikeCrest_nCells

        self.runDLBreach_plus()

    def runDLBreach_plus(self, store_dir = Path.cwd()):
        ## 0. Parameters initialization
        # -----------------------------
        if self.t == 0:

            # 0. Parameters initialization from external file .json
            # -----------------------------------------------------

            self.set_params(file_name = self.Test_ID, store_dir = store_dir)

            # Data initialization
            self.h_down, self.h_top, self.Ve_tot, self.Ct_star_top, self.Ct_star_down, self.C_star_top, self.C_star_down, self.q_star_top, self.q_star_down, self.dV_top, self.dV_down, self.Ae_tot_down,\
                self.Ae_tot_top, self.dze_down, self.dze_top, self.alpha, self.dz_b, self.z_s, self.z_t, self.Qin_, self.Qb, self.z_b, self.U_b_top, self.U_b_down, self.Sd, self.ds, self.dx, self.db_top_up, self.db_top_down, self.db_down_up, self.db_down_down,\
                self.b_top_up, self.b_top_down, self.b_down_up, self.b_down_down, self.B_down, self.b_down, self.B_down_up, self.B_down_down, self.B_top, self.b_top, self.B_top_up,\
                self.B_top_down, self.Ct_out_top, self.Ct_out_down, self.n, self.n_prime, self.w_s, self.h_b, self.ze_down, self.H, self.V_FP, self.breach_activated, self.btop_effMax = self.initializeVectors(t_end_idx, d50, An,\
                    An_prime, n_min, rho_s, rho, g, nu, Sp, h_b_ini, Sd_ini, Su, Lk, z_s_ini, z_t_ini, h_d, b_ini, m_up, m_down)

            # Initial dike geometry (defined by 28 points) --> t = 0
            self.ptsUS, self.ptsDS, self.coord_tri, self.idx_tri = PointsCoordinates.initialize(self.end_up, self.end_down, self.b_down[0], self.b_down_down, self.b_down_up, self.b_top[0], self.b_top_down, self.b_top_up, self.Lk, self.Sd, self.Su, self.h_d, self.h_b, self.z_b, self.m_down, self.m_up, self.dx, 0, self.slope)

            # Interpolation matrix
            self.nbx_topo, self.nby_topo = self.interpMatrix.nbx, self.interpMatrix.nby
            self.topoArray = np.zeros((self.t_end_idx,self.nbx_topo,self.nby_topo))
            self.coord_tri[:,0] -= min(self.coord_tri[:,0])
            self.coord_tri[:,1] -= min(self.coord_tri[:,1]) # + remove 0.5 from coord_tri for tests 1, 2 and 3 only
            self.coord_tri[:,2] += self.elevation_shift
            if self.riverbank == 'left': # Flip dike to match the MNT
                self.coord_tri[:,1] = -self.coord_tri[:,1]
            if self.horiz_rotation != 0:
                angle = self.horiz_rotation/180 * math.pi
                x_temp = self.coord_tri[:,0] * cos(angle) - self.coord_tri[:,1] * sin(angle)
                y_temp = self.coord_tri[:,0] * sin(angle) + self.coord_tri[:,1] * cos(angle)
                self.coord_tri[:,0], self.coord_tri[:,1] = x_temp, y_temp
            self.coord_tri[:,0] = self.coord_tri[:,0]+self.dike_origin[0]
            self.coord_tri[:,1] = self.coord_tri[:,1]-min(self.coord_tri[:,1])+self.dike_origin[1]
            self.interpMatrix.interpolate_on_triangulation(coords=self.coord_tri, triangles=self.idx_tri)
            self.topoArray[0,:,:]=self.interpMatrix.array.data # Where elevation data are stored
            self.topoArray[0,:,:] = np.fliplr(self.topoArray[0,:,:])

            # Data stored from WOLF
            if self.dikeCrest_nCells == 0:
                self.Uybreach = np.zeros((self.t_end_idx,self.nbx_topo))    # Water velocity at the breach
                self.hbreach = np.zeros((self.t_end_idx,self.nbx_topo))     # Water depth at the breach
                self.zbbreach = np.zeros((self.t_end_idx,self.nbx_topo))    # Bathy at the breach (along crest centerline)
            else:
                self.Uybreach = np.zeros((self.t_end_idx,self.dikeCrest_nCells))    # Water velocity at the breach
                self.hbreach = np.zeros((self.t_end_idx,self.dikeCrest_nCells))     # Water depth at the breach
                self.zbbreach = np.zeros((self.t_end_idx,self.dikeCrest_nCells))    # Bathy at the breach (along crest centerline)

        else:

            # Iterate on time
            t = self.t-1
            dt = self.time[t+1]-self.time[t]

            #The following parameters are not modified during the simulation
            t_end_idx, g, d50, nu, rho, rho_s, p, phi, dam, Su, Sd_ini, Lk, h_d, dx_min, end_up, end_down, xmin_topo, ymin_topo, m, m_up, m_down, m_mean,\
            h_b_ini, b_ini, lmc, wmc, S_lat, slope, z_s_ini, z_t_ini, c1, c2, c_eff, lambda_loss, An, An_prime, n_min, lbda, theta_cr, Sp, C_stara, \
            C_starb, C_starc, C_stard, qb_stara, qb_starb, lambda0a, lambda0b, cb_coef, b_eff_frac = self.t_end_idx,\
            self.g, self.d50, self.nu, self.rho, self.rho_s, self.p, self.phi, self.dam, self.Su, self.Sd_ini, self.Lk, self.h_d, self.dx_min, self.end_up, self.end_down, self.xmin_topo, self.ymin_topo, self.m, self.m_up, self.m_down, self.m_mean,\
            self.h_b_ini, self.b_ini, self.lmc, self.wmc, self.S_lat, self.slope, self.z_s_ini, self.z_t_ini, self.c1, self.c2, self.c_eff, self.lambda_loss, self.An, self.An_prime, self.n_min, self.lbda, self.theta_cr, self.Sp, self.C_stara, \
            self.C_starb, self.C_starc, self.C_stard, self.qb_stara, self.qb_starb, self.lambda0a, self.lambda0b, self.cb_coef, self.b_eff_frac

            # The following parameters are modified during the simulation
            h_down, h_top, Ve_tot, Ct_star_top, Ct_star_down, C_star_top, C_star_down, q_star_top, q_star_down, dV_top, dV_down, Ae_tot_down,\
            Ae_tot_top, dze_down, dze_top, alpha, dz_b, z_s, z_t, Qb, z_b, U_b_top, U_b_down, Sd, ds, dx, db_top_up, db_top_down, db_down_up, db_down_down,\
            b_top_up, b_top_down, b_down_up, b_down_down, B_down, b_down, B_down_up, B_down_down, B_top, b_top, B_top_up,\
            B_top_down, Ct_out_top, Ct_out_down, n, n_prime, w_s, h_b, ze_down, H, btop_effMax =\
            self.h_down, self.h_top, self.Ve_tot, self.Ct_star_top, self.Ct_star_down, self.C_star_top, self.C_star_down, self.q_star_top, self.q_star_down, self.dV_top, self.dV_down, self.Ae_tot_down,\
            self.Ae_tot_top, self.dze_down, self.dze_top, self.alpha, self.dz_b, self.z_s, self.z_t, self.Qb, self.z_b, self.U_b_top, self.U_b_down, self.Sd, self.ds, self.dx, self.db_top_up, self.db_top_down, self.db_down_up, self.db_down_down,\
            self.b_top_up, self.b_top_down, self.b_down_up, self.b_down_down, self.B_down, self.b_down, self.B_down_up, self.B_down_down, self.B_top, self.b_top, self.B_top_up,\
            self.B_top_down, self.Ct_out_top, self.Ct_out_down, self.n, self.n_prime, self.w_s, self.h_b, self.ze_down, self.H, self.btop_effMax

            ## 1. Hydrodynamics
            # -----------------
            [H,B_w_down,A_down,R_down,tau_b_down,B_w_top,A_top,R_top,tau_b_top,h_top[t+1],h_down[t+1],Qb[t+1]] =\
                DLBreach_Modules.Hydrodynamics2D(self.hbreach[t+1,:],self.zbbreach[t+1,:],z_b[t],z_s[t+1],z_t[t+1],Qb[t+1],b_top[t],btop_effMax,b_down[t],abs(b_top_down[t]-b_down_down[t]),h_down[t],m_up,m_down,m_mean,dx[t],Su,Sd[t],rho,g,n)

            if self.breach_activated==False and Qb[t+1]>0:
                self.breach_activated=True

            ## 2. Sediment transport
            # ----------------------

            # 2.1) Settling velocity of sediments (w_s)
            # -----------------------------------------
            w_s_top = (1-Ct_out_top[t]/2)**4*w_s # Exponent -> [2.3;4.9] =4 for Wu
            w_s_down = (1-(Ct_out_down[t]+Ct_out_top[t])/2)**4*w_s

            # 2.2) Sediment Transport Capacity (downstream slope/top)
            # -------------------------------------------------------
            [Ct_star_top[t+1],q_star_top[t+1],C_star_top[t+1],U_b_top[t+1]] = DLBreach_Modules.Sediment_Transport_Capacity(Qb[t+1],A_top,R_top,rho_s,rho,g,w_s_top,d50,B_w_top,n,n_prime,tau_b_top,theta_cr,math.inf,phi,C_stara,C_starb,C_starc,C_stard,qb_stara,qb_starb,lambda0a,lambda0b,self.suspension)
            [Ct_star_down[t+1],q_star_down[t+1],C_star_down[t+1],U_b_down[t+1]]= DLBreach_Modules.Sediment_Transport_Capacity(Qb[t+1],A_down,R_down,rho_s,rho,g,w_s_down,d50,B_w_down,n,n_prime,tau_b_down,theta_cr,Sd[t],phi,C_stara,C_starb,C_starc,C_stard,qb_stara,qb_starb,lambda0a,lambda0b,self.suspension)

            # 2.3) Sediment concentrations
            # ----------------------------
            Ct_in_top=0               #[-] Hypo: clear water condition at the breach inlet
            [Ct_out_top[t+1], Ct_out_down[t+1], Ct_in_down] = DLBreach_Modules.Sediment_Concentrations(t, dx, ds, lbda, B_w_top, B_w_down, self.instant_equilibrium, Ct_star_top, Ct_star_down, Ct_in_top)

            # 2.4) Dike volume variation
            # --------------------------
            dV_top[t+1] = Qb[t+1]*(Ct_in_top-Ct_out_top[t+1])*dt/(1-p)      # Top
            dV_down[t+1] = Qb[t+1]*(Ct_in_down-Ct_out_down[t+1])*dt/(1-p)   # Downstream slope
            Ve_tot[t+1]=Ve_tot[t]+dV_top[t+1]+dV_down[t+1] # Total eroded volume

            ## 3. Morphodynamics
            # ------------------
            Ae_tot_top, Ae_tot_down, dze_top, dze_down, alpha, Sd, dz_b, z_b, delta_up, db_down_up, dB_down_up, delta_down, \
            db_down_down, dB_down_down, db_top_down, dB_top_down, db_top_up, dB_top_up = DLBreach_Modules.Dike_Morpho(np.array(self.ptsDS, dtype=np.float64), np.array(self.ptsUS, dtype=np.float64),\
                       dx, dx_min, ds, alpha, m_up, m_down, cb_coef, Lk, Su, Sd, h_d, h_b, z_b, dz_b, b_top, b_down, btop_effMax,\
                       Ae_tot_top, Ae_tot_down, dV_top[t+1], dV_down[t+1], dze_top, dze_down, b_top_down, b_down_down, b_down_up, B_down_up, B_down_down, t)

            ## 4. Update of geom. variables
            # -----------------------------
            H, h_b, dx, ds, m_up, m_down, m_mean, b_down_up, b_down_down, b_down, B_down, b_top_up, b_top_down, b_top, B_top, btop_effMax =\
                self.updateGeomVariables(t, z_s, z_b, h_d, ds, dx, dx_min, Lk, Sd, Su, m, b_top, b_down_up, db_down_up, b_down_down, db_down_down,\
                    delta_up, delta_down, B_down, b_down, B_down_up, b_top_up, b_top_down, db_top_up, db_top_down, B_top, btop_effMax, b_eff_frac)

            ## 5. Triangulation and data storage
            # ----------------------------------

            ## 5.1 Compute points coordinates + triangulation
            # -----------------------------------------------
            # Compute points coordinates + triangulation
            if self.breach_activated==False: # Initial shape of the dike
                self.ptsUS, self.ptsDS, self.coord_tri, self.idx_tri = PointsCoordinates.initialize(self.end_up, self.end_down, b_down[0], b_down_down, b_down_up, b_top[0], b_top_down, b_top_up, Lk, Sd, Su, h_d, h_b, z_b, m_down, m_up, dx, t+1, self.slope)
            else: # Altered shape of the dike
                self.ptsUS, self.ptsDS, self.coord_tri, self.idx_tri = PointsCoordinates.update(self.end_up, self.end_down, b_down[0], b_down_down, b_down_up, b_top[0], b_top_down, b_top_up, Lk, Sd, Su, h_d, h_b, z_b, m_down, m_up, dx, t, self.triangulate, self.slope)

            ## 5.2 Store triangulation and main outputs
            # -----------------------------------------
            # Origin of the coordinates = U/S extremity of the dike, at its toe located on the river/reservoir side
            self.coord_tri[:,0] -= min(self.coord_tri[:,0])
            self.coord_tri[:,1] -= min(self.coord_tri[:,1])
            self.coord_tri[:,2] += self.elevation_shift # Where elevation data are stored
            if self.riverbank == 'left': # Flip dike to match the MNT
                self.coord_tri[:,1] = -self.coord_tri[:,1]
            if self.horiz_rotation != 0:
                angle = self.horiz_rotation/180 * math.pi
                x_temp = self.coord_tri[:,0] * cos(angle) - self.coord_tri[:,1] * sin(angle)
                y_temp = self.coord_tri[:,0] * sin(angle) + self.coord_tri[:,1] * cos(angle)
                self.coord_tri[:,0], self.coord_tri[:,1] = x_temp, y_temp
            self.coord_tri[:,0] = self.coord_tri[:,0]+self.dike_origin[0]
            self.coord_tri[:,1] = self.coord_tri[:,1]-min(self.coord_tri[:,1])+self.dike_origin[1]
            self.interpMatrix.interpolate_on_triangulation(coords=self.coord_tri, triangles=self.idx_tri)
            self.topoArray[t+1,:,:] = self.interpMatrix.array.data
            self.topoArray[t+1,:,:] = np.fliplr(self.topoArray[t+1,:,:])
            if self.time[t+1] >= self.simu_duration-dt and self.saveTriangulation:
                PointsCoordinates.saveTriangulation(self.path_saveTri,self.nbx_topo,self.nby_topo,self.xmin_topo,self.ymin_topo,self.topoArray,self.time[t])

            if t==0:
                self.triangulation_dict = {}
                self.data_export = np.zeros((self.t_end_idx,8))
            self.triangulation_dict[int(t)] = {"time": float(t*dt),"XYZ": self.coord_tri.tolist(),"idx_triangles": self.idx_tri.tolist()}
            self.data_export[t,:] = [self.time[t], np.NaN, b_top_up[t]-m*h_b, b_top_down[t]+m*h_b, z_b[t],h_top[t+1], Qb[t+1],z_s[t],z_t[t]] # CHECK IF OUTPUTS CONSISTENT


            # THIS SHOULD BE MODIFIED
            if self.exportBreachWidth == True:
                if ((t+1) % 100) == 0:
                    mdic1 = {'Test' + str(self.Test_ID)+ '_BreachGeom' : self.data_export}
                    spio.savemat('Test' + str(self.Test_ID)+ '_BreachGeom.mat',mdic1)
                    mdic2 = {'Test' + str(self.Test_ID)+ '_UBreach' : self.Uybreach[0:t+1,:]}
                    spio.savemat('Test' + str(self.Test_ID)+ '_UBreach.mat',mdic2)
                    mdic3 = {'Test' + str(self.Test_ID)+ '_hBreach' : self.hbreach[0:t+1,:]}
                    spio.savemat('Test' + str(self.Test_ID)+ '_hBreach.mat',mdic3)
                    mdic4 = {'Test' + str(self.Test_ID)+ '_zbBreach' : self.zbbreach[0:t+1,:]}
                    spio.savemat('Test' + str(self.Test_ID)+ '_zbBreach.mat',mdic4)
                    # sys.exit() # To loop on different runs, os._exit might be useful : https://www.geeksforgeeks.org/python-exit-commands-quit-exit-sys-exit-and-os-_exit/


            ## 6. Update class variables
            # --------------------------
            self.h_down, self.h_top, self.Ve_tot, self.Ct_star_top, self.Ct_star_down, self.C_star_top, self.C_star_down, self.q_star_top, self.q_star_down, self.dV_top, self.dV_down, self.Ae_tot_down,\
            self.Ae_tot_top, self.dze_down, self.dze_top, self.alpha, self.dz_b, self.z_s, self.z_t, self.Qb, self.z_b, self.U_b_top, self.U_b_down, self.Sd, self.ds, self.dx, self.db_top_up, self.db_top_down, self.db_down_up, self.db_down_down,\
            self.b_top_up, self.b_top_down, self.b_down_up, self.b_down_down, self.B_down, self.b_down, self.B_down_up, self.B_down_down, self.B_top, self.b_top, self.B_top_up,\
            self.B_top_down, self.Ct_out_top, self.Ct_out_down, self.n, self.n_prime, self.w_s, self.h_b, self.ze_down, self.H, self.btop_effMax =\
            h_down, h_top, Ve_tot, Ct_star_top, Ct_star_down, C_star_top, C_star_down, q_star_top, q_star_down, dV_top, dV_down, Ae_tot_down,\
            Ae_tot_top, dze_down, dze_top, alpha, dz_b, z_s, z_t, Qb, z_b, U_b_top, U_b_down, Sd, ds, dx, db_top_up, db_top_down, db_down_up, db_down_down,\
            b_top_up, b_top_down, b_down_up, b_down_down, B_down, b_down, B_down_up, B_down_down, B_top, b_top, B_top_up,\
            B_top_down, Ct_out_top, Ct_out_down, n, n_prime, w_s, h_b, ze_down, H, btop_effMax



    def initializeVectors(self, t_end_idx, d50, An, An_prime, n_min, rho_s, rho, g, nu, Sp, h_b_ini, Sd_ini, Su, Lk, z_s_ini, z_t_ini, h_d, b_ini, m_up, m_down):
        """ Data initialization

        :param t_end_idx: [int] Number of time steps
        :param d50: [float] Median grain size
        :param An: [float] Empirical coef. (=16 for lab; =12 for field test) -> p.24 Wu 2016)
        :param An_prime: [float] Empirical coef. in particule Manning's coef. formula
        :param n_min: [float] Minimum value of Manning's coefficient
        :param rho_s: [float] Sediment density
        :param rho: [float] Water density
        :param g: [float] Gravitational acceleration
        :param nu: [float] Water kinematic viscosity
        :param Sp: [float] Corey shape factor (used in settling velocity)
        :param h_b_ini: [float] Initial breach depth
        :param Sd_ini: [float] Initial downstream slope (H/V)
        :param Su: [float] Upstream slope (H/V)
        :param Lk: [float] Dike crest width
        :param z_s_ini: [float] Initial water level in the main channel
        :param z_t_ini: [float] Initial water level in the floodplain
        :param h_d: [float] Dike height
        :param b_ini: [float] Initial breach bottom width
        :param m_up: [float] Upstream side slope of the breach (H/V)
        :param m_down: [float] Downstream side slope of the breach (H/V)
        :return: [np.array] Initialized vectors
        """

        # Memory preallocation (CPU optimization)
        time_length = t_end_idx+1
        h_down = np.zeros(time_length) # Initial water level on the downstream slope
        h_top = np.zeros(time_length)  # Initial water level on the flat top reach
        Ve_tot = np.zeros(time_length) # Initial eroded volume
        Ct_star_top = np.zeros(time_length)
        Ct_star_down = np.zeros(time_length)
        C_star_top = np.zeros(time_length)
        C_star_down = np.zeros(time_length)
        q_star_top = np.zeros(time_length)
        q_star_down = np.zeros(time_length)
        Ct_out_top = np.zeros(time_length) # Initial sediment concentrations
        Ct_out_down = np.zeros(time_length)
        dV_top = np.zeros(time_length)
        dV_down = np.zeros(time_length)
        Ae_tot_down = np.zeros(time_length)
        Ae_tot_top = np.zeros(time_length)
        dze_down = np.zeros(time_length)
        dze_top = np.zeros(time_length)
        alpha = np.zeros(time_length)
        dz_b = np.zeros(time_length)
        z_s= np.zeros(time_length)
        z_t= np.zeros(time_length)
        Qin_ = np.zeros(time_length)
        Qb = np.zeros(time_length)
        z_b = np.zeros(time_length)
        U_b_top = np.zeros(time_length)
        U_b_down = np.zeros(time_length)
        Sd = np.zeros(time_length)
        ds = np.zeros(time_length)
        dx = np.zeros(time_length)
        db_top_up = np.zeros(time_length)   #[m] Upstream breach bottom width increment
        db_top_down = np.zeros(time_length) #[m] Downstream breach bottom width increment
        b_down_up = np.zeros(time_length)
        b_top_up = np.zeros(time_length)
        b_down_down = np.zeros(time_length)
        b_top_down = np.zeros(time_length)
        B_down = np.zeros(time_length)
        B_top = np.zeros(time_length)
        b_down = np.zeros(time_length)
        b_top = np.zeros(time_length)

        # Manning roughness coefficient
        n=max(d50**(1./6.)/An,n_min)    #[s/m^(1/3)] Equal to 0.018 for Ismail p.39 Thesis
        n_prime = max(d50**(1./6.)/An_prime,n_min) #[s/m^(1/3)] Particule Manning coefficient

        # Settling velocity of sediments parameters
        # -----------------------------------------
        d_star = ((rho_s-rho)/rho*g/nu**2)**(1./3)*d50# [-] Adim. grain median size
        M=53.5*math.exp(-0.65*Sp)
        N=5.65*math.exp(-2.5*Sp)
        nn=0.7+0.9*Sp
        w_s = M*nu/(N*d50)*(sqrt(1./4+(4*N*d_star**3/(3*M**2))**(1./nn))-0.5)**nn #[m/s] Book "Computational River Dynamics", p.66 -> Used by Wu
        #w_s = nu/d50*(sqrt(25+1.2*d_star**2)-5)**1.5;#[m/s] Cheng (1997) + book Computational River Dynamics, p.62
        #w_s = 1.1*sqrt(g*(rho_s-rho)/rho*d50);     #[m/s] Used by Mike Eve

        # Geometrical parameters initialization
        # -------------------------------------
        h_b=h_b_ini      #[m] Breach depth
        ze_down=0        #[m] Mean erosion depth on downstream slope (perpendicular to the slope)
        Sd[0] = Sd_ini   #[-] Dike upstream slope
        z_s[0] = z_s_ini #[m] Water level in the main channel
        z_t[0] = z_t_ini #[m] Water level in the floodplain
        z_b[0] = h_d-h_b #[m] Breach bottom elevation (at flat top reach)
        H=z_s[0]-z_b[0]  #[m] Headwater level above the breach bottom
        V_FP = 0               #[m^3] Initial water volume in the floodplain
        breach_activated=False # Defines if breaching has been initiated
        # Flat top reach
        B_ini=b_ini+h_b_ini*(m_up+m_down) #[m] Initial breach top width
        b_top_up[0]=-b_ini/2              #[m] Initial location of breach upstream extremity (bottom)
        b_top_down[0]=b_top_up[0]+b_ini   #[m] Initial location of breach downstream extremity (bottom)
        B_top_up=b_top_up-m_up*h_b_ini    #[m] Initial location of breach upstream extremity (top)
        B_top_down=B_top_up+B_ini         #[m] Initial location of breach downstream extremity (top)
        dB_top_up=0        #[m] Upstream breach top width increment
        dB_top_down=0      #[m] Downstream breach top width increment
        B_top[0] = B_ini+dB_top_down-dB_top_up           #[m] Breach top width
        b_top[0] = b_ini+db_top_down[0]-db_top_up[0]  #[m] Breach bottom width
        btop_effMax = math.inf # Maximum effective breach width on flat top reach (used for erosion)
        dx[0]=Lk+h_d*Sd[0]-Sd[0]*z_b[0]+Su*h_b #[m] Initial breach bottom width (perpendicular to the main channel)
        # Downstream slope reach (no initial erosion on this side)
        b_down_up[0]=b_top_up[0]          #[m] Initial location of breach upstream extremity (bottom)
        b_down_down[0]=b_down_up[0]+b_ini #[m] Initial location of breach downstream extremity (bottom)
        B_down_up=b_down_up[0]            #[m] Initial location of breach upstream extremity (top)
        B_down_down=b_down_down[0]        #[m] Initial location of breach downstream extremity (top)
        db_down_up=0        #[m] Upstream breach bottom width increment
        db_down_down=0      #[m] Downstream breach bottom width increment
        b_down[0] = b_ini+db_down_down-db_down_up    #[m] Breach bottom width
        B_down[0] = b_down[0]                        #[m] Breach top width
        ds[0]=z_b[0]*sqrt(1+Sd[0]**2)          #[m] Initial length of the breach downstream side slope (perpendicular to the main channel)

        return h_down, h_top, Ve_tot, Ct_star_top, Ct_star_down, C_star_top, C_star_down, q_star_top, q_star_down, dV_top, dV_down, Ae_tot_down,\
            Ae_tot_top, dze_down, dze_top, alpha, dz_b, z_s, z_t, Qin_, Qb, z_b, U_b_top, U_b_down, Sd, ds, dx, db_top_up, db_top_down, db_down_up, db_down_down,\
            b_top_up, b_top_down, b_down_up, b_down_down, B_down, b_down, B_down_up, B_down_down, B_top, b_top, B_top_up,\
            B_top_down, Ct_out_top, Ct_out_down, n, n_prime, w_s, h_b, ze_down, H, V_FP, breach_activated, btop_effMax

    def updateGeomVariables(self, t, z_s, z_b, h_d, ds, dx, dx_min, Lk, Sd, Su, m, b_top, b_down_up, db_down_up, b_down_down, db_down_down, delta_up, delta_down,\
        B_down, b_down, B_down_up, b_top_up, b_top_down, db_top_up, db_top_down, B_top, btop_effMax, b_eff_frac):
        """
        :param t: int Current time step
        :param z_s: np.array Water level in the main channel
        :param z_b: np.array Breach bottom elevation (at flat top reach)
        :param h_d: float Dike height
        :param ds: np.array Length of the breach downstream side slope (perpendicular to the main channel)
        :param dx: np.array Breach bottom length (perpendicular to the main channel)
        :param dx_min: float Minimum breach bottom length
        :param Lk: float Length of the breach
        :param Sd: np.array Dike upstream slope
        :param Su: float Dike downstream slope
        :param m: float Breach side slope
        :param b_top: np.array Breach bottom width on the flat top reach
        :param b_down_up: np.array Location of breach upstream extremity (bottom)
        :param db_down_up: float Upstream breach bottom width increment
        :param b_down_down: np.array Location of breach downstream extremity (bottom)
        :param db_down_down: float Downstream breach bottom width increment
        :param delta_up: float Upstream breach top width increment
        :param delta_down: float Downstream breach top width increment
        :param B_down: np.array Breach top width
        :param b_down: np.array Breach bottom width on the downstream slope
        :param B_down_up: np.array Location of breach upstream extremity (top)
        :param b_top_up: np.array Location of breach upstream extremity (bottom)
        :param b_top_down: np.array Location of breach downstream extremity (bottom)
        :param db_top_up: np.array Upstream breach top width increment
        :param db_top_down: np.array Downstream breach top width increment
        :param B_top: np.array Breach top width
        :param btop_effMax: float Maximum effective breach width on flat top reach (used for erosion)
        :param b_eff_frac: float Fraction of the breach width considered as effective (cfr effective breach width). If >=1, full breach used
        :return: float, float, np.array, np.array, float, float, float, np.array, np.array, np.array, np.array, np.array, np.array, np.array, np.array, np.array, float
        """

        # General
        H = max(z_s[t+1]-z_b[t+1],0)
        h_b = h_d-z_b[t+1]
        if dx[t]==dx_min:
            dx[t+1]=dx_min
        else:
            if Sd[t+1]==math.inf:
                dx[t+1]=dx[t]
            else:
                dx[t+1]=max(Lk+h_d*Sd[0]-Sd[t+1]*z_b[t+1]+Su*h_b,dx_min)
        ds[t+1]=max(0,((Lk+(Sd[0]+Su)*h_d)-dx[t+1]-z_b[t+1]*Su)/cos(atan(1./Sd[t+1])))
        if z_b[t+1]==0:
            m_up = m   #(B_down_up[t+1]-b_down_up[t+1])/h_b;
            m_down = m #(B_down_down[t+1]-b_down_down[t+1])/h_b;
        else:
            m_up = m   #(B_top_up[t+1]-b_top_up[t+1])/h_b;
            m_down = m #(B_top_down[t+1]-b_top_down[t+1])/h_b;
        m_mean = (abs(m_down)+abs(m_up))/2

        # Downstream slope reach
        if b_top[t]< btop_effMax:
            b_down_up[t+1]= b_down_up[t]-abs(db_down_up)
            B_down_up = b_down_up[t+1]-delta_up
        else: # Breach upstream extremities are unchanged
            b_down_up[t+1] = b_down_up[t]
        b_down_down[t+1] = b_down_down[t]+abs(db_down_down)
        B_down_down = b_down_down[t+1]+delta_down
        B_down[t+1] = B_down_down-B_down_up
        b_down[t+1] = b_down_down[t+1]-b_down_up[t+1]
        # Flat top reach
        if dx[t+1]==0 or z_b[t+1]==0:
            if z_b[t+1]==0:
                b_top_up[t+1] = b_down_up[t+1]
                b_top_down[t+1] = b_down_down[t+1]
                b_top[t+1] = b_down[t+1]
                B_top_up = b_top_up[t+1]-m_up*(h_d-z_b[t+1])
                B_top_down = b_top_down[t+1]+m_down*(h_d-z_b[t+1])
                B_top[t+1] = B_top_down-B_top_up
                B_down[t+1] = B_top[t+1]
            else: # Not super rigorous
                B_top_up = B_down_up
                B_top_down = B_down_down
                B_top[t+1] = B_down[t+1]
                b_top_up[t+1] = b_down_up[t+1]
                b_top_down[t+1] = b_down_down[t+1]
                b_top[t+1] = b_down[t+1] # b_down can become HUGE when Ae_tot_down -> 0 : dangerous condition
        else:
            if b_top[t]< btop_effMax:
                b_top_up[t+1] = max(b_top_up[t]-abs(db_top_up),b_down_up[t+1])         # Breach bottom width on flat top reach is always smaller than breach bottom width on D/S reach
                B_top_up = b_top_up[t+1]-m_up*(h_d-z_b[t+1])
            else: # Breach upstream extremities are unchanged
                b_top_up[t+1] = b_top_up[t]
            b_top_down[t+1] = min(b_top_down[t]+abs(db_top_down),b_down_down[t+1])
            b_top[t+1] = b_top_down[t+1]-b_top_up[t+1]
            B_top_down = b_top_down[t+1]+m_down*(h_d-z_b[t+1])
            B_top[t+1] = B_top_down-B_top_up
        if z_b[t+1]>0:
            btop_effMax = math.inf # Symmetric breach expansion
        else:
            btop_effMax = b_top[t+1]*b_eff_frac # Non-symmetric breach expansion

        return H, h_b, dx, ds, m_up, m_down, m_mean, b_down_up, b_down_down, b_down, B_down, b_top_up, b_top_down, b_top, B_top, btop_effMax
