import math

class BusModel(object):
    g = 9.81
    def __init__(self, M, p_a, A_f, C_d, P_tire, R_W, n_t, p_rot_in=0.1):
        self.M = M
        self.M_equ = M * p_rot_in
        self.p_a = p_a
        self.A_f = A_f
        self.C_d = C_d
        self.P_tire = P_tire
        self.R_W = R_W
        self.n_t = n_t
    
    def T_M(self):
        pass

    def F_total(self, V, V_wind, alpha):
        return self.F_a(V, V_wind) + self.F_r(V, alpha) + self.F_g(alpha) + self.F_acc(0)

    def F_a(self, V, V_wind):
        return 0.5 * self.p_a + self.A_f + self.C_d * (self.V_eff(V, V_wind) ** 2)

    def V_eff(self, V, V_wind):
        return V - V_wind
    
    def F_r(self, V, alpha):
        return self.C_r(V) * self.M * self.g * math.cos(alpha)

    def C_r(self, V):
        return 0.005 + (1/self.P_tire) * (0.01 + 0.0095 * (V/100) **2 )
    
    def F_g(self, alpha):
        return self.M * self.g * math.sin(alpha)
    
    def F_MW(self, T_M, omega_M, V):
        return (1/self.R_W) * self.T_W(T_M, omega_M, V)

    def T_W(self, T_M, omega_M, V):
        return self.n_t * T_M * (omega_M/self.omega_W(V))

    def omega_W(self, V):
        return (V * 1e3)/self.R_W

    def F_acc(self, t):
        return 0
