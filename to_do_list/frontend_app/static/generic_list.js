class GenericList {
    readableListElementName = undefined;
    errorFieldName = "error_field";
    listElementName = "list";
    listElementsCreationFormName = "list_elements_creation_form";

    constructor(props) {
        Object.assign(this, props);
    }

    getDeletionURL(itemId) {
        return undefined;
    }

    getCreationURL() {
        return undefined;
    }

    getGetterURL() {
        return undefined;
    }

    async deleteListElementCallback(event) {
        if (confirm(
            `Do you really want to delete this ${this.readableListElementName}?`
        )) {
            let response = await this.fetchWithShowingErrorToUser(
                this.getDeletionURL(event.target.dataset.item_id)
            );
            if (response.error) {
                setError(response.error);
            } else {
                event.target.parentElement.remove();
            }
        }
    }

    setError(errorText) {
        let errorField = document.getElementById(this.errorFieldName);
        if (errorText) {
            errorField.hidden = false;
            errorField.children[0].innerText = errorText;
        } else {
            errorField.hidden = true;
            errorField.children[0].innerText = "";
        }
    }

    makeListItemTitle(listElement) {
        return listElement.title;
    }

    addListElement(listElement, where="afterbegin") {
        let listItem = document.createElement("li");
        listItem.append(this.makeListItemTitle(listElement));
        let deleteButton = document.createElement("button");
        deleteButton.append("Delete");
        deleteButton.style["margin-left"] = "0.5em";
        deleteButton.dataset.item_id = listElement.id;
        deleteButton.addEventListener(
            "click", this.deleteListElementCallback.bind(this)
        );
        listItem.append(deleteButton);
        let list = document.getElementById(this.listElementName);
        list.insertAdjacentElement(where, listItem);
        deleteButton.style.position = "static";
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
            this.setError(
                `You haven't provided a title for a ${self.readableListElementName}!`
            );
        }
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