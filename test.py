from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import requests
import os

# Initialize the WebDriver
driver = webdriver.Chrome()

try:
    # Open the E-Shop Checkout page
    file_path = os.path.abspath("checkout.html")
    driver.get(f"file:///{file_path}")
    # Update with the correct path

    # Add items to the cart
    driver.find_element(By.XPATH, "//button[contains(text(), 'Add to Cart') and preceding-sibling::span[contains(text(), 'Product A')]]").click()
    driver.find_element(By.XPATH, "//button[contains(text(), 'Add to Cart') and preceding-sibling::span[contains(text(), 'Product B')]]").click()

    # Apply discount code
    discount_input = driver.find_element(By.ID, "discountCode")
    discount_input.send_keys("SAVE15")
    discount_input.send_keys(Keys.RETURN)

    # Wait for the discount to be applied
    time.sleep(2)

    # Check if the discount was applied
    discount_message = driver.find_element(By.ID, "discountMessage").text
    total_value = float(driver.find_element(By.ID, "total").text)

    assert "Discount applied!" in discount_message, "Discount message not as expected"
    assert total_value == (50 + 30) * 0.85, "Total value after discount is incorrect"

    # Simulate API call to verify discount application
    response = requests.post("http://your_api_endpoint/apply_coupon", json={"code": "SAVE15"})
    response_data = response.json()

    assert response_data.get("discount_applied") is True, "API did not confirm discount application"
    assert response_data.get("discount_percentage") == 15, "API did not confirm correct discount percentage"

finally:
    # Close the WebDriver
    driver.quit()