// https://stackoverflow.com/a/15133763

document.onreadystatechange = function () {
  if (document.readyState == "complete") {
    const logout = document.querySelector("#logoutButton");
    logout.onclick = onLogoutEventHandler;
    const deleteForms = document.querySelectorAll(".deleteForm");
    for (let i = 0; i < deleteForms.length; i++) {
      deleteForms[i].onsubmit = onDeleteEventHandler;
    }
  }
};

// used to display the confirmation modal when deleting an asset
function onDeleteEventHandler() {
  return confirm("Are you sure you want to delete this asset?");
}
// used to display the confirmation modal when logging out
function onLogoutEventHandler() {
  return confirm("Are you sure you want to Log Out?");
}
