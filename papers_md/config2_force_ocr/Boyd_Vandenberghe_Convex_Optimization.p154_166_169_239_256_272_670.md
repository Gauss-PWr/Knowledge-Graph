- • If  $P$  is singular, but  $q \in \mathcal{R}(P)$ , then the set of optimal points is the (affine) set  $X_{\text{opt}} = -P^\dagger q + \mathcal{N}(P)$ , where  $P^\dagger$  denotes the pseudo-inverse of  $P$  (see �A.5.4).

**Example 4.6** *Analytic centering.* Consider the (unconstrained) problem of minimizing the (convex) function  $f_0 : \mathbf{R}^n \rightarrow \mathbf{R}$ , defined as

$$f_0(x) = - \sum_{i=1}^m \log(b_i - a_i^T x), \quad \mathbf{dom} f_0 = \{x \mid Ax \prec b\},$$

where  $a_1^T, \dots, a_m^T$  are the rows of  $A$ . The function  $f_0$  is differentiable, so the necessary and sufficient conditions for  $x$  to be optimal are

$$Ax \prec b, \quad \nabla f_0(x) = \sum_{i=1}^m \frac{1}{b_i - a_i^T x} a_i = 0. \quad (4.23)$$

(The condition  $Ax \prec b$  is just  $x \in \mathbf{dom} f_0$ .) If  $Ax \prec b$  is infeasible, then the domain of  $f_0$  is empty. Assuming  $Ax \prec b$  is feasible, there are still several possible cases (see exercise 4.2):

- • There are no solutions of (4.23), and hence no optimal points for the problem. This occurs if and only if  $f_0$  is unbounded below.
- • There are many solutions of (4.23). In this case it can be shown that the solutions form an affine set.
- • There is a unique solution of (4.23), *i.e.*, a unique minimizer of  $f_0$ . This occurs if and only if the open polyhedron  $\{x \mid Ax \prec b\}$  is nonempty and bounded.

### Problems with equality constraints only

Consider the case where there are equality constraints but no inequality constraints, *i.e.*,

$$\begin{aligned} & \text{minimize} & f_0(x) \\ & \text{subject to} & Ax = b. \end{aligned}$$

Here the feasible set is affine. We assume that it is nonempty; otherwise the problem is infeasible. The optimality condition for a feasible  $x$  is that

$$\nabla f_0(x)^T (y - x) \geq 0$$

must hold for all  $y$  satisfying  $Ay = b$ . Since  $x$  is feasible, every feasible  $y$  has the form  $y = x + v$  for some  $v \in \mathcal{N}(A)$ . The optimality condition can therefore be expressed as:

$$\nabla f_0(x)^T v \geq 0 \text{ for all } v \in \mathcal{N}(A).$$

If a linear function is nonnegative on a subspace, then it must be zero on the subspace, so it follows that  $\nabla f_0(x)^T v = 0$  for all  $v \in \mathcal{N}(A)$ . In other words,

$$\nabla f_0(x) \perp \mathcal{N}(A).$$

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

achieving a minimum acceptable mean return  $r_{\min}$ , and satisfying the portfolio budget and no-shorting constraints.

Many extensions are possible. One standard extension, for example, is to allow short positions, *i.e.*,  $x_i < 0$ . To do this we introduce variables  $x_{\text{long}}$  and  $x_{\text{short}}$ , with

$$x_{\text{long}} \succeq 0, \quad x_{\text{short}} \succeq 0, \quad x = x_{\text{long}} - x_{\text{short}}, \quad \mathbf{1}^T x_{\text{short}} \leq \eta \mathbf{1}^T x_{\text{long}}.$$

The last constraint limits the total short position at the beginning of the period to some fraction  $\eta$  of the total long position at the beginning of the period.

As another extension we can include linear transaction costs in the portfolio optimization problem. Starting from a given initial portfolio  $x_{\text{init}}$  we buy and sell assets to achieve the portfolio  $x$ , which we then hold over the period as described above. We are charged a transaction fee for buying and selling assets, which is proportional to the amount bought or sold. To handle this, we introduce variables  $u_{\text{buy}}$  and  $u_{\text{sell}}$ , which determine the amount of each asset we buy and sell before the holding period. We have the constraints

$$x = x_{\text{init}} + u_{\text{buy}} - u_{\text{sell}}, \quad u_{\text{buy}} \succeq 0, \quad u_{\text{sell}} \succeq 0.$$

We replace the simple budget constraint  $\mathbf{1}^T x = 1$  with the condition that the initial buying and selling, including transaction fees, involves zero net cash:

$$(1 - f_{\text{sell}}) \mathbf{1}^T u_{\text{sell}} = (1 + f_{\text{buy}}) \mathbf{1}^T u_{\text{buy}}$$

Here the lefthand side is the total proceeds from selling assets, less the selling transaction fee, and the righthand side is the total cost, including transaction fee, of buying assets. The constants  $f_{\text{buy}} \geq 0$  and  $f_{\text{sell}} \geq 0$  are the transaction fee rates for buying and selling (assumed the same across assets, for simplicity).

The problem of minimizing return variance, subject to a minimum mean return, and the budget and trading constraints, is a QP with variables  $x$ ,  $u_{\text{buy}}$ ,  $u_{\text{sell}}$ .

#### 4.4.2 Second-order cone programming

A problem that is closely related to quadratic programming is the *second-order cone program* (SOCP):

$$\begin{aligned} & \text{minimize} & & f^T x \\ & \text{subject to} & & \|A_i x + b_i\|_2 \leq c_i^T x + d_i, \quad i = 1, \dots, m \\ & & & Fx = g, \end{aligned} \tag{4.36}$$

where  $x \in \mathbf{R}^n$  is the optimization variable,  $A_i \in \mathbf{R}^{n_i \times n}$ , and  $F \in \mathbf{R}^{p \times n}$ . We call a constraint of the form

$$\|Ax + b\|_2 \leq c^T x + d,$$

where  $A \in \mathbf{R}^{k \times n}$ , a *second-order cone constraint*, since it is the same as requiring the affine function  $(Ax + b, c^T x + d)$  to lie in the second-order cone in  $\mathbf{R}^{k+1}$ .

When  $c_i = 0$ ,  $i = 1, \dots, m$ , the SOCP (4.36) is equivalent to a QCQP (which is obtained by squaring each of the constraints). Similarly, if  $A_i = 0$ ,  $i = 1, \dots, m$ , then the SOCP (4.36) reduces to a (general) LP. Second-order cone programs are, however, more general than QCQPs (and of course, LPs).

We refer to the difference  $p^* - d^*$  as the *optimal duality gap* of the original problem, since it gives the gap between the optimal value of the primal problem and the best (*i.e.*, greatest) lower bound on it that can be obtained from the Lagrange dual function. The optimal duality gap is always nonnegative.

The bound (5.23) can sometimes be used to find a lower bound on the optimal value of a problem that is difficult to solve, since the dual problem is always convex, and in many cases can be solved efficiently, to find  $d^*$ . As an example, consider the two-way partitioning problem (5.7) described on page 219. The dual problem is an SDP,

$$\begin{aligned} & \text{maximize} \quad -\mathbf{1}^T \nu \\ & \text{subject to} \quad W + \mathbf{diag}(\nu) \succeq 0, \end{aligned}$$

with variable  $\nu \in \mathbf{R}^n$ . This problem can be solved efficiently, even for relatively large values of  $n$ , such as  $n = 1000$ . Its optimal value is a lower bound on the optimal value of the two-way partitioning problem, and is always at least as good as the lower bound (5.8) based on  $\lambda_{\min}(W)$ .

### 5.2.3 Strong duality and Slater's constraint qualification

If the equality

$$d^* = p^* \quad (5.24)$$

holds, *i.e.*, the optimal duality gap is zero, then we say that *strong duality* holds. This means that the best bound that can be obtained from the Lagrange dual function is tight.

Strong duality does not, in general, hold. But if the primal problem (5.1) is convex, *i.e.*, of the form

$$\begin{aligned} & \text{minimize} \quad f_0(x) \\ & \text{subject to} \quad f_i(x) \leq 0, \quad i = 1, \dots, m, \\ & \quad Ax = b, \end{aligned} \quad (5.25)$$

with  $f_0, \dots, f_m$  convex, we usually (but not always) have strong duality. There are many results that establish conditions on the problem, beyond convexity, under which strong duality holds. These conditions are called *constraint qualifications*.

One simple constraint qualification is *Slater's condition*: There exists an  $x \in \mathbf{relint} \mathcal{D}$  such that

$$f_i(x) < 0, \quad i = 1, \dots, m, \quad Ax = b. \quad (5.26)$$

Such a point is sometimes called *strictly feasible*, since the inequality constraints hold with strict inequalities. Slater's theorem states that strong duality holds, if Slater's condition holds (and the problem is convex).

Slater's condition can be refined when some of the inequality constraint functions  $f_i$  are affine. If the first  $k$  constraint functions  $f_1, \dots, f_k$  are affine, then strong duality holds provided the following weaker condition holds: There exists an  $x \in \mathbf{relint} \mathcal{D}$  with

$$f_i(x) \leq 0, \quad i = 1, \dots, k, \quad f_i(x) < 0, \quad i = k+1, \dots, m, \quad Ax = b. \quad (5.27)$$

We can draw several interesting conclusions from this. For example, since the inequality in the third line is an equality, we conclude that  $x^*$  minimizes  $L(x, \lambda^*, \nu^*)$  over  $x$ . (The Lagrangian  $L(x, \lambda^*, \nu^*)$  can have other minimizers;  $x^*$  is simply a minimizer.)

Another important conclusion is that

$$\sum_{i=1}^m \lambda_i^* f_i(x^*) = 0.$$

Since each term in this sum is nonpositive, we conclude that

$$\lambda_i^* f_i(x^*) = 0, \quad i = 1, \dots, m. \quad (5.48)$$

This condition is known as *complementary slackness*; it holds for any primal optimal  $x^*$  and any dual optimal  $(\lambda^*, \nu^*)$  (when strong duality holds). We can express the complementary slackness condition as

$$\lambda_i^* > 0 \implies f_i(x^*) = 0,$$

or, equivalently,

$$f_i(x^*) < 0 \implies \lambda_i^* = 0.$$

Roughly speaking, this means the  $i$ th optimal Lagrange multiplier is zero unless the  $i$ th constraint is active at the optimum.

### 5.5.3 KKT optimality conditions

We now assume that the functions  $f_0, \dots, f_m, h_1, \dots, h_p$  are differentiable (and therefore have open domains), but we make no assumptions yet about convexity.

#### KKT conditions for nonconvex problems

As above, let  $x^*$  and  $(\lambda^*, \nu^*)$  be any primal and dual optimal points with zero duality gap. Since  $x^*$  minimizes  $L(x, \lambda^*, \nu^*)$  over  $x$ , it follows that its gradient must vanish at  $x^*$ , *i.e.*,

$$\nabla f_0(x^*) + \sum_{i=1}^m \lambda_i^* \nabla f_i(x^*) + \sum_{i=1}^p \nu_i^* \nabla h_i(x^*) = 0.$$

Thus we have

$$\begin{aligned} f_i(x^*) &\leq 0, \quad i = 1, \dots, m \\ h_i(x^*) &= 0, \quad i = 1, \dots, p \\ \lambda_i^* &\geq 0, \quad i = 1, \dots, m \\ \lambda_i^* f_i(x^*) &= 0, \quad i = 1, \dots, m \\ \nabla f_0(x^*) + \sum_{i=1}^m \lambda_i^* \nabla f_i(x^*) + \sum_{i=1}^p \nu_i^* \nabla h_i(x^*) &= 0, \end{aligned} \quad (5.49)$$

which are called the *Karush-Kuhn-Tucker* (KKT) conditions.

To summarize, for *any* optimization problem with differentiable objective and constraint functions for which strong duality obtains, any pair of primal and dual optimal points must satisfy the KKT conditions (5.49).

which is the same as the dual function for the optimization problem (5.73). Since  $f_0 = 0$ , the dual function is positive homogeneous in  $(\lambda, \nu)$ : For  $\alpha > 0$ ,  $g(\alpha\lambda, \alpha\nu) = \alpha g(\lambda, \nu)$ . The dual problem associated with (5.73) is to maximize  $g(\lambda, \nu)$  subject to  $\lambda \succeq 0$ . Since  $g$  is homogeneous, the optimal value of this dual problem is given by

$$d^* = \begin{cases} \infty & \lambda \succeq 0, g(\lambda, \nu) > 0 \text{ is feasible} \\ 0 & \lambda \succeq 0, g(\lambda, \nu) > 0 \text{ is infeasible.} \end{cases} \tag{5.75}$$

Weak duality tells us that  $d^* \leq p^*$ . Combining this fact with (5.74) and (5.75) yields the following: If the inequality system

$$\lambda \succeq 0, \quad g(\lambda, \nu) > 0 \tag{5.76}$$

is feasible (which means  $d^* = \infty$ ), then the inequality system (5.72) is infeasible (since we then have  $p^* = \infty$ ). Indeed, we can interpret any solution  $(\lambda, \nu)$  of the inequalities (5.76) as a *proof* or *certificate* of infeasibility of the system (5.72).

We can restate this implication in terms of feasibility of the original system: If the original inequality system (5.72) is feasible, then the inequality system (5.76) must be infeasible. We can interpret an  $x$  which satisfies (5.72) as a certificate establishing infeasibility of the inequality system (5.76).

Two systems of inequalities (and equalities) are called *weak alternatives* if at most one of the two is feasible. Thus, the systems (5.72) and (5.76) are weak alternatives. This is true whether or not the inequalities (5.72) are convex (*i.e.*,  $f_i$  convex,  $h_i$  affine); moreover, the alternative inequality system (5.76) is always convex (*i.e.*,  $g$  is concave and the constraints  $\lambda_i \geq 0$  are convex).

### Strict inequalities

We can also study feasibility of the *strict* inequality system

$$f_i(x) < 0, \quad i = 1, \dots, m, \quad h_i(x) = 0, \quad i = 1, \dots, p. \tag{5.77}$$

With  $g$  defined as for the nonstrict inequality system, we have the alternative inequality system

$$\lambda \succeq 0, \quad \lambda \neq 0, \quad g(\lambda, \nu) \geq 0. \tag{5.78}$$

We can show directly that (5.77) and (5.78) are weak alternatives. Suppose there exists an  $\tilde{x}$  with  $f_i(\tilde{x}) < 0$ ,  $h_i(\tilde{x}) = 0$ . Then for any  $\lambda \succeq 0$ ,  $\lambda \neq 0$ , and  $\nu$ ,

$$\lambda_1 f_1(\tilde{x}) + \dots + \lambda_m f_m(\tilde{x}) + \nu_1 h_1(\tilde{x}) + \dots + \nu_p h_p(\tilde{x}) < 0.$$

It follows that

$$\begin{aligned} g(\lambda, \nu) &= \inf_{x \in \mathcal{D}} \left( \sum_{i=1}^m \lambda_i f_i(x) + \sum_{i=1}^p \nu_i h_i(x) \right) \\ &\leq \sum_{i=1}^m \lambda_i f_i(\tilde{x}) + \sum_{i=1}^p \nu_i h_i(\tilde{x}) \\ &< 0. \end{aligned}$$

We need to show that  $w = (x^T Ax, x^T Bx)$  for some  $x$ .

We distinguish two cases. First, assume  $(0, \gamma)$  is a linear combination of the vectors  $(\lambda_1, \sigma_1)$  and  $(\lambda_2, \sigma_2)$ :

$$0 = z_1\lambda_1 + z_2\lambda_2, \quad \gamma = z_1\sigma_1 + z_2\sigma_2,$$

for some  $z_1, z_2$ . In this case we choose  $x = \alpha v_1 + \beta v_2$ , where  $\alpha$  and  $\beta$  are determined by solving two quadratic equations in two variables

$$\alpha^2 + 2\alpha\beta z_1 = 1, \quad \beta^2 + 2\alpha\beta z_2 = 1. \quad (\text{B.9})$$

This will give the desired result, since

$$\begin{aligned} & \begin{bmatrix} (\alpha v_1 + \beta v_2)^T A(\alpha v_1 + \beta v_2) \\ (\alpha v_1 + \beta v_2)^T B(\alpha v_1 + \beta v_2) \end{bmatrix} \\ &= \alpha^2 \begin{bmatrix} \lambda_1 \\ \sigma_1 \end{bmatrix} + 2\alpha\beta \begin{bmatrix} 0 \\ \gamma \end{bmatrix} + \beta^2 \begin{bmatrix} \lambda_2 \\ \sigma_2 \end{bmatrix} \\ &= (\alpha^2 + 2\alpha\beta z_1) \begin{bmatrix} \lambda_1 \\ \sigma_1 \end{bmatrix} + (\beta^2 + 2\alpha\beta z_2) \begin{bmatrix} \lambda_2 \\ \sigma_2 \end{bmatrix} \\ &= \begin{bmatrix} \lambda_1 + \lambda_2 \\ \sigma_1 + \sigma_2 \end{bmatrix}. \end{aligned}$$

It remains to show that the equations (B.9) are solvable. To see this, we first note that  $\alpha$  and  $\beta$  must be nonzero, so we can write the equations equivalently as

$$\alpha^2(1 + 2(\beta/\alpha)z_1) = 1, \quad (\beta/\alpha)^2 + 2(\beta/\alpha)(z_2 - z_1) = 1.$$

The equation  $t^2 + 2t(z_2 - z_1) = 1$  has a positive and a negative root. At least one of these roots (the root with the same sign as  $z_1$ ) satisfies  $1 + 2tz_1 > 0$ , so we can choose

$$\alpha = \pm 1/\sqrt{1 + 2tz_1}, \quad \beta = t\alpha.$$

This yields two solutions  $(\alpha, \beta)$  that satisfy (B.9). (If both roots of  $t^2 + 2t(z_2 - z_1) = 1$  satisfy  $1 + 2tz_1 > 0$ , we obtain four solutions.)

Next, assume that  $(0, \gamma)$  is not a linear combination of  $(\lambda_1, \sigma_1)$  and  $(\lambda_2, \sigma_2)$ . In particular, this means that  $(\lambda_1, \sigma_1)$  and  $(\lambda_2, \sigma_2)$  are linearly dependent. Therefore their sum  $w = (\lambda_1 + \lambda_2, \sigma_1 + \sigma_2)$  is a nonnegative multiple of  $(\lambda_1, \sigma_1)$ , or  $(\lambda_2, \sigma_2)$ , or both. If  $w = \alpha^2(\lambda_1, \sigma_1)$  for some  $\alpha$ , we can choose  $x = \alpha v_1$ . If  $w = \beta^2(\lambda_2, \sigma_2)$  for some  $\beta$ , we can choose  $x = \beta v_2$ .

## B.4 Proofs of the strong duality results

We first prove the S-procedure result given in �B.2. The assumption of strict feasibility of  $\hat{x}$  implies that the matrix

$$\begin{bmatrix} A_2 & b_2 \\ b_2^T & c_2 \end{bmatrix}$$