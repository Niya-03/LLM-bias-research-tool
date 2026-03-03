document.addEventListener("DOMContentLoaded", () => {
    let existingCatRadio = document.getElementById('existingCategoryRadio')
    let newCatRadio = document.getElementById('newCategoryRadio')

    let categorySelect = document.getElementById('categorySelect')
    let subcategorySelect = document.getElementById('subcategorySelect')

    let categoryInput = document.getElementById('categoryInput')
    let subcategoryInput = document.getElementById('subcategoryInput')

    existingCatRadio.addEventListener("change", () => {
        if (existingCatRadio.checked) {
            categorySelect.disabled = false;
            subcategorySelect.disabled = false;

            categoryInput.disabled = true;
            subcategoryInput.disabled = true;
        }
    })

    newCatRadio.addEventListener("change", () => {
        if (newCatRadio.checked) {
            categoryInput.disabled = false;
            subcategoryInput.disabled = false;

            categorySelect.disabled = true;
            subcategorySelect.disabled = true;
        }
    })

})