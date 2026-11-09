**Figure 4.5** Geometric illustration of QP. The feasible set  $\mathcal{P}$ , which is a polyhedron, is shown shaded. The contour lines of the objective function, which is convex quadratic, are shown as dashed curves. The point  $x^*$  is optimal.

where  $P_i \in \mathbf{S}_+^n$ ,  $i = 0, 1, \dots, m$ , the problem is called a *quadratically constrained quadratic program* (QCQP). In a CQP, we minimize a convex quadratic function over a feasible region that is the intersection of ellipsoids (when  $P_i \succ 0$ ).

Quadratic programs include linear programs as a special case, by taking  $P = 0$  in (4.34). Quadratically constrained quadratic programs include quadratic programs (and therefore also linear programs) as a special case, by taking  $P_i = 0$  in (4.35), for  $i = 1, \dots, m$ .

## 4.4.1 Examples

$$\|Ax - b\|_2^2 = x^T A^T Ax - 2b^T Ax + b^T b$$

$$\begin{aligned} \text{minimize} & \quad \|Ax - b\|_2^2 \\ \text{subject to} & \quad l_i \leq x_i \leq u_i, \quad i = 1, \dots, n, \end{aligned}$$