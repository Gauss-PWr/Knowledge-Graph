providing some more details. (Our aim is to produce a simple example, not a particularly realistic one.) Recall that the agent makes a decision at times determined by external events (or by other parts of the robot's control system). At each such time the robot decides whether it should (1) actively search for a can, (2) remain stationary and wait for someone to bring it a can, or (3) go back to home base to recharge its battery. Suppose the environment works as follows. The best way to find cans is to actively search for them, but this runs down the robot's battery, whereas waiting does not. Whenever the robot is searching, the possibility exists that its battery will become depleted. In this case the robot must shut down and wait to be rescued (producing a low reward).

The agent makes its decisions solely as a function of the energy level of the battery. It can distinguish two levels, **high** and **low**, so that the state set is  $\mathcal{S} = \{\text{high, low}\}$ . Let us call the possible decisions—the agent’s actions—**wait**, **search**, and **recharge**. When the energy level is **high**, recharging would always be foolish, so we do not include it in the action set for this state. The agent’s action sets are

$$\mathcal{A}(\text{high}) = \{\text{search, wait}\}$$
1(low) {search, wait,

$$\mathcal{A}(\text{low}) = \{\text{search, wait, recharge}\}.$$

If the energy level is **high**, then a period of active search can always be completed without risk of depleting the battery. A period of searching that begins with a **high** energy level leaves the energy level **high** with probability  $\alpha$  and reduces it to **low** with probability  $1 - \alpha$ . On the other hand, a period of searching undertaken when the energy level is **low** leaves it **low** with probability  $\beta$  and depletes the battery with probability  $1 - \beta$ . In the latter case, the robot must be rescued, and the battery is then recharged back to **high**. Each can collected by the robot counts as a unit reward, whereas a reward of  $-3$  results whenever the robot has to be rescued. Let  $r_{\text{search}}$  and  $r_{\text{wait}}$ , with  $r_{\text{search}} > r_{\text{wait}}$ , respectively denote the expected number of cans the robot will collect (and hence the expected reward) while searching and while waiting. Finally, to keep things simple, suppose that no cans can be collected during a run home for recharging, and that no cans can be collected on a step in which the battery is depleted. This system is then a finite MDP, and we can write down the transition probabilities and the expected rewards, as in Table 3.1.

A *transition graph* is a useful way to summarize the dynamics of a finite MDP. Figure 3.3 shows the transition graph for the recycling robot example. There are two kinds of nodes: *state nodes* and *action nodes*. There is a state node for each possible state (a large open circle labeled by the name of the state), and an action node for each state–action pair (a small solid circle labeled

state individually. Instead, the agent would have to maintain v<sup>π</sup> and q<sup>π</sup> as parameterized functions and adjust the parameters to better match the observed returns. This can also produce accurate estimates, although much depends on the nature of the parameterized function approximator (Chapter 9).

A fundamental property of value functions used throughout reinforcement learning and dynamic programming is that they satisfy particular recursive relationships. For any policy  $\pi$  and any state  $s$ , the following consistency condition holds between the value of  $s$  and the value of its possible successor states:

$$\begin{aligned}
v_{\pi}(s) &= \mathbb{E}_{\pi}[G_t \mid S_t = s] \\
&= \mathbb{E}_{\pi} \left[ \sum_{k=0}^{\infty} \gamma^k R_{t+k+1} \mid S_t = s \right] \\
&= \mathbb{E}_{\pi} \left[ R_{t+1} + \gamma \sum_{k=0}^{\infty} \gamma^k R_{t+k+2} \mid S_t = s \right] \\
&= \sum_a \pi(a|s) \sum_{s'} \sum_r p(s', r|s, a) \left[ r + \gamma \mathbb{E}_{\pi} \left[ \sum_{k=0}^{\infty} \gamma^k R_{t+k+2} \mid S_{t+1} = s' \right] \right] \\
&= \sum_a \pi(a|s) \sum_{s', r} p(s', r|s, a) \left[ r + \gamma v_{\pi}(s') \right], \tag{3.12}
\end{aligned}$$

where it is implicit that the actions,  $a$ , are taken from the set  $\mathcal{A}(s)$ , the next states,  $s'$ , are taken from the set  $\mathcal{S}$  (or from  $\mathcal{S}^+$  in the case of an episodic problem), and the rewards,  $r$ , are taken from the set  $\mathcal{R}$ . Note also how in the last equation we have merged the two sums, one over all the values of  $s'$  and the other over all values of  $r$ , into one sum over all possible values of both. We will use this kind of merged sum often to simplify formulas. Note how the final expression can be read very easily as an expected value. It is really a sum over all values of the three variables,  $a$ ,  $s'$ , and  $r$ . For each triple, we compute its probability,  $\pi(a|s)p(s', r|s, a)$ , weight the quantity in brackets by that probability, then sum over all possibilities to get an expected value.

Equation (3.12) is the *Bellman equation for  $v_\pi$* . It expresses a relationship between the value of a state and the values of its successor states. Think of looking ahead from one state to its possible successor states, as suggested by Figure 3.4a. Each open circle represents a state and each solid circle represents a state–action pair. Starting from state  $s$ , the root node at the top, the agent could take any of some set of actions—three are shown in Figure 3.4a. From each of these, the environment could respond with one of several next states,  $s'$ , along with a reward,  $r$ . The Bellman equation (3.12) averages over all the possibilities, weighting each by its probability of occurring. It states that the

they instead select an action at random. That is, all nongreedy actions are given the minimal probability of selection,  $\frac{\epsilon}{|\mathcal{A}(s)|}$ , and the remaining bulk of the probability,  $1 - \epsilon + \frac{\epsilon}{|\mathcal{A}(s)|}$ , is given to the greedy action. The  $\epsilon$ -greedy policies are examples of  $\epsilon$ -soft policies, defined as policies for which  $\pi(a|s) \geq \frac{\epsilon}{|\mathcal{A}(s)|}$  for all states and actions, for some  $\epsilon > 0$ . Among  $\epsilon$ -soft policies,  $\epsilon$ -greedy policies are in some sense those that are closest to greedy.

The overall idea of on-policy Monte Carlo control is still that of GPI. As in Monte Carlo ES, we use first-visit MC methods to estimate the action-value function for the current policy. Without the assumption of exploring starts, however, we cannot simply improve the policy by making it greedy with respect to the current value function, because that would prevent further exploration of nongreedy actions. Fortunately, GPI does not require that the policy be taken all the way to a greedy policy, only that it be moved *toward* a greedy policy. In our on-policy method we will move it only to an  $\epsilon$ -greedy policy. For any  $\epsilon$ -soft policy,  $\pi$ , any  $\epsilon$ -greedy policy with respect to  $q_\pi$  is guaranteed to be better than or equal to  $\pi$ .

That any  $\varepsilon$ -greedy policy with respect to  $q_\pi$  is an improvement over any  $\varepsilon$ -soft policy  $\pi$  is assured by the policy improvement theorem. Let  $\pi'$  be the  $\varepsilon$ -greedy policy. The conditions of the policy improvement theorem apply because for any  $s \in \mathcal{S}$ :

$$\begin{aligned}
q_{\pi}(s, \pi'(s)) &= \sum_a \pi'(a|s) q_{\pi}(s, a) \\
&= \frac{\epsilon}{|\mathcal{A}(s)|} \sum_a q_{\pi}(s, a) + (1 - \epsilon) \max_a q_{\pi}(s, a) \\
&\geq \frac{\epsilon}{|\mathcal{A}(s)|} \sum_a q_{\pi}(s, a) + (1 - \epsilon) \sum_a \frac{\pi(a|s) - \frac{\epsilon}{|\mathcal{A}(s)|}}{1 - \epsilon} q_{\pi}(s, a)
\end{aligned} \tag{5.2}$$

(the sum is a weighted average with nonnegative weights summing to 1, and as such it must be less than or equal to the largest number averaged)

= |A(s)| X a <sup>q</sup>π(s, a) − |A(s)| X a <sup>q</sup>π(s, a) + X a <sup>π</sup>(a|s)qπ(s, a) = vπ(s).

Thus, by the policy improvement theorem,  $\pi' \geq \pi$  (i.e.,  $v_{\pi'}(s) \geq v_{\pi}(s)$ , for all  $s \in \mathcal{S}$ ). We now prove that equality can hold only when both  $\pi'$  and  $\pi$  are optimal among the  $\varepsilon$ -soft policies, that is, when they are better than or equal to all other  $\varepsilon$ -soft policies.

Consider a new environment that is just like the original environment, except with the requirement that policies be  $\varepsilon$ -soft “moved inside” the environment. The new environment has the same action and state set as the original

Input: the policy  $\pi$  to be evaluated  
Initialize  $V(s)$  arbitrarily (e.g.,  $V(s) = 0, \forall s \in S^+$ )  
Repeat (for each episode):  
  Initialize  $S$   
  Repeat (for each step of episode):  
     $A \leftarrow$  action given by  $\pi$  for  $S$   
    Take action  $A$ ; observe reward,  $R$ , and next state,  $S'$   
     $V(S) \leftarrow V(S) + \alpha[R + \gamma V(S') - V(S)]$   
     $S \leftarrow S'$   
until  $S$  is terminal

Figure 6.1: Tabular TD(0) for estimating  $v_\pi$ .

Figure 6.2: The backup diagram for TD(0).

the backup diagram is updated on the basis of the one sample transition from it to the immediately following state. We refer to TD and Monte Carlo updates as *sample backups* because they involve looking ahead to a sample successor state (or state–action pair), using the value of the successor and the reward along the way to compute a backed-up value, and then changing the value of the original state (or state–action pair) accordingly. *Sample* backups differ from the *full* backups of DP methods in that they are based on a single sample successor rather than on a complete distribution of all possible successors.

**Example 6.1: Driving Home** Each day as you drive home from work, you try to predict how long it will take to get home. When you leave your office you note the time, the day of week, and anything else that might be relevant. Say on this Friday you are leaving at exactly 6 o'clock, and you estimate that it will take 30 minutes to get home. As you reach your car it is 6:05, and you notice it is starting to rain. Traffic is often slower in the rain, so you reestimate that it will take 35 minutes from then, or a total of 40 minutes. Fifteen minutes later you have completed the highway portion of your journey in good time. As you exit onto a secondary road you cut your estimate of total travel time to 35 minutes. Unfortunately, at this point you get stuck behind a slow truck, and the road is too narrow to pass. You end up having to follow the truck until you turn onto the side street where you live at 6:40. Three minutes later you are home. The sequence of states, times, and predictions is

upward. For example, if you are one cell to the right of the goal, then the action **left** takes you to the cell just above the goal. Let us treat this as an undiscounted episodic task, with constant rewards of  $-1$  until the goal state is reached. Figure 6.11 shows the result of applying  $\epsilon$ -greedy Sarsa to this task, with  $\epsilon = 0.1$ ,  $\alpha = 0.5$ , and the initial values  $Q(s, a) = 0$  for all  $s, a$ . The increasing slope of the graph shows that the goal is reached more and more quickly over time. By 8000 time steps, the greedy policy (shown inset) was long since optimal; continued  $\epsilon$ -greedy exploration kept the average episode length at about 17 steps, two more than the minimum of 15. Note that Monte Carlo methods cannot easily be used on this task because termination is not guaranteed for all policies. If a policy was ever found that caused the agent to stay in the same state, then the next episode would never end. Step-by-step learning methods such as Sarsa do not have this problem because they quickly learn *during the episode* that such policies are poor, and switch to something else. ■

## 6.5 Q-Learning: Off-Policy TD Control

One of the most important breakthroughs in reinforcement learning was the development of an off-policy TD control algorithm known as *Q-learning* (Watkins, 1989). Its simplest form, *one-step Q-learning*, is defined by

$$Q(S_t, A_t) \leftarrow Q(S_t, A_t) + \alpha \left[ R_{t+1} + \gamma \max_a Q(S_{t+1}, a) - Q(S_t, A_t) \right]. \quad (6.6)$$
In this case, the learned action value function  $Q$  directly approximates  $a$ 

In this case, the learned action-value function,  $Q$ , directly approximates  $q_*$ , the optimal action-value function, independent of the policy being followed. This dramatically simplifies the analysis of the algorithm and enabled early convergence proofs. The policy still has an effect in that it determines which state-action pairs are visited and updated. However, all that is required for correct convergence is that all pairs continue to be updated. As we observed in Chapter 5, this is a minimal requirement in the sense that any method guaranteed to find optimal behavior in the general case must require it. Under this assumption and a variant of the usual stochastic approximation conditions on the sequence of step-size parameters,  $Q$  has been shown to converge with probability 1 to  $q_*$ . The Q-learning algorithm is shown in procedural form in Figure 6.12.

What is the backup diagram for Q-learning? The rule (6.6) updates a state–action pair, so the top node, the root of the backup, must be a small, filled action node. The backup is also *from* action nodes, maximizing over all those actions possible in the next state. Thus the bottom nodes of the backup diagram should be all these action nodes. Finally, remember that we indicate

are the moment-by-moment one-step TD errors. For example, the TD error for state-value prediction is

$$\delta_t = R_{t+1} + \gamma V_t(S_{t+1}) - V_t(S_t). \quad (7.10)$$

In the backward view of  $\text{TD}(\lambda)$ , the global TD error signal triggers proportional updates to all recently visited states, as signaled by their nonzero traces:

$$\Delta V_t(s) = \alpha \delta_t E_t(s), \quad \text{for all } s \in \mathcal{S}. \quad (7.11)$$

As always, these increments could be done on each step to form an on-line algorithm, or saved until the end of the episode to produce an off-line algorithm. In either case, equations (7.8–7.11) provide the mechanistic definition of the TD( $\lambda$ ) algorithm. A complete algorithm for on-line TD( $\lambda$ ) is given in Figure 7.7.

The backward view of  $TD(\lambda)$  is oriented backward in time. At each moment we look at the current TD error and assign it backward to each prior state according to the state’s eligibility trace at that time. We might imagine ourselves riding along the stream of states, computing TD errors, and shouting them back to the previously visited states, as suggested by Figure 7.8. Where the TD error and traces come together, we get the update given by (7.11).

To better understand the backward view, consider what happens at various values of  $\lambda$ . If  $\lambda = 0$ , then by (7.9) all traces are zero at  $t$  except for the trace corresponding to  $S_t$ . Thus the  $\text{TD}(\lambda)$  update (7.11) reduces to the simple TD

Initialize  $V(s)$  arbitrarily (but set to 0 if  $s$  is terminal)

Repeat (for each episode):

Initialize  $E(s) = 0$ , for all  $s \in \mathcal{S}$ 

Initialize  $S$ 

Repeat (for each step of episode):

 $A \leftarrow$  action given by  $\pi$  for  $S$ 

Take action  $A$ , observe reward,  $R$ , and next state,  $S'$ 

$$\delta \leftarrow R + \gamma V(S') - V(S)$$
 $E(S) \leftarrow E(S) + 1$  (accumulating traces)

or  $E(S) \leftarrow (1 - \alpha)E(S) + 1$  (dutch traces)

or  $E(S) \leftarrow 1$  (replacing traces)

For all  $s \in \mathcal{S}$ :

 $V(s) \leftarrow V(s) + \alpha \delta E(s)$ 

 $E(s) \leftarrow \gamma \lambda E(s)$ 

 $S \leftarrow S'$ 

until  $S$  is terminal