import requests
import random
import time
import pandas as pd

BASE_URL = "http://127.0.0.1:5000"

HEADERS = {
    "Connection": "Close"
}

def populate_users_and_products(count, product_count):
    """
    Inserts multiple user and product records into the database for testing purposes.
    Args:
        count (int): The number of users to insert.
        product_count (int): The number of products (tech) to associate with each user.
    """
    for i in range(count):
        user_data = {
            "username": f"user_{i}",
            "password": "password"
        }
        user_response = requests.post(f"{BASE_URL}/users", json=user_data, headers=HEADERS)
        if user_response.status_code != 200:
            print(f"Error inserting user data: {user_response.json()}")
            continue
        user_id = user_response.json()['id']

        for j in range(product_count):
            product_data = {
                "name": f"tech_{j}",
                "brand": f"brand_{j}",
                "price": round(j * 1.5, 2),
                "user_id": user_id
            }
            product_response = requests.post(f"{BASE_URL}/products", json=product_data, headers=HEADERS)
            if product_response.status_code != 200:
                print(f"Error inserting product data: {product_response.json()}")

def measure_execution_time(func, *args):
    """
    Measures the execution time of a given function.
    Args:
        func (function): The function to measure.
        *args: Arguments to pass to the function.
    Returns:
        float: The execution time in seconds.
    """
    start_time = time.time()
    func(*args)
    return time.time() - start_time

def test_select_users_and_products():
    """Performs a GET request to retrieve all users and products."""
    response_users = requests.get(f"{BASE_URL}/users", headers=HEADERS)
    response_products = requests.get(f"{BASE_URL}/products", headers=HEADERS)
    
    if response_users.status_code != 200:
        print(f"Error fetching users: {response_users.json()}")
    if response_products.status_code != 200:
        print(f"Error fetching products: {response_products.json()}")

def test_insert_product():
    """Performs a POST request to insert a single test product record."""
    data = {
        "name": "Test_Tech",
        "brand": "Test_Brand",
        "price": 200.0,
        "user_id": 1
    }
    response = requests.post(f"{BASE_URL}/products", json=data, headers=HEADERS)
    if response.status_code != 200:
        print(f"Error inserting product data: {response.json()}")

def test_update_product():
    """Performs a PUT request to update a specific product record."""
    data = {
        "name": "Updated_Tech",
        "brand": "Updated_Brand",
        "price": 250.0,
        "user_id": 1
    }
    response = requests.put(f"{BASE_URL}/products/1", json=data, headers=HEADERS)
    if response.status_code != 200:
        print(f"Error updating product data: {response.json()}")

def test_delete_product():
    """Performs a DELETE request to remove a specific product record."""
    response = requests.delete(f"{BASE_URL}/products/1", headers=HEADERS)
    if response.status_code != 200:
        print(f"Error deleting product data: {response.json()}")

def run_tests(test_sizes):
    """
    Runs API performance tests for specified record sizes.
    Args:
        test_sizes (list): A list of record sizes to test.
    Returns:
        pd.DataFrame: A DataFrame containing performance metrics.
    """
    results = []

    for size in test_sizes:
        print(f"Testing with {size} records...")

        # Measure populate time for users and products
        populate_time = measure_execution_time(populate_users_and_products, size, 10)

        # Measure time for other operations
        select_time = measure_execution_time(test_select_users_and_products)
        insert_time = measure_execution_time(test_insert_product)
        update_time = measure_execution_time(test_update_product)
        delete_time = measure_execution_time(test_delete_product)

        results.append({
            "size": size,
            "populate_time": populate_time,
            "select_time": select_time,
            "insert_time": insert_time,
            "update_time": update_time,
            "delete_time": delete_time
        })

        print(f"Completed testing for {size} records.")

    return pd.DataFrame(results)

if __name__ == "__main__":
    TEST_SIZES = [1000, 10000, 100000]  # You can add more sizes if needed
    results_df = run_tests(TEST_SIZES)

    results_file = "results.csv"
    results_df.to_csv(results_file, index=False)
    print(f"Results saved to {results_file}")