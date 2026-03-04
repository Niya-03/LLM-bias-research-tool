document.addEventListener("DOMContentLoaded", () => {

    let datasetSelect = document.getElementById("datasetSelect")

    let existingCatRadio = document.getElementById('existingCategoryRadio')
    let newCatRadio = document.getElementById('newCategoryRadio')

    let categorySelect = document.getElementById('categorySelect')
    let subcategorySelect = document.getElementById('subcategorySelect')

    let categoryInput = document.getElementById('categoryInput')
    let subcategoryInput = document.getElementById('subcategoryInput')

    let polaritySelect = document.getElementById('polaritySelect');

    let addStatementBtn = document.getElementById('addStatementBtn')
    let bg_statementInput = document.getElementById('statementBg')
    let en_statementInput = document.getElementById('statementEn')

    addStatementBtn.addEventListener('click', async ()=>{
        let selectedDataset = datasetSelect.value;
        let useExistingCategory = existingCatRadio.checked;
        let category;
        let subcategory;
        let polarity = polaritySelect.value;
        let bg_statement = bg_statementInput.value;
        let en_statement = en_statementInput.value;


        if(useExistingCategory){
            category = categorySelect.value;
            subcategory = subcategorySelect.value;
        }else{
            category = categoryInput.value;
            subcategory = subcategoryInput.value;

            if(!category || !subcategory){
                Swal.fire({
                    title: "Грешка!",
                    icon: "error",
                    text: "Попълнете всички полета!",
                    confirmButtonColor: "#3085d6",
                    confirmButtonText: "ОК"
                })
                return;
            }
        }

        if(!bg_statement || !en_statement){
            Swal.fire({
                    title: "Грешка!",
                    icon: "error",
                    text: "Попълнете всички полета!",
                    confirmButtonColor: "#3085d6",
                    confirmButtonText: "ОК"
                })
            return;
        }

        try {
        const response = await fetch("/api/add-statement", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                selectedDataset,
                useExistingCategory,
                category,
                subcategory,
                polarity,
                bg_statement,
                en_statement
               
            })
        });

        if (response.ok) {
            Swal.fire({
                title: "Успех!",
                icon: "success",
                text: "Редът е добавен успешно!",
                confirmButtonColor: "#3085d6",
                confirmButtonText: "ОК"
            }).then(() => {
                // Reset form
                document.getElementById('statementBg').value = '';
                document.getElementById('statementEn').value = '';
            });
        } else {
            const error = await response.json();
            Swal.fire({
                title: "Грешка!",
                icon: "error",
                text: error.error || "Възникна грешка при добавяне на реда!",
                confirmButtonColor: "#3085d6",
                confirmButtonText: "ОК"
            });
        }
    } catch (error) {
        console.error("Error adding statement:", error);
        Swal.fire({
            title: "Грешка!",
            icon: "error",
            text: "Възникна грешка. Проверете конзолата за детайли.",
            confirmButtonColor: "#3085d6",
            confirmButtonText: "ОК"
        });
    }

        
    })

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

    existingCatRadio.checked = true;
    categorySelect.disabled = false;
    subcategorySelect.disabled = false;
    categoryInput.disabled = true;
    subcategoryInput.disabled = true;

    loadSelectSubcategories();


    categorySelect.addEventListener("change", async () => {
        loadSelectSubcategories()
    });

})

async function loadSelectSubcategories() {
    const categorySelect = document.getElementById("categorySelect");
    const subcategorySelect = document.getElementById("subcategorySelect");
    const datasetSelect = document.querySelector("select[aria-label='Select dataset']");

    const category = categorySelect.value;
    const dataset = datasetSelect.value;

    if (!category) {
        subcategorySelect.innerHTML = '<option value="">Choose category first</option>';
        return;
    }

    try {
        const response = await fetch(`/api/subcategories?dataset=${dataset}&category=${category}`);
        const data = await response.json();

        if (response.ok) {
            subcategorySelect.innerHTML = data.subcategories
                .map(sub => `<option value="${sub}">${sub}</option>`)
                .join("");
        } else {
            subcategorySelect.innerHTML = `<option value="">Error: ${data.error}</option>`;
        }
    } catch (error) {
        console.error("Error fetching subcategories:", error);
        subcategorySelect.innerHTML = '<option value="">Error loading subcategories</option>';
    }
}

