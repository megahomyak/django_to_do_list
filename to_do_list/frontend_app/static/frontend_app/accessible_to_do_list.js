function checkAndClearSelection() {
    let selection = document.getSelection();
    let selectionExists = selection.type != "None";
    if (selectionExists) {
        if (selection.empty) {
            selection.empty();
        } else {
            selection.removeAllRanges();
        }
    }
    return selectionExists;
}


class ToDoList extends GenericList {
    readableListElementName = "task";
    postRequestsElementIdFieldName = "task_id";

    constructor(toDoListId) {
        super();
        this.toDoListId = toDoListId;
    }

    addListElement(listElement, where="afterbegin") {
        let listItem = super.addListElement(...arguments);
        let checkBox = document.createElement("input");
        checkBox.type = "checkbox";
        checkBox.classList.add("checkbox");
        checkBox.checked = listElement.is_done;
        checkBox.addEventListener("change", this.checkBoxWasPressed.bind(this));
        listItem.prepend(checkBox);
    }

    checkBoxWasPressed(event) {
        let checkBox = event.target;
        let listItem = checkBox.parentElement;
        let titleElement = listItem.querySelector(".title");
        if (checkBox.checked) {
            titleElement.style["text-decoration"] = "line-through";
        } else {
            titleElement.style["text-decoration"] = "";
        }
        let request_form = new FormData();
        request_form.append("csrfmiddlewaretoken", csrfMiddlewareToken);
        request_form.append("new_state", +checkBox.checked);
        request_form.append("task_id", checkBox.parentElement.dataset.record_id);
        this.fetchWithShowingErrorToUser("/api/tasks/change_state/", {
            method: "POST",
            body: request_form,
        });
    }

    getCreationFormData(listElementsCreationForm) {
        let form_data = new FormData(listElementsCreationForm);
        form_data.append("to_do_list_id", this.toDoListId);
        return form_data;
    }

    getDeletionURL(itemId) {
        return "/api/tasks/delete/";
    }

    getCreationURL() {
        return "/api/tasks/create/";
    }

    getGetterURL() {
        return `/api/to_do_lists/${this.toDoListId}/`;
    }

    makeListItemTitle(listElement) {
        let title = document.createElement("span");
        title.innerText = listElement.title;
        if (listElement.is_done) {
            title.style["text-decoration"] = "line-through";
        }
        title.draggable = "true";
        title.classList.add("draggable");
        title.addEventListener("dragstart", this.handleDragStart.bind(this));
        title.addEventListener("dragend", this.handleDragEnd.bind(this));
        return title;
    }

    async sendEditedElementTitleToTheBackEnd(elementId, requestForm) {
        requestForm.append("task_id", elementId);
        return await this.fetchWithShowingErrorToUser(
            "/api/tasks/rename/", {
                method: "POST",
                body: requestForm,
            }
        );
    }

    handleDragStart(event) {
        if (checkAndClearSelection()) {
            return;
        }
        event.target.classList.add("dragging");
    }

    handleDragOver(event) {
        event.preventDefault();
        let list = document.getElementById(this.listElementName);
        let listContents = list.children;
        let draggedElement = document.querySelector(".dragging")?.parentElement;
        if (!draggedElement) {
            return;
        }
        for (let listItem of listContents) {
            let boundingBox = listItem.getBoundingClientRect();
            if (boundingBox.top <= event.clientY && event.clientY <= boundingBox.bottom) {
                let nextSibling = listItem.nextSibling;
                if (draggedElement.isSameNode(nextSibling)) {
                    list.insertBefore(draggedElement, listItem);
                } else {
                    list.insertBefore(draggedElement, nextSibling);
                }
                return;
            }
        }
    }

    handleDragEnd(event) {
        if (checkAndClearSelection()) {
            return;
        }
        event.target.classList.remove("dragging");
        let list = document.getElementById(this.listElementName);
        let listItem = event.target.closest("li");
        let order = list.childElementCount - [...list.children].indexOf(listItem);
        let requestForm = this.getFormDataWithCsrfToken();
        console.log("record id", listItem.dataset.record_id, "new order", order);
        requestForm.append("task_id", +listItem.dataset.record_id);
        requestForm.append("new_order", order);
        this.fetchWithShowingErrorToUser("/api/tasks/reorder/", {
            method: "POST",
            body: requestForm,
        });
    }

    bind() {
        super.bind();
        let list = document.getElementById(this.listElementName);
        list.addEventListener("dragover", this.handleDragOver.bind(this));
    }
}

let listObject = new ToDoList(toDoListId);
listObject.bind();