(function($) {

  var modal;

  $(function() {

    modal = $('#modal');

    $('.primary', modal).click(function() {
      modal.modal('hide');
    });

    $('a.open-modal-form').click(function() {
      $.get(this.href, {}, function(data) {
        $('div.modal-body', modal).html(data);
        modal.modal('show');
      });
      return false;
    });

    $('div.modal-body').delegate('input.btn', 'click', (function(event) {
      var $form = $(event.target).closest('form');
      $.post($form.attr('action'),
             $form.serialize(),
             function(data) {
               if (data.match("<html")) // Full page returned - KLUGE ALERT - just redirect to /
                 window.location = "/";
               else { // Partial page returned; assume it's a replacement form
                 $('div.modal-body', modal).html(data);
               }
               return false;
             });
      return false;
    }));


    $('.twipsy').tooltip();

  });

})(jQuery);
