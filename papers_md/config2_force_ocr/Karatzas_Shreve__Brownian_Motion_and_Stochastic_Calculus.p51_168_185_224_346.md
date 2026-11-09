- (i)  $\langle \alpha X + \beta Y, Z \rangle = \alpha \langle X, Z \rangle + \beta \langle Y, Z \rangle$ ,
- (ii)  $\langle X, Y \rangle = \langle Y, X \rangle$ ,
- (iii)  $|\langle X, Y \rangle|^2 \leq \langle X \rangle \langle Y \rangle$ .
- (iv) For  $P$ -a.e.  $\omega \in \Omega$ ,

$$\begin{aligned} \xi_t(\omega) - \xi_s(\omega) &\leq \frac{1}{2} [\langle X \rangle_t(\omega) - \langle X \rangle_s(\omega) + \langle Y \rangle_t(\omega) - \langle Y \rangle_s(\omega)]; \\ 0 &\leq s < t < \infty, \end{aligned}$$

where  $\xi_t$  denotes the total variation of  $\xi \triangleq \langle X, Y \rangle$  on  $[0, t]$ .

The use of the term *quadratic variation* in Definition 5.3 may appear to be unfounded. Indeed, a more conventional use of this term is the following. Let  $X = \{X_t; 0 \leq t < \infty\}$  be a process, fix  $t > 0$ , and let  $\Pi = \{t_0, t_1, \dots, t_m\}$ , with  $0 = t_0 \leq t_1 \leq t_2 \leq \dots \leq t_m = t$ , be a partition of  $[0, t]$ . Define the  $p$ -th variation ( $p > 0$ ) of  $X$  over the partition  $\Pi$  to be

$$V_t^{(p)}(\Pi) = \sum_{k=1}^m |X_{t_k} - X_{t_{k-1}}|^p.$$

Now define the mesh of the partition  $\Pi$  as  $\|\Pi\| = \max_{1 \leq k \leq m} |t_k - t_{k-1}|$ . If  $V_t^{(2)}(\Pi)$  converges in some sense as  $\|\Pi\| \rightarrow 0$ , the limit is entitled to be called the quadratic variation of  $X$  on  $[0, t]$ . Our justification of Definition 5.3 for *continuous* martingales (on which we shall concentrate from now on) is the following result:

**5.8 Theorem.** *Let  $X$  be in  $\mathcal{M}_2^c$ . For partitions  $\Pi$  of  $[0, t]$ , we have  $\lim_{\|\Pi\| \rightarrow 0} V_t^{(2)}(\Pi) = \langle X \rangle_t$  (in probability); i.e., for every  $\varepsilon > 0$ ,  $\eta > 0$  there exists  $\delta > 0$  such that  $\|\Pi\| < \delta$  implies*

$$P[|V_t^{(2)}(\Pi) - \langle X \rangle_t| > \varepsilon] < \eta.$$

The proof of Theorem 5.8 proceeds through two lemmas. The key fact employed here is that, *when squaring sums of martingale increments and taking the expectation, one can neglect the cross-product terms*. More precisely, if  $X \in \mathcal{M}_2$  and  $0 \leq s < t \leq u < v$ , then

$$E[(X_v - X_u)(X_t - X_s)] = E\{E[X_v - X_u|\mathcal{F}_u](X_t - X_s)\} = 0.$$

We shall apply this fact to both martingales  $X \in \mathcal{M}_2$  and  $X^2 - \langle X \rangle$ . In the latter case, we note that because

$$\begin{aligned} E[(X_v - X_u)^2|\mathcal{F}_t] &= E[X_v^2 - 2X_u E[X_v|\mathcal{F}_u] + X_u^2|\mathcal{F}_t] \\ &= E[X_v^2 - X_u^2|\mathcal{F}_t] = E[\langle X \rangle_v - \langle X \rangle_u|\mathcal{F}_t], \end{aligned}$$

the terms  $X_v^2 - \langle X \rangle_v - (X_u^2 - \langle X \rangle_u)$  and  $(X_v - X_u)^2 - (\langle X \rangle_v - \langle X \rangle_u)$  have the same conditional expectation given  $\mathcal{F}_t$ , namely zero, and thus the expectation of products of such terms over nonoverlapping intervals is still zero.

Let us consider again a basic probability space  $(\Omega, \mathcal{F}, P)$  with an associated filtration  $\{\mathcal{F}_t\}$  which we always assume to satisfy the usual conditions.

**3.1 Definition.** *A continuous semimartingale  $X = \{X_t, \mathcal{F}_t; 0 \leq t < \infty\}$  is an adapted process which has the decomposition,  $P$  a.s.,*

$$(3.1) \quad X_t = X_0 + M_t + B_t; \quad 0 \leq t < \infty,$$

where  $M = \{M_t, \mathcal{F}_t; 0 \leq t < \infty\} \in \mathcal{M}^{c, \text{loc}}$  (Definition 1.5.15) and  $B = \{B_t, \mathcal{F}_t; 0 \leq t < \infty\}$  is the difference of continuous, nondecreasing, adapted processes  $\{A_t^\pm, \mathcal{F}_t; 0 \leq t < \infty\}$ :

$$(3.2) \quad B_t = A_t^+ - A_t^-; \quad 0 \leq t < \infty,$$

with  $A_0^\pm = 0$ ,  $P$  a.s. We shall always assume that (3.2) is the minimal decomposition of  $B$ ; in other words,  $A_t^+$  is the positive variation of  $B$  on  $[0, t]$  and  $A_t^-$  is the negative variation. The total variation of  $B$  on  $[0, t]$  is then  $\tilde{B}_t \triangleq A_t^+ + A_t^-$ .

The following problem discusses the question of uniqueness for the decomposition (3.1) of a continuous semimartingale.

**3.2 Problem.** Let  $X = \{X_t, \mathcal{F}_t; 0 \leq t < \infty\}$  be a continuous semimartingale with decomposition (3.1). Suppose that  $X$  has another decomposition

$$X_t = X_0 + \tilde{M}_t + \tilde{B}_t; \quad 0 \leq t < \infty,$$

where  $\tilde{M} \in \mathcal{M}^{c, \text{loc}}$  and  $\tilde{B}$  is a continuous, adapted process which has finite total variation on each bounded interval  $[0, t]$ . Prove that  $P$ -a.s.,

$$M_t = \tilde{M}_t, \quad B_t = \tilde{B}_t, \quad 0 \leq t < \infty.$$

## A. The It� Rule

It�'s formula states that a "smooth function" of a continuous semimartingale is a continuous semimartingale, and provides its decomposition.

**3.3 Theorem.** (It� (1944), Kunita & Watanabe (1967)). *Let  $f: \mathbb{R} \rightarrow \mathbb{R}$  be a function of class  $C^2$  and let  $X = \{X_t, \mathcal{F}_t; 0 \leq t < \infty\}$  be a continuous semimartingale with decomposition (3.1). Then,  $P$ -a.s.,*

$$(3.3) \quad \begin{aligned} f(X_t) = f(X_0) + \int_0^t f'(X_s) dM_s + \int_0^t f'(X_s) dB_s \\ + \frac{1}{2} \int_0^t f''(X_s) d\langle M \rangle_s, \quad 0 \leq t < \infty. \end{aligned}$$

**3.4 Remark.** For fixed  $\omega$  and  $t > 0$ , the function  $X_s(\omega)$  is bounded for  $0 \leq s \leq t$ , so  $f'(X_s(\omega))$  is bounded on this interval. It follows that  $\int_0^t f'(X_s) dM_s$  is defined

**3.27 Remark.** A straightforward localization argument shows that (3.27), (3.29) are valid for any  $M \in \mathcal{M}^{c, \text{loc}}$ . The same is true for (3.28), provided that the additional condition  $E(\langle M \rangle_T^m) < \infty$  holds.

We can state now the principal result of this subsection.

**3.28 Theorem** (The Burkholder-Davis-Gundy Inequalities). *Let  $M \in \mathcal{M}^{c, \text{loc}}$  and recall the convention (3.26). For every  $m > 0$  there exist universal positive constants  $k_m, K_m$  (depending only on  $m$ ), such that*

$$(3.37) \quad k_m E(\langle M \rangle_T^m) \leq E[(M_T^*)^{2m}] \leq K_m E(\langle M \rangle_T^m)$$

*holds for every stopping time  $T$ . In particular, if we have  $E\sqrt{\langle M \rangle_a} < \infty$  for every  $0 < a < \infty$ , then  $M$  is a martingale.*

**PROOF.** From Proposition 3.26 and Remark 3.27, we have the validity of (3.37) for  $m > 1/2$ . It remains to deal with the case  $0 < m \leq 1/2$ ; we assume without loss of generality that  $M, \langle M \rangle$  are bounded.

Let us recall now Problem 1.4.15 and its consequence (1.4.17). The right-hand side of (3.29) permits the choice  $X = (M^*)^2, A = C_1 \langle M \rangle$  in the former, and we obtain from the latter  $E[(M_T^*)^{2m}] \leq ((2 - m)/(1 - m)) C_1^m E(\langle M \rangle_T^m)$  for every  $0 < m < 1$ . Similarly, the left-hand side of (3.29) allows us to take  $X = B_1 \langle M \rangle, A = (M^*)^2$  in Problem 1.4.15, and then (1.4.17) gives for  $0 < m < 1$ :  $((1 - m)/(2 - m)) B_1^m E(\langle M \rangle_T^m) \leq E[(M_T^*)^{2m}]$ . The last claim follows from Problem 1.5.19(i), since then (3.37) implies  $E(\sup_{0 \leq t \leq a} |M_t|) < \infty, \forall 0 < a < \infty$ .  $\square$ 

**3.29 Problem.** Let  $M = (M^{(1)}, \dots, M^{(d)})$  be a vector of continuous, local martingales, i.e.,  $M^{(i)} \in \mathcal{M}^{c, \text{loc}}$ , and denote

$$\|M\|_t^* \triangleq \max_{0 \leq s \leq t} \|M_s\|, \quad A_t \triangleq \sum_{i=1}^d \langle M^{(i)} \rangle_t; \quad 0 \leq t < \infty.$$

Show that for any  $m > 0$ , there exist (universal) positive constants  $\lambda_m, \Lambda_m$  such that

$$(3.38) \quad \lambda_m E(A_T^m) \leq E(\|M\|_T^*)^{2m} \leq \Lambda_m E(A_T^m)$$

holds for every stopping time  $T$ .

**3.30 Remark.** In particular, if the  $M^{(i)}$  in Problem 3.29 are given by

$$M_t^{(i)} = \sum_{j=1}^r \int_0^t X_s^{(i,j)} dW_s^{(j)},$$

where  $\{W_t = (W_t^{(1)}, \dots, W_t^{(r)}), \mathcal{F}_t; 0 \leq t < \infty\}$  is standard,  $r$ -dimensional Brownian motion,  $\{X_t = (X_t^{(i,j)}); 1 \leq i \leq d, 1 \leq j \leq r, 0 \leq t < \infty\}$  is a matrix

$$(6.10) \quad (W_t - a)^+ - (z - a)^+ = \int_0^t 1_{(a, \infty)}(W_s) dW_s + \frac{1}{2} \int_0^t \delta(W_s - a) ds,$$

and in conjunction with (6.9), we have

$$(6.11) \quad L_t(a) = (W_t - a)^+ - (z - a)^+ - \int_0^t 1_{(a, \infty)}(W_s) dW_s; \quad 0 \leq t < \infty$$

 $P^z$ -a.s. for every  $z \in \mathbb{R}$ . Despite the heuristic nature of both (6.9) and (6.10), the representation (6.11) for local time is valid and will be established rigorously.

**6.8 Proposition.** *Let us assume that Brownian local time exists, and fix a number  $a \in \mathbb{R}$ . Then the process  $L(a) = \{L_t(a), \mathcal{F}_t; 0 \leq t < \infty\}$  is a nonnegative, continuous additive functional which satisfies (6.11) and the companion representations*

$$(6.12) \quad L_t(a) = (W_t - a)^- - (z - a)^- + \int_0^t 1_{(-\infty, a]}(W_s) dW_s; \quad 0 \leq t < \infty,$$

$$(6.13) \quad 2L_t(a) = |W_t - a| - |z - a| - \int_0^t \operatorname{sgn}(W_s - a) dW_s; \quad 0 \leq t < \infty$$

*a.s.  $P^z$ , for every  $z \in \mathbb{R}$ .*

**6.9 Remark.** Any of the formulas (6.11), (6.12), or (6.13) is referred to as the *Tanaka formula for Brownian local time*. We need establish only (6.11); then (6.12) follows by symmetry and (6.13) by addition, since

$$P^z \left[ \int_0^t 1_{\{a\}}(W_s) dW_s = 0; \quad \forall 0 \leq t < \infty \right] = 1; \quad \forall z \in \mathbb{R}.$$

In particular, it does not matter how we define  $\operatorname{sgn}(0)$  in (6.13); we shall define  $\operatorname{sgn}$  so as to make it left-continuous, i.e.,

$$(6.14) \quad \operatorname{sgn}(x) = \begin{cases} 1; & x > 0 \\ -1; & x \leq 0. \end{cases}$$

**6.10 Remark.** The process  $\{(W_t - a)^+, \mathcal{F}_t; 0 \leq t < \infty\}$  is a continuous, non-negative submartingale (Proposition 1.3.6); it admits, therefore, a unique Doob-Meyer decomposition (under  $P^z$ , for any  $z \in \mathbb{R}$ ):

$$(6.15) \quad (W_t - a)^+ = (z - a)^+ + M_t(a) + A_t(a); \quad 0 \leq t < \infty,$$

where  $A(a)$  is a continuous, increasing process and  $M(a)$  is a martingale (see Section 1.4). The Tanaka formula (6.11) identifies both parts of this decomposition, as  $A_t(a) = L_t(a)$  and

$$(6.16) \quad M_t(a) = \int_0^t 1_{(a, \infty)}(W_s) dW_s; \quad 0 \leq t < \infty.$$

where we have used not only the equality of  $P_y\{\omega \in \Omega; \omega(t_n - t_{n-1}) \in B\}$  and  $\tilde{P}_y\{\omega \in \Omega; \omega(t_n - t_{n-1}) \in B\}$ , but also their  $\mathcal{G}(t_1, \dots, t_{n-1})$ -measurability. It is now clear that  $P^x$  and  $\tilde{P}^x$  agree on  $\mathcal{G}(t_1, \dots, t_n)$ .  $\square$ 

We can now put the various results together.

**4.28 Theorem** (Stroock & Varadhan (1969)). *Suppose that the coefficients  $b(x)$  and  $\sigma(x)$  in Definition 4.15 are such that, for every  $f \in C_0^\infty(\mathbb{R}^d)$ , the Cauchy problem (4.31), (4.32) has a solution  $u_f \in C([0, \infty) \times \mathbb{R}^d) \cap C^{1,2}((0, \infty) \times \mathbb{R}^d)$  which is bounded on each strip of the form  $[0, T] \times \mathbb{R}^d$ . Then, for every  $x \in \mathbb{R}^d$ , there exists at most one solution to the time-homogeneous martingale problem.*

**4.29 Corollary.** *Let the coefficients  $b(x)$ ,  $\sigma(x)$  be bounded and continuous and satisfy the assumptions of Theorem 4.28. Then the time-homogeneous martingale problem is well posed.*

**4.30 Remark.** A sufficient condition for the solvability of the Cauchy problem (4.31), (4.32) in the way required by Theorem 4.28 is that the coefficients  $b_i(x)$ ,  $a_{ik}(x); 1 \leq j, k \leq d$  be bounded and H�lder-continuous on  $\mathbb{R}^d$ , and the matrix  $a(x)$  be *uniformly positive definite*; i.e.,

$$(4.34) \quad \sum_{i=1}^d \sum_{k=1}^d a_{ik}(x) \xi_i \xi_k \geq \lambda \|\xi\|^2; \quad \forall x, \xi \in \mathbb{R}^d \quad \text{and some } \lambda > 0.$$

We refer to Friedman (1964), Chapter 1, and Friedman (1975), �6.4, �6.5, or Stroock & Varadhan (1979), Theorem 3.2.1, for such results; see also Remark 7.8 later in this chapter.

**4.31 Remark.** If  $a_{ik} \in C^2(\mathbb{R}^d)$  for  $1 \leq i, k \leq d$ , then  $a(x)$  has a locally Lipschitz-continuous square root, i.e., a  $(d \times d)$ -matrix-valued function  $\tilde{\sigma}(x) = \{\tilde{\sigma}_{ij}(x)\}_{1 \leq i, j \leq d}$  such that  $a_{ik}(x) = \sum_{j=1}^d \tilde{\sigma}_{ij}(x) \tilde{\sigma}_{kj}(x); x \in \mathbb{R}^d$  (Friedman (1975), Theorem 6.1.2). We do not necessarily have  $\sigma(x) = \tilde{\sigma}(x)$  (indeed, one interesting case is the one-dimensional problem with  $\sigma(x) = \text{sgn}(x)$  and  $\tilde{\sigma}(x) = 1; x \in \mathbb{R}$ ). If, in addition,  $b_i \in C^1(\mathbb{R}^d); 1 \leq i \leq d$ , then according to Theorem 2.5, Remark 3.3, Proposition 3.20, Corollary 4.9, and Proposition 4.11, for every  $x \in \mathbb{R}^d$  there exists *at most* one solution to the time-homogeneous martingale problem. This result imposes no condition analogous to (4.34) and is thus especially helpful in the study of degenerate diffusions.

**4.32 Refinements.** It can be shown that if the coefficients  $b(x)$ ,  $\sigma(x)$  are bounded and Borel-measurable, and the matrix  $a(x)$  is uniformly positive definite on compact subsets of  $\mathbb{R}^d$ , then the time-homogeneous martingale problem admits a solution. In the cases  $d = 1$  and  $d = 2$ , this solution is unique. See Stroock & Varadhan (1979), Exercises 7.3.2–7.3.4, and Krylov (1969), (1974).