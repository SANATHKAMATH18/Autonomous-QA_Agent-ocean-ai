from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os

# Initialize the WebDriver
driver = webdriver.Chrome()

try:
    # Open the E-Shop Checkout page
    file_path = os.path.abspath("checkout.html")
    driver.get(f"file:///{file_path}")

    # Add products to the cart
    driver.find_element(By.XPATH, "//button[contains(text(), 'Add to Cart') and preceding-sibling::span[contains(text(), 'Product A')]]").click()
    driver.find_element(By.XPATH, "//button[contains(text(), 'Add to Cart') and preceding-sibling::span[contains(text(), 'Product B')]]").click()

    # Wait for the cart to update
    time.sleep(1)

    # Enter the discount code
    discount_input = driver.find_element(By.ID, "discountCode")
    discount_input.send_keys("SAVE15")

    # Apply the discount
    driver.find_element(By.XPATH, "//button[contains(text(), 'Apply')]").click()

    # Wait for the discount to be applied
    time.sleep(1)

    # Verify the discount application
    total_element = driver.find_element(By.ID, "total")
    discount_message = driver.find_element(By.ID, "discountMessage")

    # Calculate expected total after 15% discount
    original_total = 50 + 30  # Product A + Product B
    expected_total = original_total - (original_total * 0.15)

    # Check if the total is updated correctly
    assert float(total_element.text) == round(expected_total, 2), "Total after discount is incorrect."

    # Check if the success message is displayed
    assert discount_message.text == "Discount applied!", "Discount success message is not displayed."

finally:
    # Close the WebDriver
    driver.quit()