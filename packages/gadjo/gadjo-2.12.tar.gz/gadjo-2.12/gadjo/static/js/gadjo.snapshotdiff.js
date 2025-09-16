const $ = window.$
$(function () {
  $('div.snapshot-diff tr').each(function () {
    let $tr = $(this)
    if (!$tr.find('.diff_add, .diff_chg, .diff_sub').length) {
      return
    }
    // mark 3 lines before and after each change
    $tr.addClass('no-collapse')
      .prev().addClass('no-collapse')
      .prev().addClass('no-collapse')
      .prev().addClass('no-collapse')
    $tr
      .next().addClass('no-collapse')
      .next().addClass('no-collapse')
      .next().addClass('no-collapse')
  })
  $('div.snapshot-diff tr').each(function () {
    let $tr = $(this)
    if (!$tr.find('.diff_next a').length) {
      return
    }
    let trId = $tr.find('a').first().attr('href').substring(1)
    // collapse previous lines
    let previousLines = $tr.prevUntil('.difflib_chg_to')
    previousLines.each(function () {
      let $line = $(this)
      if ($line.hasClass('no-collapse') || $line.hasClass('expand-handler')) {
        return
      }
      $line.addClass(trId).addClass('difflib_chg_to').hide()
    })
    // add expand
    if ($tr.prevAll('.difflib_chg_to').first().hasClass(trId)) {
      let expandClass = 'expand-between'
      if ($tr.prevAll('.difflib_chg_to').first().prevAll('.no-collapse').length === 0) {
        expandClass = 'expand-before'
      }
      $('<tr class="expand-handler"></tr>')
        .html(
          '<td colspan="6" class="diff_header expand ' + expandClass + '" data-expand="' + trId + '"></td>',
        )
        .insertAfter($tr.prevAll('.difflib_chg_to').first())
    }
    // if last change
    if ($tr.find('a').first().text() === 't') {
      // collapse next lines
      let nextLines = $tr.nextAll()
      nextLines.each(function () {
        let $line = $(this)
        if ($line.hasClass('no-collapse') || $line.hasClass('expand-handler')) {
          return
        }
        $line.addClass(trId + '-end').addClass('difflib_chg_to').hide()
      })
      // add expand
      $('<tr class="expand-handler"></tr>')
        .html('<td colspan="6" class="diff_header expand expand-after" data-expand="' + trId + '-end"></td>')
        .insertAfter($tr.nextAll('.difflib_chg_to').first())
    }
  })
  $('div.snapshot-diff').show()
  $(document).on('click', '.expand-handler', function () {
    let $handler = $(this)
    $handler.hide()
    let expandClass = $handler.find('td.expand').first().data('expand')
    $('.' + expandClass).show()
  })
})
