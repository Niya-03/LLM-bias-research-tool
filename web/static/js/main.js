document.addEventListener("DOMContentLoaded", () => {
    async function loadHTML(id, file) {
        const container = document.querySelectorAll(`#${id}`);
        if (!container.length) return;

        try {
            const response = await fetch(file);
            const html = await response.text();
            container.forEach(c => {
                c.innerHTML = html;
            })

        } catch (error) {
            console.error("Error loading html:", file, error);
        }
    }

    loadHTML("headerContainer", "partials/header.html")
    loadHTML("footerContainer", "./partials/footer.html")

})

