**Figure 4.5** Geometric illustration of QP. The feasible set  $\mathcal{P}$ , which is a polyhedron, is shown shaded. The contour lines of the objective function, which is convex quadratic, are shown as dashed curves. The point  $x^*$  is optimal.

where  $P_i \in \mathbf{S}_+^n$ ,  $i = 0, 1, \dots, m$ , the problem is called a *quadratically constrained quadratic program* (QCQP). In a QCQP, we minimize a convex quadratic function over a feasible region that is the intersection of ellipsoids (when  $P_i \succ 0$ ).

Quadratic programs include linear programs as a special case, by taking  $P = 0$  in (4.34). Quadratically constrained quadratic programs include quadratic programs (and therefore also linear programs) as a special case, by taking  $P_i = 0$  in (4.35), for  $i = 1, \dots, m$ .

## 4.4.1 Examples

### Least-squares and regression

The problem of minimizing the convex quadratic function

$$\|Ax - b\|_2^2 = x^T A^T Ax - 2b^T Ax + b^T b$$

is an (unconstrained) QP. It arises in many fields and has many names, *e.g., regression analysis* or *least-squares approximation*. This problem is simple enough to have the well known analytical solution  $x = A^\dagger b$ , where  $A^\dagger$  is the pseudo-inverse of  $A$  (see �A.5.4).

When linear inequality constraints are added, the problem is called *constrained regression* or *constrained least-squares*, and there is no longer a simple analytical solution. As an example we can consider regression with lower and upper bounds on the variables, *i.e.*,

$$\begin{aligned} \text{minimize} \quad & \|Ax - b\|_2^2 \\ \text{subject to} \quad & l_i \leq x_i \leq u_i, \quad i = 1, \dots, n, \end{aligned}$$