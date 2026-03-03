document.addEventListener("DOMContentLoaded", () => {

    let addDatasetBtn = document.getElementById("addDatasetBtn");
    addDatasetBtn.addEventListener("click", async () => {
        let errorMsg = document.getElementById("errorMsg");
        errorMsg.textContent = "";

        let fileInput = document.getElementById("csvFile");
        const formData = new FormData();
        formData.append("file", fileInput.files[0]);

        let allowedExtensions = /(\.csv)$/i;
        if (!fileInput.value) {
            errorMsg.textContent = "Моля, качете файл!";
            return;
        } else if (!allowedExtensions.exec(fileInput.value)) {
            errorMsg.textContent = "Невалиден файлов формат!";
            return;
        }

        try {
            const response = await fetch("/api/add-dataset", {
                method: "POST",
                body: formData
            });

            if (response.ok) {
                Swal.fire({
                    title: "Наборът данни е качен успешно!",
                    icon: "success",
                    confirmButtonColor: "#3085d6",
                    confirmButtonText: "ОК"
                }).then(() => {
                    window.location.replace("/experiment");
                });
            } else {
                const error = await response.json();
                Swal.fire({
                    title: "Грешка!",
                    icon: "error",
                    text: error.error,
                    confirmButtonColor: "#3085d6",
                    confirmButtonText: "ОК"
                })
            }
        } catch (error) {
            alert("Неуспешно качване:", error);
        }
    })
})



async function uploadFile() {

}