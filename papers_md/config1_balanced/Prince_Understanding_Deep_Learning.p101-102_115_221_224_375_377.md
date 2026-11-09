$$\begin{aligned}\mathbf{m}_{t+1} & \leftarrow \beta \cdot \mathbf{m}_t + (1 - \beta) \sum_{i \in \mathcal{B}_t} \frac{\partial \ell_i[\phi_t - \alpha\beta \cdot \mathbf{m}_t]}{\partial \phi} \\ \phi_{t+1} & \leftarrow \phi_t - \alpha \cdot \mathbf{m}_{t+1},\end{aligned}\tag{6.12}$$

where now the gradients are evaluated at *ϕ<sup>t</sup> − αβ ·* **m***t*. One way to think about this is that the gradient term now corrects the path provided by momentum alone.

### **6.4 Adam**

Gradient descent with a fixed step size has the following undesirable property: it makes large adjustments to parameters associated with large gradients (where perhaps we should be more cautious) and small adjustments to parameters associated with small gradients (where perhaps we should explore further). When the gradient of the loss surface is much steeper in one direction than another, it is difficult to choose a learning rate that (i) makes good progress in both directions and (ii) is stable (figures 6.9a–b).

A straightforward approach is to normalize the gradients so that we move a fixed distance (governed by the learning rate) in each direction. To do this, we first measure the gradient  $\mathbf{m}_{t+1}$  and the pointwise squared gradient  $\mathbf{v}_{t+1}$ :

$$\begin{aligned}\mathbf{m}_{t+1} &\leftarrow \frac{\partial L[\phi_t]}{\partial \phi} \\ \mathbf{v}_{t+1} &\leftarrow \left( \frac{\partial L[\phi_t]}{\partial \phi} \right)^2.\end{aligned}\tag{6.13}$$

Then we apply the update rule:

$$\phi_{t+1} \leftarrow \phi_t - \alpha \cdot \frac{\mathbf{m}_{t+1}}{\sqrt{\mathbf{v}_{t+1}} + \epsilon}, \quad (6.14)$$

where the square root and division are both pointwise,  $\alpha$  is the learning rate, and  $\epsilon$  is a small constant that prevents division by zero when the gradient magnitude is zero. The term  $\mathbf{v}_{t+1}$  is the squared gradient, and the positive root of this is used to normalize the gradient itself, so all that remains is the sign in each coordinate direction. The result is that the algorithm moves a fixed distance  $\alpha$  along each coordinate, where the direction is determined by whichever way is downhill (figure 6.9c). This simple algorithm makes good progress in both directions but will not converge unless it happens to land exactly at the minimum. Instead, it will bounce back and forth around the minimum.

*Adaptive moment estimation, or Adam,* takes this idea and adds momentum to both the estimate of the gradient and the squared gradient:

<span id="page-102-0"></span>**Figure 6.9** Adaptive moment estimation (Adam). a) This loss function changes quickly in the vertical direction but slowly in the horizontal direction. If we run full-batch gradient descent with a learning rate that makes good progress in the vertical direction, then the algorithm takes a long time to reach the final horizontal position. b) If the learning rate is chosen so that the algorithm makes good progress in the horizontal direction, it overshoots in the vertical direction and becomes unstable. c) A straightforward approach is to move a fixed distance along each axis at each step so that we move downhill in both directions. This is accomplished by normalizing the gradient magnitude and retaining only the sign. However, this does not usually converge to the exact minimum but instead oscillates back and forth around it (here between the last two points). d) The Adam algorithm uses momentum in both the estimated gradient and the normalization term, which creates a smoother path.

<span id="page-115-0"></span>**Figure 7.4** Backpropagation backward pass #1. We work backward from the end of the function computing the derivatives *∂ℓi/∂f<sup>k</sup>* and *∂ℓi/∂h<sup>k</sup>* of the loss with respect to the intermediate quantities. Each derivative is computed from the previous one by multiplying by terms of the form *∂fk/∂h<sup>k</sup>* or *∂hk/∂fk−*1.

represent the effects of this chain. Notice that we already computed the second of these derivatives, and the other is the derivative of *β*<sup>3</sup> +*ω*<sup>3</sup> *· h*<sup>3</sup> with respect to *h*3, which is *ω*3.

We continue in this way, computing the derivatives of the output with respect to these intermediate quantities (figure [7.4](#page-115-0)):

<span id="page-115-1"></span>*∂ℓ<sup>i</sup> ∂f*<sup>2</sup> = *∂h*<sup>3</sup> *∂f*<sup>2</sup> *∂f*<sup>3</sup> *∂h*<sup>3</sup> *∂ℓ<sup>i</sup> ∂f*<sup>3</sup> *∂ℓ<sup>i</sup> ∂h*<sup>2</sup> = *∂f*<sup>2</sup> *∂h*<sup>2</sup> *∂h*<sup>3</sup> *∂f*<sup>2</sup> *∂f*<sup>3</sup> *∂h*<sup>3</sup> *∂ℓ<sup>i</sup> ∂f*<sup>3</sup> *∂ℓ<sup>i</sup> ∂f*<sup>1</sup> = *∂h*<sup>2</sup> *∂f*<sup>1</sup> *∂f*<sup>2</sup> *∂h*<sup>2</sup> *∂h*<sup>3</sup> *∂f*<sup>2</sup> *∂f*<sup>3</sup> *∂h*<sup>3</sup> *∂ℓ<sup>i</sup> ∂f*<sup>3</sup> *∂ℓ<sup>i</sup> ∂h*<sup>1</sup> = *∂f*<sup>1</sup> *∂h*<sup>1</sup> *∂h*<sup>2</sup> *∂f*<sup>1</sup> *∂f*<sup>2</sup> *∂h*<sup>2</sup> *∂h*<sup>3</sup> *∂f*<sup>2</sup> *∂f*<sup>3</sup> *∂h*<sup>3</sup> *∂ℓ<sup>i</sup> ∂f*<sup>3</sup> *∂ℓ<sup>i</sup> ∂f*<sup>0</sup> = *∂h*<sup>1</sup> *∂f*<sup>0</sup> *∂f*<sup>1</sup> *∂h*<sup>1</sup> *∂h*<sup>2</sup> *∂f*<sup>1</sup> *∂f*<sup>2</sup> *∂h*<sup>2</sup> *∂h*<sup>3</sup> *∂f*<sup>2</sup> *∂f*<sup>3</sup> *∂h*<sup>3</sup> *∂ℓ<sup>i</sup> ∂f*<sup>3</sup> *.* (7.13)

Problem 7.2

**Problem 7.2** In each case, we have already computed the quantities in the brackets in the previous step, and the last term has a simple expression. These equations embody Observation 2 from the previous section (figure 7.2); we can reuse the previously computed derivatives if we calculate them in reverse order.

**Backward pass #2:** Finally, we consider how the loss  $\ell_i$  changes when we change the parameters  $\{\beta_k\}$  and  $\{\omega_k\}$ . Once more, we apply the chain rule (figure 7.5):

$$\begin{aligned}\frac{\partial \ell_i}{\partial \beta_k} &= \frac{\partial f_k}{\partial \beta_k} \frac{\partial \ell_i}{\partial f_k} \\ \frac{\partial \ell_i}{\partial \omega_k} &= \frac{\partial f_k}{\partial \omega_k} \frac{\partial \ell_i}{\partial f_k}.\end{aligned}\tag{7.14}$$

In each case, the second term on the right-hand side was computed in equation 7.13. When  $k > 0$ , we have  $f_k = \beta_k + \omega_k \cdot h_k$ , so:

$$\frac{\partial f_k}{\partial \beta_k} = 1 \quad \text{and} \quad \frac{\partial f_k}{\partial \omega_k} = h_k. \quad (7.15)$$

Second, one of the defining characteristics of NLP problems is that each input (one or more sentences) is of a different length; hence, it's not even obvious how to apply a fully connected network. These observations suggest that the network should share parameters across words at different input positions, similarly to how convolutional networks share parameters across different image positions.

Third, language is ambiguous; it is unclear from the syntax alone that the pronoun it refers to the restaurant and not to the ham sandwich. To understand the text, the word it should somehow be connected to the word restaurant. In the parlance of transformers, the former word should pay *attention* to the latter. This implies that there must be connections between the words and that the strength of these connections will depend on the words themselves. Moreover, these connections need to extend across large text spans. For example, the word their in the last sentence also refers to the restaurant.

## **12.2 Dot-product self-attention**

The previous section argued that a model for processing text will (i) use parametere sharing to cope with long input passages of differing lengths and (ii) contain connections between word representations that depend on the words themselves. The transformer acquires both properties by using *dot-product self-attention*.

A standard neural network layer  $\mathbf{f}[\mathbf{x}]$ , takes a  $D \times 1$  input  $\mathbf{x}$  and applies a linear transformation followed by an activation function like a ReLU, so:

$$\mathbf{f}[\mathbf{x}] = \mathbf{ReLU}[\boldsymbol{\beta} + \boldsymbol{\Omega} \mathbf{x}], \quad (12.1)$$

where *β* contains the biases, and **Ω** contains the weights.

A self-attention block **sa[•]** takes  $N$  inputs  $\mathbf{x}_1, \dots, \mathbf{x}_N$ , each of dimension  $D \times 1$ , and returns  $N$  outputs, each of which is also of size  $D \times 1$ . In the context of NLP, each input represents a word or word fragment. First, a set of *values* are computed for each input:

$$\mathbf{v}_m = \boldsymbol{\beta}_v + \boldsymbol{\Omega}_v \mathbf{x}_m, \quad (12.2)$$

where  $\boldsymbol{\beta}_v \in \mathbb{R}^{D \times 1}$  and  $\boldsymbol{\Omega}_v \in \mathbb{R}^{D \times D}$  represent biases and weights, respectively.

Then the  $n^{th}$  output  $\mathbf{sa}_n[\mathbf{x}_1, \dots, \mathbf{x}_N]$  is a weighted sum of all the values  $\mathbf{v}_1, \dots, \mathbf{v}_N$ :

<span id="page-221-0"></span>
$$\mathbf{sa}_n[\mathbf{x}_1, \dots, \mathbf{x}_N] = \sum_{m=1}^N a[\mathbf{x}_m, \mathbf{x}_n] \mathbf{v}_m. \quad (12.3)$$

The scalar weight  $a[\mathbf{x}_m, \mathbf{x}_n]$  is the *attention* that the  $n^{th}$  output pays to input  $\mathbf{x}_m$ . The  $N$  weights  $a[\bullet, \mathbf{x}_n]$  are non-negative and sum to one. Hence, self-attention can be thought of as *routing* the values in different proportions to create each output (figure 12.1).

The following sections examine dot-product self-attention in more detail. First, we consider the computation of the values and their subsequent weighting (equation 12.3). Then we describe how to compute the attention weights  $a[\mathbf{x}_m, \mathbf{x}_n]$  themselves.

**Figure 12.3** Computing attention weights. a) Query vectors  $\mathbf{q}_n = \boldsymbol{\beta}_q + \boldsymbol{\Omega}_q \mathbf{x}_n$  and key vectors  $\mathbf{k}_n = \boldsymbol{\beta}_k + \boldsymbol{\Omega}_k \mathbf{x}_n$  are computed for each input  $\mathbf{x}_n$ . b) The dot products between each query and the three keys are passed through a softmax function to form non-negative attentions that sum to one. c) These route the value vectors (figure 12.1) via the sparse matrix from figure 12.2c.

the values, which is usually the same size as the input, so the representation doesn't change size.

Problems 12.1–12.2

## **12.2.3 Self-attention summary**

The  $n^{th}$  output is a weighted sum of the same linear transformation  $\mathbf{v}_\bullet = \beta_v + \mathbf{\Omega}_v \mathbf{x}_\bullet$  applied to all of the inputs, where these attention weights are positive and sum to one. The weights depend on a measure of similarity between input  $\mathbf{x}_n$  and the other inputs. There is no activation function, but the mechanism is nonlinear due to the dot-product and a softmax operation used to compute the attention weights.

Note that this mechanism fulfills the initial requirements. First, there is a single shared set of parameters  $\phi = \{\beta_v, \Omega_v, \beta_q, \Omega_q, \beta_k, \Omega_k\}$ . This is independent of the

$$\begin{aligned}
& \frac{(1 - \alpha_{t-1})}{1 - \alpha_t} \sqrt{1 - \beta_t} \mathbf{z}_t + \frac{\sqrt{\alpha_{t-1}} \beta_t}{1 - \alpha_t} \mathbf{x} \\
&= \frac{(1 - \alpha_{t-1})}{1 - \alpha_t} \sqrt{1 - \beta_t} \mathbf{z}_t + \frac{\sqrt{\alpha_{t-1}} \beta_t}{1 - \alpha_t} \left( \frac{1}{\sqrt{\alpha_t}} \mathbf{z}_t - \frac{\sqrt{1 - \alpha_t}}{\sqrt{\alpha_t}} \boldsymbol{\epsilon} \right) \\
&= \frac{(1 - \alpha_{t-1})}{1 - \alpha_t} \sqrt{1 - \beta_t} \mathbf{z}_t + \frac{\beta_t}{1 - \alpha_t} \left( \frac{1}{\sqrt{1 - \beta_t}} \mathbf{z}_t - \frac{\sqrt{1 - \alpha_t}}{\sqrt{1 - \beta_t}} \boldsymbol{\epsilon} \right),
\end{aligned} \tag{18.32}$$
we have used the fact that  $\sqrt{1 - \beta_t} / \sqrt{1 - \alpha_t} = \sqrt{1 - \beta_t} / \sqrt{1 - \alpha_t} = 1$  between the second and third

Problem 18.9

**Problem 18.9** where we have used the fact that  $\sqrt{\alpha_t}/\sqrt{\alpha_{t-1}} = \sqrt{1 - \beta_t}$  between the second and third lines. Simplifying further, we get:

(1 *<sup>−</sup> <sup>α</sup>t−*1) 1 *− α<sup>t</sup>* p 1 *− βt***z***<sup>t</sup>* + *√<sup>α</sup>t−*1*β<sup>t</sup>* 1 *− α<sup>t</sup>* **x** (18.33) = (1 *<sup>−</sup> <sup>α</sup>t−*1) *√* 1 *− β<sup>t</sup>* 1 *− α<sup>t</sup>* + *βt* (1 *− αt*) *√* 1 *− β<sup>t</sup>* **z***<sup>t</sup> − <sup>β</sup><sup>t</sup> √* 1 *− α<sup>t</sup> √* 1 *− β<sup>t</sup> ϵ* = (1 *<sup>−</sup> <sup>α</sup>t−*1)(1 *<sup>−</sup> <sup>β</sup>t*) (1 *− αt*) *√* 1 *− β<sup>t</sup>* + *βt* (1 *− αt*) *√* 1 *− β<sup>t</sup>* **z***<sup>t</sup> − <sup>β</sup><sup>t</sup> √* 1 *− α<sup>t</sup> √* 1 *− β<sup>t</sup> ϵ* = (1 *<sup>−</sup> <sup>α</sup>t−*1)(1 *<sup>−</sup> <sup>β</sup>t*) <sup>+</sup> *<sup>β</sup><sup>t</sup>* (1 *− αt*) *√* 1 *− β<sup>t</sup>* **z***<sup>t</sup> − <sup>β</sup><sup>t</sup> √* 1 *− α<sup>t</sup> √* 1 *− β<sup>t</sup> ϵ* = 1 *− α<sup>t</sup>* (1 *− αt*) *√* 1 *− β<sup>t</sup>* **z***<sup>t</sup> − <sup>β</sup><sup>t</sup> √* 1 *− α<sup>t</sup> √* 1 *− β<sup>t</sup> ϵ* = 1 *√* 1 *− β<sup>t</sup>* **z***<sup>t</sup> − <sup>β</sup><sup>t</sup> √* 1 *− α<sup>t</sup> √* 1 *− β<sup>t</sup> ϵ,*

where we have multiplied the numerator and denominator of the first term by *√* 1 *− β<sup>t</sup>* between lines two and three, multiplied out the terms, and simplified the numerator in

Problem 18.10

**Problem 18.10** the first term between lines three and four.  
Substituting this back into the loss function (equation 18.29), we have:

$$\begin{aligned} L[\phi_{1\dots T}] &= \sum_{i=1}^I \left( -\log \left[ \text{Norm}_{\mathbf{x}_i} \left[ \mathbf{f}_1[\mathbf{z}_{i1}, \phi_1], \sigma_1^2 \mathbf{I} \right] \right] \right. \\ &\quad \left. + \sum_{t=2}^T \frac{1}{2\sigma_t^2} \left\| \left( \frac{1}{\sqrt{1-\beta_t}} \mathbf{z}_{it} - \frac{\beta_t}{\sqrt{1-\alpha_t} \sqrt{1-\beta_t}} \epsilon_{it} \right) - \mathbf{f}_t[\mathbf{z}_{it}, \phi_t] \right\|^2 \right). \end{aligned} \quad (18.34)$$

# **18.5.2 Reparameterization of network**

Now we replace the model **<sup>z</sup>**ˆ*t−*<sup>1</sup> <sup>=</sup> **<sup>f</sup>***t*[**z***t, <sup>ϕ</sup><sup>t</sup>* ] with a new model ˆ*ϵ* = **g***<sup>t</sup>* [**z***t, ϕ<sup>t</sup>* ], which predicts the noise *ϵ* that was mixed with **x** to create **z***t*:

$$\mathbf{f}_t[\mathbf{z}_t, \phi_t] = \frac{1}{\sqrt{1 - \beta_t}} \mathbf{z}_t - \frac{\beta_t}{\sqrt{1 - \alpha_t} \sqrt{1 - \beta_t}} \mathbf{g}_t[\mathbf{z}_t, \phi_t]. \quad (18.35)$$

#### **Algorithm 18.1:** Diffusion model training

```
Input: Training data  $\mathbf{x}$ 
Output: Model parameters  $\phi_t$ 
repeat
  for  $i \in \mathcal{B}$  do            // For every training example index in batch
    |  $t \sim \text{Uniform}[1, \dots T]$       // Sample random timestep
    |  $\epsilon \sim \text{Norm}[0, \mathbf{I}]$           // Sample noise
    |  $\ell_i = \left\| \mathbf{g}_t \left[ \sqrt{\alpha_t} \mathbf{x}_i + \sqrt{1 - \alpha_t} \epsilon, \phi_t \right] - \epsilon \right\|^2$     // Compute individual loss
Accumulate losses for batch and take gradient step
until converged
```

#### **Algorithm 18.2:** Sampling

| <b>Input:</b>                                                                                                                                  | Model, $\mathbf{g}_t[\bullet, \phi_t]$                                                                                                                     |                                          |
|------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------|
| <b>Output:</b>                                                                                                                                 | Sample, $\mathbf{x}$                                                                                                                                       |                                          |
| $\mathbf{z}_T \sim \text{Norm}_{\mathbf{z}}[\mathbf{0}, \mathbf{I}]$                                                                           | // Sample last latent variable                                                                                                                             |                                          |
| <b>for</b>                                                                                                                                     | $t = T \dots 2$ <b>do</b>                                                                                                                                  |                                          |
|                                                                                                                                                | $\hat{\mathbf{z}}_{t-1} = \frac{1}{\sqrt{1-\beta_t}} \mathbf{z}_t - \frac{\beta_t}{\sqrt{1-\alpha_t} \sqrt{1-\beta_t}} \mathbf{g}_t[\mathbf{z}_t, \phi_t]$ | // Predict previous latent variable      |
|                                                                                                                                                | $\epsilon \sim \text{Norm}_{\epsilon}[\mathbf{0}, \mathbf{I}]$                                                                                             | // Draw new noise vector                 |
|                                                                                                                                                | $\mathbf{z}_{t-1} = \hat{\mathbf{z}}_{t-1} + \sigma_t \epsilon$                                                                                            | // Add noise to previous latent variable |
| $\mathbf{x} = \frac{1}{\sqrt{1-\beta_1}} \mathbf{z}_1 - \frac{\beta_1}{\sqrt{1-\alpha_1} \sqrt{1-\beta_1}} \mathbf{g}_1[\mathbf{z}_1, \phi_1]$ | // Generate sample from $\mathbf{z}_1$ without noise                                                                                                       |                                          |

## **18.6.1 Application to images**

Diffusion models have been very successful in modeling image data. Here, we need to construct models that can take a noisy image and predict the noise that was added at each step. The obvious architectural choice for this image-to-image mapping is the U-Net (figure 11.10). However, there may be a very large number of diffusion steps, and training and storing multiple U-Nets is inefficient. The solution is to train a single U-Net that also takes a predetermined vector representing the time step as input (figure 18.9). In practice, this is resized to match the number of channels at each stage of the U-Net and used to offset and/or scale the representation at each spatial position.

A large number of time steps are needed as the conditional probabilities *<sup>q</sup>*(**z***t−*1*|***z***t*) become closer to normal when the hyperparameters *β<sup>t</sup>* are close to zero, matching the form of the decoder distributions *P r*(**z***t−*1*|***z***t, <sup>ϕ</sup><sup>t</sup>* ). However, this makes sampling slow. We might have to run the U-Net model through *T* = 1000 steps to generate good images.

#### **18.6.2 Improving generation speed**

The loss function (equation 18.40) requires the diffusion kernel to have the form  $q(\mathbf{z}_t | \mathbf{x}) = \text{Norm}[\sqrt{\alpha_t} \mathbf{x}, \sqrt{1 - \alpha_t} \cdot \mathbf{I}]$ . The same loss function will be valid for *any* forward process