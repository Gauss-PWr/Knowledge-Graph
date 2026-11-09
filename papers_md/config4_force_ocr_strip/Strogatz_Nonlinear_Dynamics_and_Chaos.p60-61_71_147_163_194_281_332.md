We begin with the most fundamental bifurcation of all.

## 3.1 Saddle-Node Bifurcation

The saddle-node bifurcation is the basic mechanism by which fixed points are *created and destroyed*. As a parameter is varied, two fixed points move toward each other, collide, and mutually annihilate.

The prototypical example of a saddle-node bifurcation is given by the first-order system

$$\dot{x} = r + x^2 \quad (1)$$

where  $r$  is a parameter, which may be positive, negative, or zero. When  $r$  is negative, there are two fixed points, one stable and one unstable (Figure 3.1.1a).

**Figure 3.1.1**

As  $r$  approaches 0 from below, the parabola moves up and the two fixed points move toward each other. When  $r = 0$ , the fixed points coalesce into a half-stable fixed point at  $x^* = 0$  (Figure 3.1.1b). This type of fixed point is extremely delicate—it vanishes as soon as  $r > 0$ , and now there are no fixed points at all (Figure 3.1.1c).

In this example, we say that a *bifurcation* occurred at  $r = 0$ , since the vector fields for  $r < 0$  and  $r > 0$  are qualitatively different.

### Graphical Conventions

There are several other ways to depict a saddle-node bifurcation. We can show a stack of vector fields for discrete values of  $r$  (Figure 3.1.2).

**Figure 3.1.2**

This representation emphasizes the dependence of the fixed points on  $r$ . In the limit of a *continuous* stack of vector fields, we have a picture like Figure 3.1.3. The curve shown is  $r = -x^2$ , i.e.,  $\dot{x} = 0$ , which gives the fixed points for different  $r$ . To distinguish between stable and unstable fixed points, we use a solid line for stable points and a broken line for unstable ones.

However, the most common way to depict the bifurcation is to invert the axes of Figure 3.1.3. The rationale is that  $r$  plays the role of an independent variable,

**Figure 3.1.3**

and so should be plotted horizontally (Figure 3.1.4). The drawback is that now the  $x$ -axis has to be plotted vertically, which looks strange at first. Arrows are sometimes included in the picture, but not always. This picture is called the *bifurcation diagram* for the saddle-node bifurcation.

**Figure 3.1.4**

### Terminology

Bifurcation theory is rife with conflicting terminology. The subject really hasn't settled down yet, and different people use different words for the same thing. For example, the saddle-node bifurcation is sometimes called a *fold bifurcation* (because the curve in Figure 3.1.4

Figure 3.4.1 shows the vector field for different values of  $r$ .

**Figure 3.4.1**

When  $r < 0$ , the origin is the only fixed point, and it is stable. When  $r = 0$ , the origin is still stable, but much more weakly so, since the linearization vanishes. Now solutions no longer decay exponentially fast—instead the decay is a much slower algebraic function of time (recall Exercise 2.4.9). This lethargic decay is called *critical slowing down* in the physics literature. Finally, when  $r > 0$ , the origin has become unstable. Two new stable fixed points appear on either side of the origin, symmetrically located at  $x^* = \pm\sqrt{r}$ .

The reason for the term “pitchfork” becomes clear when we plot the bifurcation diagram (Figure 3.4.2). Actually, pitchfork trifurcation might be a better word!

**Figure 3.4.2**

**EXAMPLE 5.2.1:**

Solve the initial value problem  $\dot{x} = x + y$ ,  $\dot{y} = 4x - 2y$ , subject to the initial condition  $(x_0, y_0) = (2, -3)$ .

*Solution:* The corresponding matrix equation is

$$\begin{pmatrix} \dot{x} \\ \dot{y} \end{pmatrix} = \begin{pmatrix} 1 & 1 \\ 4 & -2 \end{pmatrix} \begin{pmatrix} x \\ y \end{pmatrix}.$$

First we find the eigenvalues of the matrix  $A$ . The matrix has  $\tau = -1$  and  $\Delta = -6$ , so the characteristic equation is  $\lambda^2 + \lambda - 6 = 0$ . Hence

$$\lambda_1 = 2, \lambda_2 = -3.$$

Next we find the eigenvectors. Given an eigenvalue  $\lambda$ , the corresponding eigenvector  $\mathbf{v} = (v_1, v_2)$  satisfies

$$\begin{pmatrix} 1-\lambda & 1 \\ 4 & -2-\lambda \end{pmatrix} \begin{pmatrix} v_1 \\ v_2 \end{pmatrix} = \begin{pmatrix} 0 \\ 0 \end{pmatrix}.$$

For  $\lambda_1 = 2$ , this yield  $\begin{pmatrix} -1 & 1 \\ 4 & -4 \end{pmatrix} \begin{pmatrix} v_1 \\ v_2 \end{pmatrix} = \begin{pmatrix} 0 \\ 0 \end{pmatrix}$ , which has a nontrivial solution  $(v_1, v_2) = (1, 1)$ , or any scalar multiple thereof. (Of course, any multiple of an eigenvector is always an eigenvector; we try to pick the simplest multiple, but any one will do.) Similarly, for  $\lambda_2 = -3$ , the eigenvector equation becomes  $\begin{pmatrix} 4 & 1 \\ 4 & 1 \end{pmatrix} \begin{pmatrix} v_1 \\ v_2 \end{pmatrix} = \begin{pmatrix} 0 \\ 0 \end{pmatrix}$ , which has a nontrivial solution  $(v_1, v_2) = (1, -4)$ . In summary,

$$\mathbf{v}_1 = \begin{pmatrix} 1 \\ 1 \end{pmatrix}, \quad \mathbf{v}_2 = \begin{pmatrix} 1 \\ -4 \end{pmatrix}.$$

Next we write the general solution as a linear combination of eigensolutions. From (6), the general solution is

$$\mathbf{x}(t) = c_1 \begin{pmatrix} 1 \\ 1 \end{pmatrix} e^{2t} + c_2 \begin{pmatrix} 1 \\ -4 \end{pmatrix} e^{-3t}. \tag{7}$$

Finally, we compute  $c_1$  and  $c_2$  to satisfy the initial condition  $(x_0, y_0) = (2, -3)$ . At  $t = 0$ , (7) becomes

**Figure 6.1.3**

The nullclines also partition the plane into regions where  $\dot{x}$  and  $\dot{y}$  have various signs. Some of the typical vectors are sketched above in Figure 6.1.3. Even with the limited information obtained so far, Figure 6.1.3 gives a good sense of the overall flow pattern.

Now we use the computer to finish the problem. The direction field is indicated by the line segments in Figure 6.1.4, and several trajectories are shown. Note how the trajectories always follow the local slope.

**Figure 6.1.4**

The fixed point is now seen to be a nonlinear version of a saddle point. ■

## 6.2 Existence, Uniqueness, and Topological Consequences

We have been a bit optimistic so far—at this stage, we have no guarantee that the general nonlinear system  $\dot{\mathbf{x}} = \mathbf{f}(\mathbf{x})$  even *has* solutions! Fortunately the existence and uniqueness theorem given in Section 2.5 can be generalized to two-dimensional

**Theorem 6.8.2:** Any closed orbit in the phase plane must enclose fixed points whose indices sum to +1.

**Proof:** Let  $C$  denote the closed orbit. From property (4) above,  $I_C = +1$ . Then Theorem 6.8.1 implies  $\sum_{k=1}^n I_k = +1$ . ■

Theorem 6.8.2 has many practical consequences. For instance, it implies that there is always at least one fixed point inside any closed orbit in the phase plane (as you may have noticed on your own). If there is *only* one fixed point inside, it cannot be a saddle point. Furthermore, Theorem 6.8.2 can sometimes be used to rule out the possible occurrence of closed trajectories, as seen in the following examples.

**EXAMPLE 6.8.5:**

Show that closed orbits are impossible for the “rabbit vs. sheep” system

$$\dot{x} = x(3 - x - 2y)$$

$$\dot{y} = y(2 - x - y)$$

studied in Section 6.4. Here  $x, y \geq 0$ .

*Solution:* As shown previously, the system has four fixed points:  $(0,0) =$  unstable node;  $(0,2)$  and  $(3,0) =$  stable nodes; and  $(1,1) =$  saddle point. The index at each of these points is shown in Figure 6.8.9.

Now suppose that the system had a closed trajectory. Where could it lie? There are three qualitatively different locations, indicated by the dotted curves  $C_1$ ,  $C_2$ ,

**Figure 6.8.9**

 $C_3$ . They can be ruled out as follows: orbits like  $C_1$  are impossible because they don’t enclose any fixed points, and orbits like  $C_2$  violate the requirement that the indices inside must sum to +1. But what is wrong with orbits like  $C_3$ , which satisfy the index requirement? The trouble is that such orbits always cross the  $x$ -axis or the  $y$ -axis, and these axes contain straight-line trajectories. Hence  $C_3$  violates the rule that trajectories can’t cross (recall Section 6.2). ■

### Scaling Laws

For each of the bifurcations given here, there are characteristic *scaling laws* that govern the amplitude and period of the limit cycle as the bifurcation is approached. Let  $\mu$  denote some dimensionless measure of the distance from the bifurcation, and assume that  $\mu \ll 1$ . The generic scaling laws for bifurcations of cycles in two-dimensional systems are given in Table 7.4.1.

|                                   | Amplitude of<br>stable limit cycle | Period of cycle |
|-----------------------------------|------------------------------------|-----------------|
| Supercritical Hopf                | $O(\mu^{1/2})$                     | $O(1)$          |
| Saddle-node bifurcation of cycles | $O(1)$                             | $O(1)$          |
| Infinite-period                   | $O(1)$                             | $O(\mu^{-1/2})$ |
| Homoclinic                        | $O(1)$                             | $O(\ln \mu)$    |

**Table 8.4.1**

All of these laws have been explained previously, except those for the homoclinic bifurcation. The scaling of the period in that case is obtained by estimating the time required for a trajectory to pass by a saddle point (see Exercise 8.4.12 and Gaspard 1990).

Exceptions to these rules can occur, but only if there is some symmetry or other special feature that renders the problem nongeneric, as in the following example.

### EXAMPLE 8.4.1:

The van der Pol oscillator  $\ddot{x} + \varepsilon \dot{x}(x^2 - 1) + x = 0$  does not seem to fit anywhere in Table 7.4.1. At  $\varepsilon = 0$ , the eigenvalues at the origin are pure imaginary ( $\lambda = \pm i$ ), suggesting that a Hopf bifurcation occurs at  $\varepsilon = 0$ . But we know from Section 7.6 that for  $0 < \varepsilon \ll 1$ , the system has a limit cycle of amplitude  $r \approx 2$ . Thus the cycle is born “full grown,” not with size  $O(\varepsilon^{1/2})$  as predicted by the scaling law. What’s the explanation?

*Solution:* The bifurcation at  $\varepsilon = 0$  is degenerate. The nonlinear term  $\varepsilon \ddot{x}x^2$  vanishes at precisely the same parameter value as the eigenvalues cross the imaginary axis. That’s a nongeneric coincidence if there ever was one!

We can rescale  $x$  to remove this degeneracy. Write the equation as  $\ddot{x} + x + \varepsilon x^2 \dot{x} - \varepsilon \dot{x} = 0$ . Let  $u^2 = \varepsilon x^2$  to remove the  $\varepsilon$ -dependence of the nonlinear term. Then  $u = \varepsilon^{1/2}x$  and the equation becomes

$$\ddot{u} + u + u^2 \dot{u} - \varepsilon \dot{u} = 0.$$

head and therefore faster leakage. Although this is plausible physically, the fluid mechanics of leakage is complicated, and other rules are conceivable as well. The real justification for the rule above is that it agrees with direct measurements on the waterwheel itself, to a good approximation. (For experts on fluids: to achieve this linear relation between outflow and pressure head, Malkus attached thin tubes to the holes at the bottom of each chamber. Then the outflow is essentially Poiseuille flow in a pipe.)

1. 3. As the wheel rotates, it carries a new block of water into our observation sector. That block has mass  $m(\theta_1) \omega \Delta t$ , because it has angular width  $\omega \Delta t$  (Figure 9.1.5), and  $m(\theta_1)$  is its mass per unit angle.
2. 4. Similarly, the mass carried out of the sector is  $-m(\theta_2) \omega \Delta t$ .

Hence,

$$\Delta M = \Delta t \left[ \int_{\theta_1}^{\theta_2} Q d\theta - \int_{\theta_1}^{\theta_2} Km d\theta \right] + m(\theta_1) \omega \Delta t - m(\theta_2) \omega \Delta t. \quad (1)$$

To convert (1) to a differential equation, we put the transport terms inside the integral, using  $m(\theta_1) - m(\theta_2) = - \int_{\theta_1}^{\theta_2} \frac{\partial m}{\partial \theta} d\theta$ . Then we divide by  $\Delta t$  and let  $\Delta t \rightarrow 0$ . The result is

$$\frac{dM}{dt} = \int_{\theta_1}^{\theta_2} (Q - Km - \omega \frac{\partial m}{\partial \theta}) d\theta.$$

But by definition of  $M$ ,

$$\frac{dM}{dt} = \int_{\theta_1}^{\theta_2} \frac{\partial m}{\partial t} d\theta.$$

Hence

$$\int_{\theta_1}^{\theta_2} \frac{\partial m}{dt} d\theta = \int_{\theta_1}^{\theta_2} (Q - Km - \omega \frac{\partial m}{\partial \theta}) d\theta.$$

Since this holds for *all*  $\theta_1$  and  $\theta_2$ , we must have

$$\frac{\partial m}{\partial t} = Q - Km - \omega \frac{\partial m}{\partial \theta}. \quad (2)$$

Equation (2) is often called the *continuity equation*. Notice that it is *a partial* differential equation, unlike all the others considered so far in this book. We'll worry about how to analyze it later; we still need an equation that tells us how  $\omega(t)$  evolves.