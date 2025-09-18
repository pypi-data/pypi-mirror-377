# Tversky Neural Network - PyTorch

Implementation of [Tversky Neural Networks](https://arxiv.org/abs/2506.11035) in PyTorch. 

[Tversky (1977)](https://pages.ucsd.edu/~scoulson/203/tversky-features.pdf) argued that similarity judgments can be regarded as extensions of similarity statements. Such statements are directional, in the sense that "a is like b" may differ from "b is like a." However, most neural network architectures in deep learning model similarity through dot-product measures, which are symmetric and therefore have generally not incorporated asymmetry, given the challenges of representing it in differentiable form. Motivated by Tversky's insight, [Doumbouya et al. (2025)](https://arxiv.org/pdf/2506.11035) has introduced architectures that incorporate **asymmetric similarity**.

From **set** form,

<img width="813" height="47" alt="image" src="https://github.com/user-attachments/assets/5ac6e6d1-3985-448a-b53f-ed68d7c88dd4" />

to **differentiable vector** form.

<img width="968" height="237" alt="image" src="https://github.com/user-attachments/assets/8b2c3e26-af61-452a-8a4c-959a8ba3191f" />

<img width="965" height="264" alt="image" src="https://github.com/user-attachments/assets/a3b9bd17-f89e-4952-8b14-0a63ce4fcb39" />



## Install

```bash
$ pip install tversky-neural-network-pytorch
```

## Usage

Tversky Projection Layer

```python
import torch
from tversky_neural_network import TverskyProjectionLayer

model = TverskyProjectionLayer(
    in_features = 32,
    out_features = 16,
    num_features = 8,
    alpha = 0.5,
    beta = 0.5,
    theta = 1.0,
    eps = 1e-8,
    psi = "softmin",
    softmin_tau = 0.8,
    match_type = "subtract",
)

x = torch.randn(10, 32, device=device)
out = model(x)

loss = out.sum()
loss.backward()
```

## Develop in Docker

1. Start the development environment:

    ```bash
    $ docker compose up -d 
    ```

2. Access docker container terminal with:

    ```bash
    $ docker exec -it dev /bin/bash
    ```

    Exit terminal with `CTRL + D`.

3. Stop docker container with:

    ```bash
    $ docker compose down
    ```

4. In container terminal, execute scripts with:

    ```bash
    $ uv run python your_script.py
    # test
    $ uv run pytest -v
    ```
    
## Citations

```bibtex
@article{doumbouya2025tversky,
  title={Tversky Neural Networks: Psychologically Plausible Deep Learning with Differentiable Tversky Similarity},
  author={Doumbouya, Moussa Koulako Bala and Jurafsky, Dan and Manning, Christopher D},
  journal={arXiv preprint arXiv:2506.11035},
  year={2025}
}
```

```bibtex
@article{tversky1977features,
  title={Features of similarity.},
  author={Tversky, Amos},
  journal={Psychological review},
  volume={84},
  number={4},
  pages={327},
  year={1977},
  publisher={American Psychological Association}
}
```