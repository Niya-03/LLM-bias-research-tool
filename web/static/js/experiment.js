
document.addEventListener("DOMContentLoaded", () => {

    loadSelectSubcategories();

    const categorySelect = document.getElementById("categorySelect");
    categorySelect.addEventListener("change", async () => {
        loadSelectSubcategories()
    });

    const resultsBtn = document.getElementById("resultsBtn");
    resultsBtn.addEventListener("click", generateResults);
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

async function generateResults() {
    const datasetSelect = document.querySelector("select[aria-label='Select dataset']");
    const categorySelect = document.getElementById("categorySelect");
    const subcategorySelect = document.getElementById("subcategorySelect");
    const modelSelect = document.querySelector("select[aria-label='Select a model']");

    const dataset = datasetSelect.value;
    const category = categorySelect.value;
    const subcategory = subcategorySelect.value;
    const model = modelSelect.value;

    if (!dataset || !category || !subcategory || !model) {
        alert("Please select all options before generating results");
        return;
    }

    try {
        const response = await fetch("/api/generate-results", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                dataset,
                category,
                subcategory,
                model
            })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `${category}_${model}_results.zip`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } else {
            const error = await response.json();
            alert(`Error: ${error.error}`);
        }
    } catch (error) {
        console.error("Error generating results:", error);
        alert("Error generating results. Check the console for details.");
    }
}
