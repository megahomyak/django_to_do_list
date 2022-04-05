class ListOfToDoLists extends GenericList {
    getDeletionURL(itemId) {
        return `/api/to_do_lists/${itemId}/delete/`;
    }

    getCreationURL(itemId) {
        return "/api/to_do_lists/create/";
    }

    getGetterURL(itemId) {
        return "/api/to_do_lists/";
    }

    makeListItemTitle(listElement) {
        let viewHyperlink = document.createElement("a");
        viewHyperlink.href = `/to_do_lists/${listElement.id}`;
        viewHyperlink.append(listElement.title);
        return viewHyperlink;
    }
}

let list_object = new ListOfToDoLists({
    readableListElementName: "to-do list",
});
list_object.bind();