- (i) <aX + PY,Z) <sup>=</sup> a<X,Z) + P<Y,Z),
- (ii) <X, Y) = <Y, X),
- (iii) I<X, Y) 1 <sup>2</sup> <X)<Y).
- (iv) For P-a.e. WEn,

$$\begin{aligned} \check{\xi}_t(\omega) - \check{\xi}_s(\omega) &\leq \frac{1}{2}[\langle X \rangle_t(\omega) - \langle X \rangle_s(\omega) + \langle Y \rangle_t(\omega) - \langle Y \rangle_s(\omega)], \\ 0 &\leq s < t < \infty, \end{aligned}$$

where ~, denotes the total variation of <X, Y) on [0, t].

The use of the term *quadratic variation* in Definition 5.3 may appear to be unfounded. Indeed, a more conventional use of this term is the following. Let *X* = *{X,;* 0:::;; t < oo} be a process, fix t > 0, and let 0 = *{to,t1, ... ,tm },* with o= to :::;; <sup>t</sup> <sup>1</sup> :::;; <sup>t</sup> <sup>2</sup> :::;; ••• :::;; *tm* = t, be <sup>a</sup> partition of[0, t]. Define the *p-th variation (p* > 0) *of X over the partition* 0 to be

$$V_t^{(p)}(\Pi) = \sum_{k=1}^m |X_{t_k} - X_{t_{k-1}}|^p.$$

Now define the mesh of the partition 0 as 11011 = max 1*SkSm* It*<sup>k</sup>* - tk-11. If Jt;(2)(0) converges in some sense as 11011 0, the limit is entitled to be called the quadratic variation of X on [0, t]. Our justification of Definition 5.3 for *continuous* martingales (on which we shall concentrate from now on) is the following result:

5.8 Theorem. *Let X be* in At~. *For partitions* 0 *of* [0, *t], we have* limllllll\_o Jt;(2)(ll) = <X), (in *probability); i.e., for every e* > 0, '1 > 0 *there exists* J > 0 *such that* II 0 II < J *implies*

$$P[|V_t^{(2)}(\Pi) - \langle X \rangle_t| > \varepsilon] < \eta.$$

The proof of Theorem 5.8 proceeds through two lemmas. The key fact employed here is that, *when squaring sums of martingale increments and taking the expectation, one can neglect the cross-product terms.* More precisely, if X E At2 and 0 :::;; s < t :::;; *u* < *v,* then

$$E[(X_v - X_u)(X_t - X_s)] = E\{E[X_v - X_u|{\mathcal{F}}_u](X_t - X_s)\} = 0.$$

We shall apply this fact to both martingales X EAt2 and X *<sup>2</sup>* - <X). In the latter case, we note that because

$$\begin{aligned} E[(X_v - X_u)^2 | \mathcal{F}_t] &= E[X_v^2 - 2X_u E[X_v | \mathcal{F}_u] + X_u^2 | \mathcal{F}_t] \\ &= E[X_v^2 - X_u^2 | \mathcal{F}_t] = E[\langle X \rangle_v - \langle X \rangle_u | \mathcal{F}_t], \end{aligned}$$

the terms X'; - <X)v - (X'; - <X)u> and (Xv - XY - «X)v - <X)u> have the same conditional expectation given~, namely zero, and thus the expectation of products of such terms over nonoverlapping intervals is still zero.

Let us consider again a basic probability space (n,:F, P) with an associated filtration {g;} which we always assume to satisfy the usual conditions.

3.1 Definition. *A continuous semimartingale X* = *{XI>* g;; 0 ::s; *t* < oo} is an adapted process which has the decomposition, P a.s.,

$$(3.1) \quad X_t = X_0 + M_t + B_t; \quad 0 \leq t < \infty,$$

where M = *{MI,*g;; 0 ::s; *<sup>t</sup>* < oo} <sup>E</sup> .;(("Ioc (Definition 1.5.15) and *<sup>B</sup>* = *{BI>* g;; o::s; *<sup>t</sup>* < oo} is the difference of continuous, nondecreasing, adapted processes {AI±,g;; O::s; *t* < oo}:

$$(3.2) \quad B_t = A_t^+ - A_t^-; \quad 0 \leq t < \infty,$$

$$(3.3) \quad f(X_t) = f(X_0) + \int_0^t f'(X_s) dM_s + \int_0^t f'(X_s) dB_s + \frac{1}{2} \int_0^t f''(X_s) d\langle M \rangle_s, \quad 0 \leq t < \infty.$$

with At = 0, P a.s. We shall always assume that (3.2) is the minimal decomposition of B; in other words, *A7* is the positive variation of Bon [0, *t]* and A; is the negative variation. The total variation of B on [0, *t]* is then BI £ *A7* + Ar -·

The following problem discusses the question of uniqueness for the decomposition (3.1) of a continuous semimartingale.

3.2 Problem. Let *X* = *{X"* g;; 0 ::s; *t* < oo} be a continuous semimartingale with decomposition (3.1). Suppose that X has another decomposition

$$X_t = X_0 + \tilde{M}_t + \tilde{B}_t; \quad 0 \leq t < \infty,$$

where ME.;(("Ioc and *ii* is a continuous, adapted process which has finite total variation on each bounded interval [0, *t].* Prove that P-a.s.,

$$M_t = \tilde{M}_t, \quad B_t = \tilde{B}_t, \quad 0 \leq t < \infty.$$

## A. The Ito Rule

Ito's formula states that a "smooth function" of a continuous semimartingale is a continuous semimartingale, and provides its decomposition.

3.3 Theorem. (Ito (1944), Kunita & Watanabe (1967)). *Let f:* -+ *be a function of class* C2 *and let X* = *{XI>* g;; 0 ::s; *t* < oo} *be a continuous semimartingale with decomposition* (3.1). *Then, P-a.s.,*

3.4 Remark. For fixed wand *t* > 0, the function *Xs(w)* is bounded for 0 ::s; s ::s; *t,* so *f'(Xs(w))* is bounded on this interval. It follows that J~f'(Xs)*dMs*is defined 3.27 **Remark.** A straightforward localization argument shows that (3.27), (3.29) are valid for any ME Jlc,loc. The same is true for (3.28), provided that the additional condition *E(<M)j!)* < <sup>00</sup> holds.

We can state now the principal result of this subsection.

3.28 **Theorem** (The Burkholder-Davis-Gundy Inequalities). *Let* ME Jlc,loc *and recall the convention* (3.26). *For every m* > 0 *there exist universal positive constants km , K <sup>m</sup> (depending only on m), such that*

$$(3.37) \quad k_m E(\langle M \rangle_T^m) \leq E[(M_T^*)^{2m}] \leq K_m E(\langle M \rangle_T^m)$$

*holds for every stopping time T In particular,* if *we have EJ<M)a* < <sup>00</sup> *for every* 0 < *a* < 00, *then* M *is a martingale.*

PROOF. From Proposition 3.26 and Remark 3.27, we have the validity of(3.37) for *m* > 1/2. It remains to deal with the case 0 < *m* ::; 1/2; we assume without loss of generality that M, *<M)* are bounded.

Let us recall now Problem 1.4.15 and its consequence (1.4.17). The righthand side of (3.29) permits the choice *X* = *(M\*)2, A* = C<sup>l</sup> *<M)* in the former, and we obtain from the latter *E[(Mj-)2m]* ::; ((2 - m)/(I - *m))CfE«M)'T)* for every 0 < *m* < 1. Similarly, the left-hand side of (3.29) allows us to take *X* = *B*1*<M), A* = *(M\*)2* in Problem 1.4.15, and then (1.4.17) gives for *0< m* < 1: ((1- *m)/(2* - *m))BfE«M)'T))::; E[(Mj-)2m].* The last claim follows from Problem 1.5.19(i), since then (3.37) implies E(SUPOS:Is:a IMII) < 00, *VO<a<oo.* D

3.29 **Problem.** Let M = (M(l), .. " *M(d»)* be a vector of continuous, local martingales, i.e., *M(i)* <sup>E</sup> Jlc.loc, and denote

$$\|M\|_t^* \triangleq \max_{0 \leq s \leq t} \|M_s\|, \quad A_t \triangleq \sum_{i=1}^d \langle M^{(i)} \rangle_t; \quad 0 \leq t < \infty.$$

Show that for any *m* > 0, there exist (universal) positive constants A.*<sup>m</sup> ,* Am such that

$$(3.38) \quad \lambda_m E(A_T^m) \leq E(\|M \|_T^*)^{2m} \leq \Lambda_m E(A_T^m) \quad \text{where } \Lambda_m = \lambda_m^2. \quad (3.39)$$

holds for every stopping time T

3.30 **Remark.** In particular, if the *M(i)* in Problem 3.29 are given by

lar, if the 
$$M^{(i)}$$
 in Problem 1
$$M_t^{(i)} = \sum_{j=1}^r \int_0^t X_s^{(i,j)} dW_s^{(j)},$$

where {Jt; = (Jt;(l), ... , Jt;(r»),~; 0 ::; *t* < oo} is standard, r-dimensional Brownian motion, {XI = (Xfi,j»); 1 ::; i ::; *d,* 1 ::; j ::; *r,O* ::; *t* < oo} is a matrix

(6.10) 
$$(W_t - a)^+ - (z - a)^+ = \int_0^t 1_{(a, \infty)}(W_s) dW_s + \frac{1}{2} \int_0^t \delta(W_s - a) ds$$
,

and in conjunction with (6.9), we have

and in conjunction with (6.9), we have
$$(6.11) \quad L_t(a) = (W_t - a)^+ - (z - a)^+ - \int_0^t 1_{(a, \infty)}(W_s) dW_s; \quad 0 \leq t < \infty$$

*PZ-a.s.* for every zEIR. Despite the heuristic nature of both (6.9) and (6.10), the representation (6.11) for local time is valid and will be established rigorously.

**6.8 Proposition.** *Let us assume that Brownian local time exists, and fix a number a* EIR. *Then the process L(a)* = *{LI(a),* ~; 0 :s; *t* < oo} *is a nonnegative, continuous additive functional which satisfies* (6.11) *and the companion representations*

ous additive functional which satisfies (6.11) and the companion represent
$$(6.12) \quad L_t(a) = (W_t - a)^- - (z - a)^- + \int_0^t 1_{(-\infty, a]}(W_s) dW_s; \quad 0 \leq t < \infty,$$

$$(6.12) \quad \underline{L}_t(s) = (n_t - a) - (t - a) + \int_0^t 1_{\{s \in [a, n_t - s) \}} w_s s, \quad t \geq t - 1 = \infty$$
$$(6.13) \quad 2L_t(a) = |W_t - a| - |z - a| - \int_0^t \text{sgn}(W_s - a) dW_s; \quad 0 \leq t < \infty$$

*a.s. pz, for every* <sup>z</sup> <sup>E</sup> IR.

**6.9 Remark.** Any of the formulas (6.11), (6.12), or (6.13) is referred to as the *Tanaka formula for Brownian local time.* We need establish only (6.11); then (6.12) follows by symmetry and (6.13) by addition, since

$$P^z \left[ \int_0^t 1_{\{a\}}(W_s) dW_s = 0; \quad \forall 0 \leq t < \infty \right] = 1; \quad \forall z \in \mathbb{R}.$$

**In** particular, it does not matter how we define sgn(O) in (6.13); we shall define sgn so as to make it left-continuous, i.e.,

$$(6.14) \quad \operatorname{sgn}(x) = \begin{cases} 1; & x > 0 \\ -1; & x \leq 0. \end{cases}$$

**6.10 Remark.** The process {(l¥, - *at,* ~; 0 :s; *t* < oo} is a continuous, nonnegative submartingale (Proposition 1.3.6); it admits, therefore, a unique Doob-Meyer decomposition (under *pz,* for any ZE IR):

$$(6.15) \quad (W_t - a)^+ = (z - a)^+ + M_t(a) + A_t(a); \quad 0 \leq t < \infty,$$

where *A(a)* is a continuous, increasing process and *M(a)* is a martingale (see Section 1.4). The Tanaka formula (6.11) identifies both parts of this decomposition, as *AI(a)* = *LI(a)* and

*(6.16) MI(a)* <sup>=</sup> I l(a.oo)(~)d~; O:s; *<sup>t</sup>* <sup>&</sup>lt; 00.

where we have used not only the equality of *Py{WEQ; wet.* - *t.\_1)EB}* and *Py{WEQ; wet.* - *t.\_1)EB},* but also their ~(tl, ... ,t.\_l)-measurability. It is now clear that *p <sup>x</sup>* and p*<sup>x</sup>* agree on ~(t 1"'" *t.).* 0

We can now put the various results together.

**4.28 Theorem** (Stroock & Varadhan (1969». *Suppose that the coefficients b(x) and <rex) in Definition* 4.15 *are such that, for every f* E CO'(jRd), *the Cauchy problem* (4.31), (4.32) *has a solution UfE C([O,* 00) <sup>X</sup> jRd) *n* C1,2«O, 00) x jRd) *which is bounded on each strip of the form* [0, *T]* x jRd. *Then, for every x* E jRd, *there exists at most one solution to the time-homogeneous martingale problem.*

**4.29 Corollary.** *Let the coefficients b(x), a(x) be bounded and continuous and satisfy the assumptions of Theorem* 4.28. *Then the time-homogeneous martingale problem is well posed.*

**4.30 Remark.** A sufficient condition for the solvability ofthe Cauchy problem (4.31), (4.32) in the way required by Theorem 4.28 is that the coefficients b;(x), *aik(x);* 1 :5: j, *k* :5: *d* be bounded and Holder-continuous on jRd, and the matrix *a(x)* be *uniformly positive definite;* i.e.,

$$(4.34) \quad \sum_{i=1}^d \sum_{k=1}^d a_{ik}(x) \xi_i \xi_k \geq \lambda \|\xi\|^2; \quad \forall x, \xi \in \mathbb{R}^d \quad \text{and some } \lambda > 0.$$

We refer to Friedman (1964), Chapter 1, and Friedman (1975), §6.4, §6.5, or Stroock & Varadhan (1979), Theorem 3.2.1, for such results; see also Remark 7.8 later in this chapter.

**4.31 Remark. If** *aik* E C <sup>2</sup> (jRd) for 1 :5: *i,* k :5: *d,* then *a(x)* has a locally Lipschitzcontinuous square root, i.e., a *(d* x d)-matrix-valued function *O'(x) = {O'ij(x)L* ~i,j:"d such that *aik(x)* = L1~1 *O'ij(x)O'kix);* XE jRd (Friedman (1975), Theorem 6.1.2). We do not necessarily have *a(x)* = *O'(x)* (indeed, one interesting case is the one-dimensional problem with *a(x)* = sgn(x) and *O'(x)* = 1; *x* <sup>E</sup> /R). If, in addition, b*<sup>i</sup>* E C 1(jRd); 1 :5: i :5: d, then according to Theorem 2.5, Remark 3.3, Proposition 3.20, Corollary 4.9, and Proposition 4.11, for every x E jRd there exists *at most* one solution to the time-homogeneous martingale problem. This result imposes no condition analogous to (4.34) and is thus especially helpful in the study of degenerate diffusions.

**4.32 Refinements. It** can be shown that ifthe coefficients *b(x), a(x)* are bounded and Borel-measurable, and the matrix *a(x)* is uniformly positive definite on compact subsets of /R<sup>d</sup> , then the time-homogeneous martingale problem admits a solution. **In** the cases d = 1 and d = 2, this solution is unique. See Stroock & Varadhan (1979), Exercises 7.3.2-7.3.4, and Krylov (1969), (1974).