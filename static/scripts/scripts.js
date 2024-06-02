document.getElementById('playlistForm').addEventListener('submit', function() {
    document.getElementById('loadingOverlay').style.display = 'flex';
  });

  let inputFile = document.getElementById('img');
  let fileNameField = document.getElementById('file-name');
  let dropZone = document.getElementById('drop-zone');

  inputFile.addEventListener('change', function(event){
    let uploadedFileName = event.target.files[0].name;
    fileNameField.textContent = uploadedFileName;
  });

  dropZone.addEventListener('dragover', function(event) {
    event.preventDefault();
    dropZone.classList.add('dragover');
  });

  dropZone.addEventListener('dragleave', function() {
    dropZone.classList.remove('dragover');
  });

  dropZone.addEventListener('drop', function(event) {
    event.preventDefault();
    dropZone.classList.remove('dragover');
    let files = event.dataTransfer.files;
    inputFile.files = files;
    let uploadedFileName = files[0].name;
    fileNameField.textContent = uploadedFileName;
  });

  VANTA.NET({
    el: "#bg",
    mouseControls: true,
    touchControls: true,
    gyroControls: false,
    minHeight: 200.00,
    minWidth: 200.00,
    scale: 1.00,
    scaleMobile: 1.00,
    color: 0x3fffaf
  });