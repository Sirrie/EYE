/**
 * Pin Form for Pinry
 * Descrip: This is for creation new pins on everything, the bookmarklet, on the
 *          site and even editing pins in some limited situations.
 * Authors: Pinry Contributors
 * Updated: March 3rd, 2013
 * Require: jQuery, Pinry JavaScript Helpers
 */


$(window).load(function() {
    var uploadedImage = false;
    var editedPin = null;

    // Start Helper Functions
    function getFormData() {
        return {
            //submitter: currentUser,
            url: $('#pin-form-image-url').val(),
            description: $('#pin-form-description').val(),
            tags: cleanTags($('#pin-form-tags').val())
        }
    }

    function createPinPreviewFromForm() {
        var context = {pins: [{
               // submitter: currentUser,
                image: {thumbnail: {image: $('#pin-form-image-url').val()}},
                description: $('#pin-form-description').val(),
                tags: cleanTags($('#pin-form-tags').val())
            }]},
            html = renderTemplate('#pins-template', context),
            preview = $('#pin-form-image-preview');
        preview.html(html);
        preview.find('.pin').width(500);
        preview.find('.pin').fadeIn(300);
        if (getFormData().url == "")
            preview.find('.image-wrapper').height(255);
        preview.find('.image-wrapper img').fadeIn(300);
        setTimeout(function() {
            if (preview.find('.pin').height() > 305) {
                $('#pin-form .modal-body').animate({
                    'height': preview.find('.pin').height()+25
                }, 300);
            }
        }, 300);
    }

    function dismissModal(modal) {
        modal.modal('hide');
        setTimeout(function() {
            modal.remove();
        }, 200);
    }
    // End Helper Functions


    // Start View Functions
    function createPinForm(editPinId) {
        $('body').append(renderTemplate('#pin-form-template', ''));
        var modal = $('#pin-form'),
            formFields = [$('#pin-form-image-url'), $('#pin-form-description'),
            $('#pin-form-tags')],
            pinFromUrl = getUrlParameter('pin-image-url');
        // If editable grab existing data
        /*if (editPinId) {
            var promise = getPinData(editPinId);
            promise.success(function(data) {
                editedPin = data;
                $('#pin-form-image-url').val(editedPin.image.thumbnail.image);
                $('#pin-form-image-url').parent().hide();
                $('#pin-form-image-upload').parent().hide();
                $('#pin-form-description').val(editedPin.description);
                $('#pin-form-tags').val(editedPin.tags);
                createPinPreviewFromForm();
            });
        }*/
        modal.modal('show');
        // Auto update preview on field changes
      /*  var timer;
        for (var i in formFields) {
            formFields[i].bind('propertychange keyup input paste', function() {
                clearTimeout(timer);
                timer = setTimeout(function() {
                    createPinPreviewFromForm()
                }, 700);
                if (!uploadedImage)
                    $('#pin-form-image-upload').parent().fadeOut(300);
            });
        }*/
        // Drag and Drop Upload
        $('#pin-form-image-upload').fineUploader({
            request: {
                endpoint: 'upload',
                element: $('#thumbnail-fine-uploader'),
                template: "qq-simple-thumbnails-template",
               // paramsInBody: true,
               // multiple: false,
                validation: {
                    allowedExtensions: ['jpeg', 'jpg', 'png', 'gif']
                },
                text: {
                    uploadButton: 'Click or Drop'
                }
            }
        }).on('complete', function(e, id, name, data) {
            $('#pin-form-image-url').parent().fadeOut(300);
            $('.qq-upload-button').css('display', 'none');
            var promise = getImageData(data.success.id);
            uploadedImage = data.success.id;
            var path = "media/upload/"+$("span.qq-upload-file").text();
           // $('#pin-form-image-url').val(path);
            $('#pin-form-image-preview').find('img')[0].src = path
          //  createPinPreviewFromForm();
            promise.success(function(image) {
                $('#pin-form-image-url').val(image.thumbnail.image);
            //    createPinPreviewFromForm();
            });
            promise.error(function() {
                message('Problem uploading image.', 'alert alert-error');
            });
        });
        // If bookmarklet submit
        /*if (pinFromUrl) {
            $('#pin-form-image-upload').parent().css('display', 'none');
            $('#pin-form-image-url').val(pinFromUrl);
            $('.navbar').css('display', 'none');
            modal.css({
                'margin-top': -35,
                'margin-left': -281
            });
        }*/
        // Submit pin on post click
        $('#pin-form-submit').click(function(e) {
            e.preventDefault();
            $(this).off('click');
            $(this).addClass('disabled');
           
            $.post( "/eye/post", { description: $('#pin-form-description').val(), imgurl: $("span.qq-upload-file").text(), tags: $('#pin-form-tags').val() })
              .done(function( data ) {
                alert( "Upload Successful");
                window.close();
                dismissModal(modal);
                location.reload();
              });
           
        });
        $('#pin-form-close').click(function() {
            if (pinFromUrl) return window.close();
            dismissModal(modal);
        });
      //  createPinPreviewFromForm();
    }
    // End View Functions


    // Start Init
    window.pinForm = function(editPinId) {
      //  editPinId = typeof editPinId !== 'undefined' ? editPinId : null;
        createPinForm(editPinId);
    }

    if (getUrlParameter('pin-image-url')) {
        createPinForm();
    }
    // End Init
});
