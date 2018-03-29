var $form = $('form#test-form'),
    url = 'https://script.google.com/macros/s/AKfycbxInXS-TaKovIXklXCUU5dWi842VKVq-qUU6jI7Iz4VvsrsOP4/exec'

$('#submit-form').on('click', function (e) {
    e.preventDefault();
    var jqxhr = $.ajax({
        url: url,
        method: "GET",
        dataType: "json",
        data: $form.serializeObject()
    }).success(
      // do something
    );
})