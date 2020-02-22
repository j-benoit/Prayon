let checkboxes = [];
let doubtFields = [];

const disbaleInput = element => {
    const id = $(element).attr("id");
    const fieldName = id.substr(9);
    const input_id = `id_${fieldName}`;
    const checkboxText = `[${fieldName.toUpperCase()}] = Aucune valeur trouvée\n`;

    setCheckboxes({
        id: fieldName,
        text: checkboxText,
        checked: $(element)[0].checked
    });

    if ($("#" + id).is(":checked") == true) {
        $("#" + input_id).prop("disabled", false);
        // console.log('checked');
    } else {
        // Set readonly
        $("#" + input_id).prop("disabled", true);

        // Clean value of corresponding input
        $("#" + input_id)[0].value = "";
    }
};

const setCheckboxes = newCheckbox => {
    checkboxes.forEach((box, index) => {
        if (box.id === newCheckbox.id) {
            console.log("MATCHED");
            delete checkboxes[index];
        }
    });

    checkboxes.push(newCheckbox);
};

const setDoubtFields = newDoubt => {
    doubtFields.forEach((field, index) => {
        if (field.id === newDoubt.id) {
            delete doubtFields[index];
        }
    });

    doubtFields.push(newDoubt);
};

const setColorBtnAndCheckAttr = btn => {
    if (btn.className.includes("btn-success")) {
        btn.setAttribute("class", "btn btn-warning");
        btn.setAttribute("checked", "false");
    } else {
        btn.setAttribute("class", "btn btn-success");
        btn.setAttribute("checked", "true");
    }
    return btn.getAttribute("checked");
};

const generateText = array => {
    return array
        .filter(item => {
            if (item !== undefined) {
                if (!item.checked) return true;
            }
        })
        .map(box => box.text)
        .join("");
};

const renderCommentText = () => {
    const id = "id_backlog_comment";

    const checkboxText = generateText(checkboxes);
    const doubtText = generateText(doubtFields);

    $(`#${id}`)[0].innerHTML = `${checkboxText} \n ${doubtText}`;
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
    renderCommentText();
});

const handleDoubtField = (event, field) => {
    const doubtText = `[${field.toUpperCase()}] = A confirmer\n`;
    const checkedDoubtBtn = JSON.parse(setColorBtnAndCheckAttr(event));

    setDoubtFields({
        id: field,
        text: doubtText,
        checked: checkedDoubtBtn
    });
    deactivateSubmitBtn();
    renderCommentText();
};
