jQuery(function() {
    $(".confirm-delete").click(function(e) {
        var url    = $(this).data("url");
        var name   = $(this).data("name");
        var tag_id = $(this).data("tag_id");
        //console.log(url);
        //console.log(name);
        //console.log(tag_id);
        if ( confirm("Are you sure you want to delete " + name + " ?") ) {
            //console.log("Yes");
            function on_success(response) {
                $(tag_id).hide();
            }
            function on_error(response) {
                alert("An error occured.");
            }
            $.ajax({
                'url': url,
                'type': 'GET',
                //'type': 'POST',
                //'data': $(this).data(),
                'dataType': 'json',
                'success': on_success,
                'error': on_error,
            });
        } else {
            //console.log("No");
        }
    });

    $(".click-toggle").click(function(e) {
        var tag = $(this);
        var url    = $(this).data("url");

        function on_success(response) {
            //console.log("success");
            tag.find("span").toggleClass("glyphicon-check");
            tag.find("span").toggleClass("glyphicon-unchecked");
            var tag_id = tag.data("tag_id");
            if (tag_id) {
                $(tag_id).toggleClass("btn-primary");
                $(tag_id).toggleClass("btn-default");
            }
        }
        function on_error(response) {
            alert("An error occured.");
        }
        $.ajax({
            'url': url,
            'type': 'GET',
            'dataType': 'json',
            'success': on_success,
            'error': on_error,
        });
    });

  $(".confirm-delete-file").click(function() {
    return confirm("Are you sure you want to delete this file?")
  });
//  $(".confirm-delete-project").click(function() {
//    return confirm("Are you sure you want to delete this project?")
//  });
  $(".show-button").click(function() {
    $(".appear").show();
    $(".show-button").hide();
  });
});

