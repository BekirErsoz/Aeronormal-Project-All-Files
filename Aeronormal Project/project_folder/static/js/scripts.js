$(document).ready(function() {
    var currentPage = 1;

    $('#upload-form').on('submit', function(e) {
        e.preventDefault();
        var formData = new FormData(this);
        $.ajax({
            url: '/upload',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function() {
                fetchImages(1);  // Reset to first page after uploading new image
            },
            error: function() {
                alert('Image upload failed. Please try again.');
            }
        });
    });

    function fetchImages(page) {
        $.get('/get_images', { page: page }, function(data) {
            var imageContainer = $('#image-container');
            imageContainer.empty();
            data.forEach(function(image) {
                var imageCard = '<div class="col-md-4 fade-in">' +
                                '<div class="card mb-4 shadow-sm">' +
                                '<img src="' + image.filename + '" class="card-img-top" alt="Processed Image">' +
                                '<div class="card-body">' +
                                '<p class="card-text">' + image.filename + '</p>' +
                                '<div class="d-flex justify-content-between align-items-center">' +
                                '<small class="timestamp">' + image.timestamp + '</small>' +
                                '</div></div></div></div>';
                imageContainer.append(imageCard);
            });
            updatePagination(page);
        });
    }

    function updatePagination(currentPage) {
        $.get('/total_pages', function(data) {
            var totalPages = data.total_pages;
            var pagination = $('.pagination');
            pagination.empty();
            for (var i = 1; i <= totalPages; i++) {
                var activeClass = (i === currentPage) ? 'active' : '';
                var pageItem = '<li class="page-item ' + activeClass + '">' +
                               '<a class="page-link" href="#" data-page="' + i + '">' + i + '</a>' +
                               '</li>';
                pagination.append(pageItem);
            }
        });
    }

    $(document).on('click', '.page-link', function(e) {
        e.preventDefault();
        currentPage = $(this).data('page');
        fetchImages(currentPage);
    });

    fetchImages(currentPage);  // Initial load
});