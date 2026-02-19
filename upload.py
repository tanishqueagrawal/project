const formData = new FormData();
formData.append("file", fileInput.files[0]);

fetch("http://localhost:5000/upload", {
  method: "POST",
  headers: {
    Authorization: "Bearer " + token
  },
  body: formData
});
