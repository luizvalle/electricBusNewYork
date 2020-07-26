import numpy as np

class BusModel(object):
    g = 9.81 # m/s^2 (acceleration of free-fall due to gravity)
    p_a = 1.225 # (density of air) kg/m^3
    C_d = 0.7 # (drag coefficient)
    def __init__(self, M, A_f, P_tire, R_W, lambd=1, n_t=0.8, p_rot_in=0.1):
        self.M = M # Vehicle mass (kg)
        self.M_equ = M * p_rot_in # Rotation inertia (kg)
        self.A_f = A_f # Frontal area (m^2)
        self.P_tire = P_tire # Tire pressure (bars)
        self.R_W = R_W # Wheel radius (m)
        self.lambd = lambd # Final transmission efficiency * gear ratio
        self.n_t = n_t # Overrall transmission efficiency
    
    def P_M(self, V, dV_dT, V_wind=0, alpha=0):
        return self._T_M(V, dV_dT, V_wind, alpha) * self._omega_M(V) # W
    
    def _omega_M(self, V):
        return V / self.R_W # radians/second
    
    def _T_M(self, V, dV_dT, V_wind, alpha):
        return (self.lambd/self.n_t) * self.R_W * (self._F_total(V, V_wind, alpha) + (self.M + self.M_equ) * dV_dT) # Nm
    
    def _F_total(self, V, V_wind, alpha=0):
        return self._F_a(V, V_wind) + self._F_r(V, alpha) + self._F_g(alpha) # N
    
    def _F_a(self, V, V_wind):
        return 0.5 * self.p_a * self.A_f * self.C_d * np.square(V - V_wind) # N
    
    def _F_r(self, V, alpha):
        return self._C_r(V) * self.M * self.g * np.cos(alpha) # N
    
    def _C_r(self, V):
        return 0.005 + (1 / self.P_tire) * (0.01 + 0.0095 * np.square(V * 3600 / 100000))
    
    def _F_g(self, alpha):
        return self.M * self.g * np.sin(alpha) # N
