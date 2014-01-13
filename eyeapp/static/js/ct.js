

$(document).ready( function() {
    $(".comment-submit").click(comment);

});

function comment(){ 
          var content=$(this).parent(".comment-form").serialize();
          var url = "/grumblr/comment";
          if($(this).siblings("input[type=text]").val() === ""){
            return;
          }

          $.post( url, content, function(data) {
            console.log(data);
            $( "#commentForm" ).before(data);
          });

         /* posting.done(function( data ) {
            alert(data);
            xmlDoc = $.parseXML(data),
            $xml = $( xmlDoc ),
            var content = $xml.find( "comment" );
            alert(content);
          $( "#commentForm" ).before(content);
          });*/
          // Put the results in a div
}

