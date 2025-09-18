import cvxpy as cp
import numpy as np

def create_problem(G_u, c_u, c_w, G_w_hat, G_omega, c_omega, A_hat, B_hat, u_eq, x_eq):
    r"""Function responsible for creating the problem in cvxpy and parametrize the variables to reduce the running time of the solving part as a whole
    Args:
        the same arguments as the ones required to solve the problem per say, they are: G_u, c_u, c_w, G_w_hat, G_omega, c_omega, A_hat, B_hat, and;
    """

    # Create variable u and parameter u_rl
    u = cp.Variable(c_u.shape[0])
    u_rl = cp.Parameter(c_u.shape[0])

    # Create variables Theta and theta
    theta = cp.Variable(G_omega.shape[1])
    Theta = cp.Variable((G_omega.shape[1], G_w_hat.shape[1]))
    lamb = cp.Variable(G_u.shape[0])
    sigma_lamb = cp.Variable(G_u.shape[0])
    sigma_Theta = cp.Variable((G_omega.shape[1], 1))

    # Create our second parameter: x_k
    x_k = cp.Parameter(A_hat.shape[0])

    constraints = [
        sigma_lamb >= np.zeros(sigma_lamb.shape),
        sigma_Theta >= np.zeros(sigma_Theta.shape),
        u == c_u + G_u @ lamb,
        cp.norm(lamb, "inf") <= 1 + sigma_lamb,
        (A_hat @ (x_k - x_eq)) + (B_hat @ (u - u_eq)) + c_w + x_eq == c_omega - (G_omega @ theta),
        G_w_hat == (G_omega @ Theta),
        cp.abs(cp.reshape(theta, (G_omega.shape[1], 1))) + cp.abs(Theta) @ np.ones((G_w_hat.shape[1], 1))
        <= np.ones((G_omega.shape[1], 1)) + sigma_Theta,
        # cp.abs(Theta) @ np.ones((G_w_hat.shape[1], 1)) <= np.ones((G_omega.shape[1], 1)),
    ]

    objective = cp.Minimize(
        cp.square(cp.norm(u - u_rl, 2))            
        + 1e3 * np.ones((1, G_omega.shape[1])) @ sigma_Theta
        + 1e3 * np.ones((1, G_u.shape[1])) @ sigma_lamb
        )

    prob = cp.Problem(objective, constraints)

    # Return the problem, the variable of interest and the parameters (notice that we're not solving anything in this
    # function, only building the basis of the solving procedure)
    return prob, u_rl, x_k, u