class ListOfToDoLists extends GenericList {
    readableListElementName = "to-do list";
    postRequestsElementIdFieldName = "to_do_list_id";
    getDeletionURL(itemId) {
        return "/api/to_do_lists/delete/";
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

let listObject = new ListOfToDoLists;
listObject.bind();