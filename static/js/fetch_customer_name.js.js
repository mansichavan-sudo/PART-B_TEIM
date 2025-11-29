
function fetchCustomerName(selectElement) {
    const customerId = selectElement.value;
    if (customerId) {
        fetch(`/get_customer_name/?customer_id=${customerId}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('id_customer_name').value = data.customer_name;
        })
        .catch(error => console.error('Error fetching customer name:', error));
    }
}

