function setError(errorText) {
    if (errorText) {
        error_field.hidden = false;
        error_field.children[0].innerText = errorText;
    } else {
        error_field.hidden = true;
        error_field.children[0].innerText = "";
    }
}

async function deleteToDoListCallback(event) {
    if (confirm("Do you really want to delete this to-do list?")) {
        let response = await fetchWithShowingErrorToUser(
            `to_do_list/delete/${event.target.dataset.to_do_list_id}`
        );
        if (response.error) {
            setError(response.error);
        } else {
            event.target.parentElement.remove();
        }
    }
    return false;
}

async function addToDoList(toDoList, where="afterbegin") {
    let listItem = document.createElement("li");
    let viewHyperlink = document.createElement("a");
    viewHyperlink.href = `to_do_list/view/${toDoList.id}`;
    viewHyperlink.append(toDoList.title);
    listItem.append(viewHyperlink);
    let deletionHyperlink = document.createElement("a");
    deletionHyperlink.dataset.to_do_list_id = toDoList.id;
    deletionHyperlink.href = "#";
    deletionHyperlink.addEventListener("click", deleteToDoListCallback);
    deletionHyperlink.append("Delete");
    listItem.append(" | ");
    listItem.append(deletionHyperlink);
    to_do_lists.insertAdjacentElement(where, listItem);
}

async function fetchWithShowingErrorToUser(url, parameters) {
    try {
        let response = await fetch(url, parameters);
        if (response.ok) {
            let body = await response.text();
            alert(body);
            if (body == "") {
                return null;
            } else {
                return JSON.parse(body);
            }
        } else {
            throw new Error(`${response.status} (${response.statusText})`);
        }
    } catch (error) {
        setError(error);
    }
}

async function createToDoList() {
    let title = to_do_list_creation_form.elements["title"].value;
    if (title) {
        let toDoListInfo = await fetchWithShowingErrorToUser(
            "to_do_list/create/", {
                method: "POST",
                body: new FormData(to_do_list_creation_form),
            }
        );
        if (toDoListInfo.error) {
            setError(toDoListInfo.error);
        } else {
            setError("");
            addToDoList({
                id: toDoListInfo.id,
                title,
            });
        }
    } else {
        setError("You haven't provided a title for a to-do list!");
    }
}

window.addEventListener(
    "DOMContentLoaded",
    () => fetchWithShowingErrorToUser("to_do_list/get_to_do_lists").then(
        (toDoLists) => {
            for (let toDoList of toDoLists) {
                addToDoList(toDoList, "beforeend");
            }
        }
    ),
);