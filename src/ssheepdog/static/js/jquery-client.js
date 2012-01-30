(function($) {

  var modal;

  $(function() {

    modal = $('#modal');
    modal.modal();

    $('.primary', modal).click(function() {
      modal.modal('hide');
    });

    $('a.login').click(function() {
      $.get(this.href, {}, function(data) {
        $('.modal-body', modal).html(data);
        modal.modal('show');
      });
      return false;
    });

    $('a.user').click(function() {
      $.get(this.href, {}, function(data) {
        $('.modal-body', modal).html(data);
        modal.modal('show');
      });
      return false;
    });

    $('.twipsy').twipsy();

  });

})(jQuery);
