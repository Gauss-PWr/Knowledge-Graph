the calculation of fractional differentiation in continuous stochastic processes (e.g., Jensen and Nielsen [2014]).

Differentiating the stochastic process is a computationally expensive operation. In this chapter we will take a practical, alternative, and novel approach to recover stationarity: We will generalize the difference operator to non-integer steps.

### 5.4 THE METHOD

Consider the backshift operator,  $B$ , applied to a matrix of real-valued features  $\{X_t\}$ , where  $B^k X_t = X_{t-k}$  for any integer  $k \geq 0$ . For example,  $(1 - B)^2 = 1 - 2B + B^2$ , where  $B^2 X_t = X_{t-2}$ , so that  $(1 - B)^2 X_t = X_t - 2X_{t-1} + X_{t-2}$ . Note that  $(x + y)^n = \sum_{k=0}^n \binom{n}{k} x^k y^{n-k} = \sum_{k=0}^n \binom{n}{k} x^{n-k} y^k$ , for  $n$  a positive integer. For a real number  $d$ ,  $(1 + x)^d = \sum_{k=0}^{\infty} \binom{d}{k} x^k$ , the binomial series.

In a fractional model, the exponent  $d$  is allowed to be a real number, with the following formal binomial series expansion:

$$\begin{aligned} (1 - B)^d &= \sum_{k=0}^{\infty} \binom{d}{k} (-B)^k = \sum_{k=0}^{\infty} \frac{\prod_{i=0}^{k-1} (d - i)}{k!} (-B)^k \\ &= \sum_{k=0}^{\infty} (-B)^k \prod_{i=0}^{k-1} \frac{d - i}{k - i} \\ &= 1 - dB + \frac{d(d - 1)}{2!} B^2 - \frac{d(d - 1)(d - 2)}{3!} B^3 + \dots \end{aligned}$$

#### 5.4.1 Long Memory

Let us see how a real (non-integer) positive  $d$  preserves memory. This arithmetic series consists of a dot product

$$\tilde{X}_t = \sum_{k=0}^{\infty} \omega_k X_{t-k}$$

with weights  $\omega$ 

$$\omega = \left\{ 1, -d, \frac{d(d - 1)}{2!}, -\frac{d(d - 1)(d - 2)}{3!}, \dots, (-1)^k \prod_{i=0}^{k-1} \frac{d - i}{k!}, \dots \right\}$$

and values  $X$ 

$$X = \{X_t, X_{t-1}, X_{t-2}, X_{t-3}, \dots, X_{t-k}, \dots\}$$

**FIGURE 5.1**  $\omega_k$  (y-axis) as  $k$  increases (x-axis). Each line is associated with a particular value of  $d \in [0, 1]$ , in 0.1 increments.

When  $d$  is a positive integer number,  $\prod_{i=0}^{k-1} \frac{d-i}{k!} = 0, \forall k > d$ , and memory beyond that point is cancelled. For example,  $d = 1$  is used to compute returns, where  $\prod_{i=0}^{k-1} \frac{d-i}{k!} = 0, \forall k > 1$ , and  $\omega = \{1, -1, 0, 0, \dots\}$ .

## 5.4.2 Iterative Estimation

Looking at the sequence of weights,  $\omega$ , we can appreciate that for  $k = 0, \dots, \infty$ , with  $\omega_0 = 1$ , the weights can be generated iteratively as:

$$\omega_k = -\omega_{k-1} \frac{d-k+1}{k}$$

Figure 5.1 plots the sequence of weights used to compute each value of the fractionally differentiated series. The legend reports the value of  $d$  used to generate each sequence, the x-axis indicates the value of  $k$ , and the y-axis shows the value of  $\omega_k$ . For example, for  $d = 0$ , all weights are 0 except for  $\omega_0 = 1$ . That is the case where the differentiated series coincides with the original one. For  $d = 1$ , all weights are 0 except for  $\omega_0 = 1$  and  $\omega_1 = -1$ . That is the standard first-order integer differentiation, which is used to derive log-price returns. Anywhere in between these two cases, all weights after  $\omega_0 = 1$  are negative and greater than  $-1$ .

Figure 5.2 plots the sequence of weights where  $d \in [1, 2]$ , at increments of 0.1. For  $d > 1$ , we observe  $\omega_1 < -1$  and  $\omega_k > 0, \forall k \geq 2$ .

Snippet 5.1 lists the code used to generate these plots.

Let us consider the convergence of the weights. From the above result, we can see that for  $k > d$ , if  $\omega_{k-1} \neq 0$ , then  $\left| \frac{\omega_k}{\omega_{k-1}} \right| = \left| \frac{d-k+1}{k} \right| < 1$ , and  $\omega_k = 0$  otherwise. Consequently, the weights converge asymptotically to zero, as an infinite product of factors within the unit circle. Also, for a positive  $d$  and  $k < d + 1$ , we have  $\frac{d-k+1}{k} \geq 0$ , which makes the initial weights alternate in sign. For a non-integer  $d$ , once  $k \geq d + 1$ ,  $\omega_k$  will be negative if  $\text{int}[d]$  is even, and positive otherwise. Summarizing,  $\lim_{k \rightarrow \infty} \omega_k = 0^-$  (converges to zero from the left) when  $\text{int}[d]$  is even, and  $\lim_{k \rightarrow \infty} \omega_k = 0^+$  (converges to zero from the right) when  $\text{Int}[d]$  is odd. In the special case  $d \in (0, 1)$ , this means that  $-1 < \omega_k < 0, \forall k > 0$ . This alternation of weight signs is necessary to make  $\{\tilde{X}_t\}_{t=1,\dots,T}$  stationary, as memory wanes or is offset over the long run.

## 5.5 IMPLEMENTATION

In this section we will explore two alternative implementations of fractional differentiation: the standard “expanding window” method, and a new method that I call “fixed-width window fracdiff” (FFD).

### 5.5.1 Expanding Window

Let us discuss how to fractionally differentiate a (finite) time series in practice. Suppose a time series with  $T$  real observations,  $\{X_t\}$ ,  $t = 1, \dots, T$ . Because of data limitations, the fractionally differentiated value  $\tilde{X}_T$  cannot be computed on an infinite series of weights. For instance, the last point  $\tilde{X}_T$  will use weights  $\{\omega_k\}$ ,  $k = 0, \dots, T - 1$ , and  $\tilde{X}_{T-l}$  will use weights  $\{\omega_k\}$ ,  $k = 0, \dots, T - l - 1$ . This means that the initial points will have a different amount of memory compared to the final points. For each  $l$ , we can determine the relative weight-loss,  $\lambda_l = \frac{\sum_{j=T-l}^T |\omega_j|}{\sum_{i=0}^{T-1} |\omega_i|}$ . Given a tolerance level  $\tau \in [0, 1]$ , we can determine the value  $l^*$  such that  $\lambda_{l^*} \leq \tau$  and  $\lambda_{l^*+1} > \tau$ . This value  $l^*$  corresponds to the first results  $\{\tilde{X}_t\}_{t=1,\dots,l^*}$  where the weight-loss is beyond the acceptable threshold,  $\lambda_t > \tau$  (e.g.,  $\tau = 0.01$ ).

From our earlier discussion, it is clear that  $\lambda_{l^*}$  depends on the convergence speed of  $\{\omega_k\}$ , which in turn depends on  $d \in [0, 1]$ . For  $d = 1$ ,  $\omega_k = 0$ ,  $\forall k > 1$ , and  $\lambda_l = 0$ ,  $\forall l > 1$ , hence it suffices to drop  $\tilde{X}_1$ . As  $d \rightarrow 0^+$ ,  $l^*$  increases, and a larger portion of the initial  $\{\tilde{X}_t\}_{t=1,\dots,l^*}$  needs to be dropped in order to keep the weight-loss  $\lambda_{l^*} \leq \tau$ . Figure 5.3 plots the E-mini S&P 500 futures trade bars of size 1E4, rolled forward, fractionally differentiated, with parameters  $(d = .4, \tau = 1)$  on the top and parameters  $(d = .4, \tau = 1E - 2)$  on the bottom.

The negative drift in both plots is caused by the negative weights that are added to the initial observations as the window is expanded. When we do not control for weight loss, the negative drift is extreme, to the point that only that trend is visible. The negative drift is somewhat more moderate in the right plot, after controlling

be exited at  $T_i$ , its final profit/loss is  $\pi_{i,T_i}$ . At the onset of each opportunity, the goal is to realize an expected profit  $E_0[\pi_{i,T_i}] = m_i(E_0[P_{i,T_i}] - P_{i,0})$ , where  $E_0[P_{i,T_i}]$  is the forecasted price and  $P_{i,0}$  is the entry level of opportunity  $i$ .

**Definition 1: Trading Rule:** A trading rule for strategy  $S$  is defined by the set of parameters  $R := \{\underline{\pi}, \bar{\pi}\}$ .

One way to calibrate (by brute force) the trading rule is to:

1. 1. Define a set of alternative values of  $R, \Omega := \{R\}$ .
2. 2. Simulate historically (backtest) the performance of  $S$  under alternative values of  $R \in \Omega$ .
3. 3. Select the optimal  $R^*$ .

More formally:

$$R^* = \arg \max_{R \in \Omega} \{SR_R\}$$

$$SR_R = \frac{E[\pi_{i,T_i} | R]}{\sigma[\pi_{i,T_i} | R]} \quad (13.1)$$

where  $E[\cdot]$  and  $\sigma[\cdot]$  are respectively the expected value and standard deviation of  $\pi_{i,T_i}$ , conditional on trading rule  $R$ , over  $i = 1, \dots, I$ . In other words, equation (13.1) maximizes the Sharpe ratio of  $S$  on  $I$  opportunities over the space of alternative trading rules  $R$  (see Bailey and L�pez de Prado [2012] for a definition and analysis of the Sharpe ratio). Because we count with two variables to maximize  $SR_R$  over a sample of size  $I$ , it is easy to overfit  $R$ . A trivial overfit occurs when a pair  $(\underline{\pi}, \bar{\pi})$  targets a few outliers. Bailey et al. [2017] provide a rigorous definition of backtest overfitting, which can be applied to our study of trading rules as follows.

**Definition 2: Overfit Trading Rule:**  $R^*$  is overfit if  $E \left[ \frac{E[\pi_{j,T_j} | R^*]}{\sigma[\pi_{j,T_j} | R^*]} \right] < \text{Me}_\Omega \left[ E \left[ \frac{E[\pi_{j,T_j} | R]}{\sigma[\pi_{j,T_j} | R]} \right] \right]$ , where  $j = I + 1, \dots, J$  and  $\text{Me}_\Omega[\cdot]$  is the median.

Intuitively, an optimal in-sample (IS,  $i \in [1, I]$ ) trading rule  $R^*$  is overfit when it is expected to underperform the median of alternative trading rules  $R \in \Omega$  out-of-sample (OOS,  $j \in [I + 1, J]$ ). This is essentially the same definition we used in chapter 11 to derive PBO. Bailey et al. [2014] argue that it is hard not to overfit a backtest, particularly when there are free variables able to target specific observations IS, or the number of elements in  $\Omega$  is large. A trading rule introduces such free variables,

because  $R^*$  can be determined independently from  $S$ . The outcome is that the backtest profits from random noise IS, making  $R^*$  unfit for OOS opportunities. Those same authors show that overfitting leads to negative performance OOS when  $\Delta\pi_{i,t}$  exhibits serial dependence. While PBO provides a useful method to evaluate to what extent a backtest has been overfit, it would be convenient to avoid this problem in the first place.<sup>2</sup> To that aim we dedicate the following section.

### 13.4 OUR FRAMEWORK

Until now we have not characterized the stochastic process from which observations  $\pi_{i,t}$  are drawn. We are interested in finding an optimal trading rule (OTR) for those scenarios where overfitting would be most damaging, such as when  $\pi_{i,t}$  exhibits serial correlation. In particular, suppose a discrete Ornstein-Uhlenbeck (O-U) process on prices

$$P_{i,t} = (1 - \varphi) E_0[P_{i,T_i}] + \varphi P_{i,t-1} + \sigma \varepsilon_{i,t} \quad (13.2)$$

such that the random shocks are IID distributed  $\varepsilon_{i,t} \sim N(0, 1)$ . The seed value for this process is  $P_{i,0}$ , the level targeted by opportunity  $i$  is  $E_0[P_{i,T_i}]$ , and  $\varphi$  determines the speed at which  $P_{i,0}$  converges towards  $E_0[P_{i,T_i}]$ . Because  $\pi_{i,t} = m_i(P_{i,t} - P_{i,0})$ , equation (13.2) implies that the performance of opportunity  $i$  is characterized by the process

$$\frac{1}{m_i} \pi_{i,t} = (1 - \varphi) E_0[P_{i,T_i}] - P_{i,0} + \varphi P_{i,t-1} + \sigma \varepsilon_{i,t} \quad (13.3)$$

From the proof to Proposition 4 in Bailey and L�pez de Prado [2013], it can be shown that the distribution of the process specified in equation (13.2) is Gaussian with parameters

$$\pi_{i,t} \sim N \left[ m_i \left( (1 - \varphi) E_0[P_{i,T_i}] \sum_{j=0}^{t-1} \varphi^j - P_{i,0} \right), m_i^2 \sigma^2 \sum_{j=0}^{t-1} \varphi^{2j} \right] \quad (13.4)$$

and a necessary and sufficient condition for its stationarity is that  $\varphi \in (-1, 1)$ . Given a set of input parameters  $\{\sigma, \varphi\}$  and initial conditions  $\{P_{i,0}, E_0[P_{i,T_i}]\}$  associated with opportunity  $i$ , is there an OTR  $R^* := (\underline{\pi}, \bar{\pi})$ ? Similarly, should strategy  $S$  predict a profit target  $\bar{\pi}$ , can we compute the optimal stop-loss  $\underline{\pi}$  given the input values  $\{\sigma, \varphi\}$ ? If the answer to these questions is affirmative, no backtest would be needed in order to determine  $R^*$ , thus avoiding the problem of overfitting the trading rule. In the next section we will show how to answer these questions experimentally.

<sup>2</sup> The strategy may still be the result of backtest overfitting, but at least the trading rule would not have contributed to that problem.

- •  $a = (n + \theta^2)(\pi_+ - \pi_-)^2$
- •  $b = [2n\pi_- - \theta^2(\pi_+ - \pi_-)] (\pi_+ - \pi_-)$
- •  $c = n\pi_-^2$

As a side note, Snippet 15.2 verifies these symbolic operations using SymPy Live: <http://live.sympy.org/>.

## SNIPPET 15.2 USING THE SymPy LIBRARY FOR SYMBOLIC OPERATIONS

```
>>> from sympy import *
>>> init_printing(use_unicode=False,wrap_line=False,no_global=True)
>>> p,u,d=symbols('p u d')
>>> m2=p*u**2+(1-p)*d**2
>>> m1=p*u+(1-p)*d
>>> v=m2-m1**2
>>> factor(v)
```

The above equation answers the following question: Given a trading rule characterized by parameters  $\{\pi_-, \pi_+, n\}$ , what is the precision rate  $p$  required to achieve a Sharpe ratio of  $\theta^*$ ? For example, for  $n = 260$ ,  $\pi_- = -.01$ ,  $\pi_+ = .005$ , in order to get  $\theta = 2$  we require a  $p = .72$ . Thanks to the large number of bets, a very small change in  $p$  (from  $p = .7$  to  $p = .72$ ) has propelled the Sharpe ratio from  $\theta = 1.173$  to  $\theta = 2$ . On the other hand, this also tells us that the strategy is vulnerable to small changes in  $p$ . Snippet 15.3 implements the derivation of the implied precision. Figure 15.2 displays the implied precision as a function of  $n$  and  $\pi_-$ , where  $\pi_+ = 0.1$  and  $\theta^* = 1.5$ . As  $\pi_-$  becomes more negative for a given  $n$ , a higher  $p$  is required to achieve  $\theta^*$  for a given  $\pi_+$ . As  $n$  becomes smaller for a given  $\pi_-$ , a higher  $p$  is required to achieve  $\theta^*$  for a given  $\pi_+$ .

## SNIPPET 15.3 COMPUTING THE IMPLIED PRECISION

```
def binHR(sl,pt,freq,tSR):
    ' ' '

    Given a trading rule characterized by the parameters {sl,pt,freq},
    what's the min precision  $p$  required to achieve a Sharpe ratio tSR?
1) Inputs
sl: stop loss threshold
pt: profit taking threshold
freq: number of bets per year
```