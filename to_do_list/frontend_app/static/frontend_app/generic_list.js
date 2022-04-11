function rebindButtonCallback(button, callback) {
    button.removeEventListener("click", button.lastCallback);
    button.lastCallback = callback;
    button.addEventListener("click", callback);
}


class GenericList {
    readableListElementName = undefined;
    errorFieldName = "error_field";
    listElementName = "list";
    listElementsCreationFormName = "list_elements_creation_form";
    postRequestsElementIdFieldName = undefined;

    getDeletionURL(itemId) {
        return undefined;
    }

    getCreationURL() {
        return undefined;
    }

    getGetterURL() {
        return undefined;
    }

    /**
     * Should return undefined if renaming was unsuccessful
     */
    sendEditedElementTitleToTheBackEnd(elementId, newElementTitle) {
        return undefined;
    }

    getFormDataWithCsrfToken() {
        let requestForm = new FormData();
        requestForm.append("csrfmiddlewaretoken", csrfMiddlewareToken);
        return requestForm;
    }

    async deleteListElementCallback(event) {
        if (confirm(
            `Do you really want to delete this ${this.readableListElementName}?`
        )) {
            let requestForm = this.getFormDataWithCsrfToken();
            requestForm.append(
                this.postRequestsElementIdFieldName,
                event.target.parentElement.dataset.record_id,
            );
            let response = await this.fetchWithShowingErrorToUser(
                this.getDeletionURL(), {
                    method: "POST",
                    body: requestForm,
                }
            );
            if (response.error) {
                this.setError(response.error);
            } else {
                event.target.parentElement.remove();
            }
        }
    }

    setError(errorText) {
        let errorField = document.getElementById(this.errorFieldName);
        if (errorText) {
            errorField.hidden = false;
            errorField.firstChild.innerText = errorText;
        } else {
            errorField.hidden = true;
            errorField.firstChild.innerText = "";
        }
    }

    makeListItemTitle(listElement) {
        let titleElement = document.createElement("span");
        titleElement.innerText = listElement.title;
        return titleElement;
    }

    editListElementCallback(event) {
        amountOfFieldsBeingEdited += 1;
        let button = event.target;
        rebindButtonCallback(
            button, this.saveEditedListElementTitleCallback.bind(this)
        );
        let listItem = button.parentElement;
        let titleElement = listItem.querySelector(".title");
        let inputField = listItem.querySelector(".input");
        inputField.value = titleElement.innerText;
        inputField.hidden = false;
        titleElement.hidden = true;
        button.innerText = "Save";
    }

    async saveEditedListElementTitleCallback(event) {
        let button = event.target;
        let listItem = button.parentElement;
        let inputField = listItem.querySelector(".input");
        let newTitle = inputField.value;
        if (newTitle == "") {
            this.setNoTitleProvidedError();
            return;
        }
        let requestForm = this.getFormDataWithCsrfToken();
        requestForm.append("new_title", newTitle);
        let response = await this.sendEditedElementTitleToTheBackEnd(
            listItem.dataset.record_id, requestForm,
        );
        if (response === undefined) {
            return;
        }
        this.setError("");
        rebindButtonCallback(
            button, this.editListElementCallback.bind(this)
        );
        amountOfFieldsBeingEdited -= 1;
        event.target.innerText = "Edit";
        let titleElement = listItem.querySelector(".title");
        titleElement.innerText = inputField.value;
        titleElement.hidden = false;
        inputField.hidden = true;
    }

    addListElement(listElement, where="afterbegin") {
        let listItem = document.createElement("li");
        listItem.dataset.record_id = listElement.id;
        let listTitleElement = this.makeListItemTitle(listElement);
        listTitleElement.classList.add("title");
        listItem.append(listTitleElement);
        let inputField = document.createElement("input");
        inputField.classList.add("input");
        inputField.hidden = true;
        listItem.append(inputField);
        let editButton = document.createElement("button");
        editButton.classList.add("edit");
        editButton.style["margin-left"] = "0.5em";
        editButton.append("Edit");
        {
            let lastCallback = this.editListElementCallback.bind(this);
            editButton.addEventListener("click", lastCallback);
            editButton.lastCallback = lastCallback;
        }
        listItem.append(editButton);
        let deleteButton = document.createElement("button");
        deleteButton.classList.add("delete");
        deleteButton.append("Delete");
        deleteButton.style["margin-left"] = "0.5em";
        deleteButton.addEventListener(
            "click", this.deleteListElementCallback.bind(this)
        );
        listItem.append(deleteButton);
        let list = document.getElementById(this.listElementName);
        list.insertAdjacentElement(where, listItem);
        return listItem;
    }

    getCreationFormData(listElementsCreationForm) {
        return new FormData(listElementsCreationForm);
    }

    async createElement() {
        let listElementsCreationForm = document.getElementById(
            this.listElementsCreationFormName
        );
        let title = listElementsCreationForm.elements["title"].value;
        if (title) {
            let toDoListInfo = await this.fetchWithShowingErrorToUser(
                this.getCreationURL(), {
                    method: "POST",
                    body: this.getCreationFormData(listElementsCreationForm),
                }
            );
            if (toDoListInfo.error) {
                this.setError(toDoListInfo.error);
            } else {
                this.setError("");
                this.addListElement({
                    id: toDoListInfo.id,
                    title,
                });
                listElementsCreationForm.reset();
            }
        } else {
            this.setNoTitleProvidedError();
        }
    }

    setNoTitleProvidedError() {
        this.setError(
            `You haven't provided a title for a ${this.readableListElementName}!`
        );
    }

    async fetchWithShowingErrorToUser(url, parameters) {
        try {
            let response = await fetch(url, parameters);
            if (response.ok) {
                return await response.json();
            } else {
                throw new Error(`${response.status} (${response.statusText})`);
            }
        } catch (error) {
            this.setError(error);
        }
    }

    bind() {
        window.addEventListener(
            "DOMContentLoaded",
            () => this.fetchWithShowingErrorToUser(this.getGetterURL()).then(
                (listContents) => {
                    for (let listItem of listContents) {
                        this.addListElement(listItem, "beforeend");
                    }
                }
            ),
        );
    }
}

let amountOfFieldsBeingEdited = 0;

window.addEventListener("beforeunload", function(event) {
    if (amountOfFieldsBeingEdited != 0) {
        event.preventDefault();
    }
});

const csrfMiddlewareToken = document.querySelector('[name=csrfmiddlewaretoken]').value;