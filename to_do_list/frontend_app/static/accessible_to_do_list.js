class ToDoList extends GenericList {
    addListElement(listElement, where="afterbegin") {
        let listItem = super.addListElement(...arguments);
        listItem.children[0].addEventListener(
            "pointerdown", this.onPointerDown.bind(this)
        );
    }

    getDeletionURL(itemId) {
        return `/api/tasks/${itemId}/delete`;
    }

    getCreationURL() {
        return `/api/tasks/create`;
    }

    getCreationFormData(listElementsCreationForm) {
        let form_data = new FormData(listElementsCreationForm);
        form_data.append("to_do_list_id", this.toDoListId);
        return form_data;
    }

    getGetterURL() {
        return `/api/to_do_lists/${this.toDoListId}`;
    }

    onPointerDown(event) {
        event.target.style.position = "fixed";
    }
}

let list_object = new ToDoList({
    toDoListId: toDoListId,
    readableListElementName: "task",
});
list_object.bind();