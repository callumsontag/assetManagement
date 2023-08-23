// https://stackoverflow.com/a/15133763
document.onreadystatechange = function () {
  if (document.readyState == "complete") {
    const deleteForms = document.querySelectorAll(".deleteForm");
    for (let i = 0; i < deleteForms.length; i++) {
      deleteForms[i].onsubmit = onSubmitEventHandler;
    }
  }
};

function onSubmitEventHandler() {
  return confirm("Are you sure you want to delete this asset?");
}
