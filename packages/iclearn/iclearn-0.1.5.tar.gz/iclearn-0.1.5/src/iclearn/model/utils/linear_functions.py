import numpy as np


def get_mse(y_pred, y):
    """
    A basic MSE implementation, useful for testing things out
    """

    return np.square(y - y_pred).mean()


def gradient_descent_iter(w, b, x, y, lr):

    f = y - (w * x + b)
    w -= lr * (-2.0 * x * f).mean()  # partial derivative dmse_dw
    b -= lr * (-2.0 * f).mean()  # partial derivative dmse_db
    mse = get_mse(y, w * x + b)
    return w, b, mse


def solve_analytical(x, y):

    x = np.column_stack([np.ones(len(x)), x])  # column of to represent b
    x_t = np.transpose(x)
    theta = np.linalg.inv(x_t @ x) @ x_t @ y

    return theta[1], theta[0]


def get_rsquared(w, b, x, y):
    y_pred = w * x + b
    ss_res = np.sum((y_pred - y) ** 2)
    ss_tot = np.sum((y - np.average(y)) ** 2)
    return 1.0 - ss_res / ss_tot


def gradient_descent(x, y, lr=0.2, num_epoch=50):

    w = 0.0
    b = 0.0
    for idx in range(num_epoch):
        w, b, mse = gradient_descent_iter(w, b, x, y, lr)
        print(f"gradient descent: epoch {idx}, w {w:0.3f}, b {w:0.3f}, mse {mse:0.5f}")


def generate_basic(w: float = 0.5, b: float = 0.5, dim: int = 10):
    x = np.linspace(0, 1, dim)
    return w * x + b


def gradient_descent_batch(x, y, lr=0.1, num_epochs=10, batch_size=10):

    w = 0.0
    b = 0.0

    num_batches = (len(x) + batch_size - 1) // batch_size

    for idx in range(num_epochs):
        for batch_idx in range(num_batches):
            start_idx, end_idx = batch_idx * batch_size, min(
                (batch_idx + 1) * batch_size, len(x)
            )
            batch_x, batch_y = x[start_idx:end_idx], y[start_idx:end_idx]
            w, b, mse = gradient_descent_iter(w, b, batch_x, batch_y, lr)

    return w, b
