(function($) {

  var modal;

  $(function() {

    modal = $('#modal');

    $('.primary', modal).click(function() {
      modal.modal('hide');
    });

    $('a.open-modal-form').click(function() {
      $.get(this.href, {}, function(data) {
        $('.modal-body', modal).html(data);
        modal.modal('show');
      });
      return false;
    });

    $('.twipsy').tooltip();

  });

})(jQuery);
