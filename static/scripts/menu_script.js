function add_to_db(productName, productPrice) {
  fetch("http://0.0.0.0:5000/api/v1/users/{{ user.id }}/carts", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      item: productName,
      price: productPrice,
    }),
  })
    .then((response) => {
      if (response.ok) {
        return response.json();
      }
      throw new Error("Network response was not ok.");
    })
    .then((data) => {
      const cart_id = data.id;
      const new_button =
        '<button id="removeButton" class="cart" onclick="remove_from_db(' +
        cart_id +
        ')">Remove from cart</button>';
      const addButton = $(document)
        .find('.item:contains("' + productName + '")')
        .siblings(".cart");
      addButton.replaceWith(new_button);
    });
}

function remove_from_db(cart_id) {
  fetch("http://0.0.0.0:5000/api/v1/carts/" + cart_id, {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => {
      if (response.ok) {
        const addBut =
          "<button id='cartButton' class='cart' onclick='add_to_db()'>Add to cart</button>";
        $("#removeButton").replaceWith(addBut);
      } else {
        throw new Error("Network response was not ok.");
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      // You may want to display an error message to the user if something goes wrong
    });
}
