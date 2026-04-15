const search = document.querySelector(".input-group input"),
  table_rows = document.querySelectorAll("tbody tr"),
  table_headings = document.querySelectorAll("thead th");

table_headings.forEach((head, i) => {
  let sort_asc = true;
  head.onclick = () => {
    table_headings.forEach((head) => head.classList.remove("active"));
    head.classList.add("active");

    document
      .querySelectorAll("td")
      .forEach((td) => td.classList.remove("active"));
    table_rows.forEach((row) => {
      row.querySelectorAll("td")[i].classList.add("active");
    });

    head.classList.toggle("asc", sort_asc);
    sort_asc = head.classList.contains("asc") ? false : true;

    sortTable(i, sort_asc);
  };
});

function sortTable(column, sort_asc) {
  [...table_rows]
    .sort((a, b) => {
      let first = a.querySelectorAll("td")[column].textContent;
      let second = b.querySelectorAll("td")[column].textContent;

      // 👉 If sorting AMOUNT column (example: column 0)
      if (column === 0) {
        first = parseFloat(first.replace(/[^\d.-]/g, ""));
        second = parseFloat(second.replace(/[^\d.-]/g, ""));
      } else {
        first = first.toLowerCase();
        second = second.toLowerCase();
      }

      return sort_asc ? (first > second ? 1 : -1) : first < second ? 1 : -1;
    })
    .forEach((row) => document.querySelector("tbody").appendChild(row));
}

/*=============== SHOW MENU ===============*/
const showMenu = (toggleId, navId) => {
  const toggle = document.getElementById(toggleId),
    nav = document.getElementById(navId);

  toggle.addEventListener("click", () => {
    // Add show-menu class to nav menu
    nav.classList.toggle("show-menu");

    // Add show-icon to show and hide the menu icon
    toggle.classList.toggle("show-icon");
  });
};

showMenu("nav-toggle", "nav-menu");

function changeDate(direction) {
  const element = document.getElementById("current-date");

  let current = new Date(element.dataset.date);

  current.setDate(current.getDate() + direction);

  const newDate = current.toISOString().split("T")[0];

  window.location.href = `/expenses?date=${newDate}`;
}
