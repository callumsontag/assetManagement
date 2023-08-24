// https://stackoverflow.com/a/15133763
document.onreadystatechange = function () {
  if (document.readyState == "complete") {
    const deleteForms = document.querySelectorAll(".deleteForm");
    for (let i = 0; i < deleteForms.length; i++) {
      deleteForms[i].onsubmit = onDeleteEventHandler;
    }
  }
};

document.onreadystatechange = function () {
  if (document.readyState == "complete") {
    const logout = document.querySelector("#logoutButton");
    logout.onclick = onLogoutEventHandler;
  }
};

function onDeleteEventHandler() {
  return confirm("Are you sure you want to delete this asset?");
}

function onLogoutEventHandler() {
  return confirm("Are you sure you want to Log Out?");
}
