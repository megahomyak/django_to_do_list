class ToDoList extends GenericList {
    readableListElementName = "task";
    postRequestsElementIdFieldName = "task_id";

    constructor(toDoListId) {
        super();
        this.toDoListId = toDoListId;
    }

    addListElement(listElement, where="afterbegin") {
        let listItem = super.addListElement(...arguments);
        listItem.children[0].addEventListener(
            "pointerdown", this.onPointerDown.bind(this)
        );
    }

    getCreationFormData(listElementsCreationForm) {
        let form_data = new FormData(listElementsCreationForm);
        form_data.append("to_do_list_id", this.toDoListId);
        return form_data;
    }

    getDeletionURL(itemId) {
        return "/api/tasks/delete";
    }

    getCreationURL() {
        return "/api/tasks/create";
    }

    getGetterURL() {
        return `/api/to_do_lists/${this.toDoListId}`;
    }

    onPointerDown(event) {
        event.target.style.position = "fixed";
    }
}

let listObject = new ToDoList(toDoListId);
listObject.bind();