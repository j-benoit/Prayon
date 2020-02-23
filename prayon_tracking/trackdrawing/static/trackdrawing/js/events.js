const disbaleInput = element => {
    const id = $(element).attr("id");
    const fieldName = id.substr(9);
    const input_id = `id_${fieldName}`;
    const checkboxText = `[${fieldName.toUpperCase()}] = Aucune valeur trouvée\n`;
    const id_comment = "id_backlog_comment";

    if ($("#" + id).is(":checked") == true) {
        $("#" + input_id).prop("disabled", false);
        // console.log('checked');
        var comment = $(`#${id_comment}`).val();
        comment = comment.replace(checkboxText, "");
        $(`#${id_comment}`).val(comment)
    } else {
        // Set readonly
        $("#" + input_id).prop("disabled", true);

        // Clean value of corresponding input
        $("#" + input_id)[0].value = "";

        // Add comment in text area
        var comment = checkboxText + $(`#${id_comment}`).val();
        $(`#${id_comment}`).val(comment);
    }
};

const deactivateSubmitBtn = () => {
    let submitButton = document.querySelector("#submit-id-submit");
    submitButton.removeAttribute("disabled", "");

    doubtFields.forEach(field => {
        if (!field.checked) {
            submitButton.setAttribute("disabled", "");
        }
    });
};

$(":checkbox").change(function() {
    disbaleInput(this);
});

const handleDoubtField = (event, field) => {
    const doubtText = `[${field.toUpperCase()}] = A confirmer\n`;
    const id_comment = "id_backlog_comment";
    console.log($(event))
    if ($(event).hasClass("btn-success")) {
        $(event).removeClass("btn-success");
        $(event).addClass("btn-warning")
        // Add comment in text area
        var comment = doubtText + $(`#${id_comment}`).val();
        $(`#${id_comment}`).val(comment);
    } else {
        $(event).removeClass("btn-warning");
        $(event).addClass("btn-success");
        var comment = $(`#${id_comment}`).val();
        comment = comment.replace(doubtText, "");
        $(`#${id_comment}`).val(comment)
    }
    deactivateSubmitBtn();
};
