function addExpense() {
  const container = document.getElementById("expenses-container");

  const div = document.createElement("div");
  div.classList.add("expense_item");

  div.innerHTML = `
    <div class="item">
      <label>Amount:</label>
      <input type="number" name="amount[]" required />
    </div>

    <div class="item">
      <label>Description:</label>
      <textarea name="description[]" required></textarea>
    </div>

    <div class="misc_item">
      <button class="remove_button" type="button"
        onclick="this.closest('.expense_item').remove()">
        <ion-icon name="remove"></ion-icon> Remove
      </button>
    </div>
  `;

  container.appendChild(div);

  scrollToBottom();
}

function scrollToBottom(smooth = false) {
  const container = document.getElementById("expenses-container");

  container.scrollTo({
    top: container.scrollHeight,
    behavior: smooth ? "smooth" : "auto",
  });
}
