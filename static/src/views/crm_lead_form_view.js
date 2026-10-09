/** @odoo-module **/

// Auto-save lead before opening site visit modal if form is in draft/edit
document.addEventListener("click", (ev) => {
    const target = ev.target;
    if (!target) return;
    const isSiteVisitTab = target.closest("a[name='site_visits'], .nav-link[name='site_visits'], [data-bs-target*='site_visits']");
    const isAddLine = target.closest("[name='site_visit_ids'] .o_field_x2many_list_row_add");
    if (isSiteVisitTab || isAddLine) {
        const saveBtn = document.querySelector(".o_form_button_save");
        if (saveBtn && !saveBtn.disabled && saveBtn.offsetParent !== null) {
            saveBtn.click();
        }
    }
}, true);
