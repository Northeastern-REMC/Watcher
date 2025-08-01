document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".dropdown-toggle").forEach(item => {
    item.addEventListener("click", () => {
      const subList = item.querySelector(".sub-list");
      if (subList) {
        subList.classList.toggle("show");
        item.classList.toggle("open");
      }
    });
  });
});