import numpy as np

from iclearn.model.utils.linear_functions import (
    get_mse,
    gradient_descent_iter,
    solve_analytical,
    get_rsquared,
    generate_basic,
)


# Test get_mse() function
def test_get_mse():
    y = np.array([1.0, 2.0, 3.0])
    y_pred = np.array([1.0, 2.0, 4.0])

    mse = get_mse(y_pred, y)
    expected_mse = np.square(y - y_pred).mean()

    # Check if mse is close to expected_mse with tolerance 1e-8
    assert np.isclose(
        mse, expected_mse, atol=1e-8
    ), f"Expected {expected_mse}, but got {mse}"


# Test solve_analytical() function
def test_solve_analytical():
    x = np.array([1.0, 2.0, 3.0])
    y = np.array([2.0, 4.0, 6.0])
    w, b = solve_analytical(x, y)

    # Check if w is close to 2 and b to 0 with tolerance 1e-8
    assert np.isclose(w, 2.0, atol=1e-8), f"Expected w to be 2.0, but got {w}"
    assert np.isclose(b, 0.0, atol=1e-8), f"Expected b to be 0.0, but got {b}"


# Test gradient_descent_iter() function
def test_gradient_descent_iter():
    x = np.array([1.0, 2.0, 3.0])
    y = np.array([2.0, 4.0, 6.0])
    w, b = 0.0, 0.0
    lr = 0.1

    updated_w, updated_b, mse = gradient_descent_iter(w, b, x, y, lr)

    # Check if updated parameters is close to the initial ones
    assert not np.isclose(
        updated_w, w, atol=1e-8
    ), f"Expected w to be updated, but it stayed {updated_w}"
    assert not np.isclose(
        updated_b, b, atol=1e-8
    ), f"Expected b to be updated, but it stayed {updated_b}"
    # Check that mse is float
    assert isinstance(
        mse, float
    ), f"Expected mse to be of type 'float', but got {type(mse)}"


# Test get_rsquared() function
def test_get_rsquared():
    x = np.array([1.0, 2.0, 3.0])
    y = np.array([2.0, 4.0, 6.0])
    w, b = 2.0, 1.0

    rsquared = get_rsquared(w, b, x, y)

    # Check if rsquared is between 0 and 1
    assert (
        0 <= rsquared <= 1
    ), f"Expected rsquared to be between 0 and 1, but got {rsquared}"


# Test generate_basic() function
def test_generate_basic():
    w, b = 2.0, 1.0
    dim = 10
    x = np.linspace(0, 1, dim)

    y = generate_basic(w=w, b=b, dim=dim)
    expected_y = w * x + b

    # Checek output size
    assert len(y) == dim, f"Expected result length to be {dim}, but got {len(y)}"
    # Check if y is close to expected_y with tolerance 1e-8
    assert np.allclose(y, expected_y, atol=1e-8), f"Expected {expected_y}, but got {y}"
