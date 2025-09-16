const multiSelectWidget = (function () {
  const addRow = function () {
    const widget = this.closest('.gadjo-multi-select-widget')
    event.preventDefault()

    const rows = widget.querySelectorAll('.gadjo-multi-select-widget--field')

    if (rows.length + 1 >= widget.dataset.maxChoices) {
      const addBtn = widget.querySelector('.gadjo-multi-select-widget--button-add')
      addBtn.disabled = true
    }

    /* get last row node */
    const lastRow = rows[rows.length - 1]

    /* clone the row */
    const newRow = lastRow.cloneNode(true)

    /* set new label and ids */
    const rowLabel = widget.dataset.rowLabel
    const newLabel = rowLabel + ' ' + rows.length
    newRow.querySelector('label').textContent = newLabel

    const rowId = widget.dataset.rowId
    const newId = rowId + '_' + rows.length
    newRow.querySelector('label').setAttribute('for', newId)
    newRow.querySelector('select').setAttribute('id', newId)

    /* add new row after the last row */
    lastRow.parentNode.insertBefore(newRow, lastRow.nextSibling)

    const removeButton = newRow.querySelector('.gadjo-multi-select-widget--button-remove')
    removeButton.addEventListener('click', removeRow)
  }

  const removeRow = function (event) {
    event.preventDefault()
    const field = this.closest('.content')
    const widget = this.closest('.gadjo-multi-select-widget')

    let row = this.closest('.gadjo-multi-select-widget--field')
    row.remove()

    const addBtn = widget.querySelector('.gadjo-multi-select-widget--button-add')
    addBtn.disabled = false

    field.dispatchEvent(new Event('change'))
  }

  const init = function (container) {
    const widgets = container.querySelectorAll('.gadjo-multi-select-widget')
    if (!widgets.length) return

    widgets.forEach(function (widget) {
      const deletBtn = widget.querySelectorAll('.gadjo-multi-select-widget--button-remove')
      const addBtn = widget.querySelector('.gadjo-multi-select-widget--button-add')

      addBtn.removeEventListener('click', addRow)
      addBtn.addEventListener('click', addRow)
      deletBtn.forEach(btn => btn.removeEventListener('click', removeRow))
      deletBtn.forEach(btn => btn.addEventListener('click', removeRow))
    })
  }

  return {
    init,
  }
})()

window.addEventListener('DOMContentLoaded', () => multiSelectWidget.init(document))
