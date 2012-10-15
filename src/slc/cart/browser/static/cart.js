/*global $, document*/
(function () {
    "use strict";

    var url,
        $previewBox;

    // ====================== ADD TO CART BUTTON ==========================

    function updateAddToCartButton() {
        // update the state of each add to cart button on the page

        var portalUrl,
            reqUrl,
            UID,
            $this;

        // logo will always point to portal_url
        portalUrl = $("#portal-logo").attr('href');

        $("a#add-to-cart").each(function () {
            var $this = $(this);

            // get the UID from the rel attribute of the button
            UID = $this.attr('rel');

            reqUrl = portalUrl + '/cart?is-item-in-cart=' + UID;
            $.get(reqUrl, null, function (data) {

                // check if the item is already in the cart and update the buttons
                // accordingly.

                if (data.toLowerCase() === "true") {
                    $this.text('Remove from Cart');
                    $this.addClass('remove-button in-cart');
                    $this.attr('href', function (i, url) {
                        return url.replace('add', 'remove');
                    });
                } else {
                    $this.text('Add to Cart');
                    $this.removeClass('remove-button in-cart');
                    $this.attr('href', function (i, url) {
                        return url.replace('remove', 'add');
                    });
                }
            }, "text");  // end $.get
        });
    }

    // ====================== UPDATE CART ITEM COUNT =======================

    function updateCartItemCount() {

        var portalUrl,
            $numCount,
            $numSpan;

        // logo will always point to portal_url
        portalUrl = $("#portal-logo").attr('href');

        $.get(portalUrl + '/cart?num-of-items=true', function (data) {

            // check if the returned data is a number, if it's not, a 302 redirect
            // happened, and the data contains the html of the login page
            if (!isNaN(data)) {

                // get the number count span, if it's present we update it, if not
                // add it. Also if the number of items in the cart is 0 then we
                // remove the span.

                $numCount = $("span.num-count");

                if (data === 0) {
                    $numCount.remove();
                } else if ($numCount.length) {
                    $numCount.text(' (' + data + ')');
                } else {
                    $numSpan = $("<span class='num-count'></span>");
                    $numSpan.text(' (' + data + ')');
                    $numSpan.appendTo($("#personaltools-cart > a"));
                }
            }
        });
    }

    // ====================== ADD TO CART BUTTON ACTIONS ===================

    function addToCartButtonActions() {
        // Actions for the add to cart button

        var tooltip,
            $addAllToCartButton,
            $addToCartButton,
            $portalMessage,
            $this;

        $addToCartButton = $("a#add-to-cart");

        // if the add to cart button can be found on the page, set it, if not, just
        // update the download cart menu item
        if ($addToCartButton.length) {

            tooltip = $(".searchResults #add-to-cart").tooltip({
                predelay: 500
            });

            // if the item is already in the download cart, then update the text and
            // url of the "add to cart" button
            updateAddToCartButton();

            // when the add to cart button is clicked, submit with ajax, update the
            // cart count in the menu, update the text on the button
            $addToCartButton.click(function (e) {
                e.preventDefault();

                url = $(this).attr('href');

                $.get(url, function (data) {

                    if (data.return_status) {
                        updateAddToCartButton();
                        updateCartItemCount();
                    } else {
                        $portalMessage = $(".portalMessage");
                        $portalMessage.find("dd").text(data.message);
                        $portalMessage.find("dt").text("Error");
                        $portalMessage.removeClass('info').addClass('error');
                        $portalMessage.show();
                    }
                },  "json");
            });

            // add all to cart button actions
            $addAllToCartButton = $(".add-all a");

            if ($addAllToCartButton.length) {
                $addAllToCartButton.click(function (e) {
                    e.preventDefault();

                    $addToCartButton.each(function () {
                        $this = $(this);
                        // if the item is not already in the cart, add it
                        if (!$this.hasClass("in-cart")) {
                            $this.click();
                        }
                    });
                });
            }
        }
    }



    // ======================== ALREADY DOWNLOADED =========================

    function alreadyDownloaded() {
        // dimm the item that has been downloaded previously

        $(".item-title").each(function () {

            var itemUrl,
                url,
                $this;

            $this = $(this);
            url = $this.attr('href');
            // remove the "view" from the end of the url
            itemUrl = url.substring(0, url.length - 4);

            $.get(itemUrl + "@@utils/downloaded", function (data) {
                if (data === 'true') {
                    // add class 'downloaded' to the containing row
                    $this.parent().parent().addClass("downloaded");

                    // append the Already Downloaded icon to the Words column
                    $('<span class="already-downloaded" title="You have already downloaded this item." />')
                        .appendTo($this.parent().next().next());
                }
            });

        });
    }

    // ============================== PREVIEW ==============================

    function movePreviewLeft() {
        $previewBox
            .stop(true, true)
            .animate({
                right: 0
            });
    }

    function movePreviewRight() {
        $previewBox
            .stop(true, true)
            .delay(3000)
            .animate({
                right: -600
            });
    }

    function updatePreviewBox($this) {

        var added,
            itemUrl,
            title,
            url,
            words;

        // set the href for open button based on the preview item
        url = $this.prev().attr('href');
        $previewBox.find(".preview-footer .button").attr("href", url);

        // set the title
        title = $this.prev().text();
        $previewBox.find(".preview-title").text(title);

        // set the word count and added date
        words = $this.parent().next().text();
        added = $this.parent().next().next().text();

        $previewBox.find(".preview-words").text(words);
        $previewBox.find(".preview-added").text(added);

        // get the content
        itemUrl = url.substring(0, url.length - 4);

        $.get(itemUrl + "@@utils/head", function (data) {
            data = data.substring(5, data.length - 6);
            $(".preview-body").text(data);
        });
    }

    function previewBox() {
        // item preview

        var $preview,
            $this;

        $preview = $(".preview");

        if ($preview.length) {

            $previewBox = $(".preview-box");

            // if the user clicks on the search icon, the search is shown,
            // and from now on it's shown until it's closed with the close button,
            // or the mouse leaves the results table. Hovering each row the preview
            // updates.

            // click on preview opens it
            $preview.bind('click', function (e) {
                e.preventDefault();
                $this = $(this);
                updatePreviewBox($this);

                $previewBox.addClass("opened");
                $this.css('backgroundPosition', '0px -106px');

                movePreviewLeft();
            });

            // if the preview is opened, mouse hover updates the preview box
            $(".search-item").bind('mouseenter', function () {
                if ($previewBox.hasClass("opened")) {
                    $preview = $(this).find(".preview");
                    $preview.css('backgroundPosition', '0px -106px');
                    updatePreviewBox($preview);
                }
            });

            // when mouse leaves the row, show the inactive preview icon
            $(".search-item").bind('mouseleave', function () {
                if ($previewBox.hasClass("opened")) {
                    $(this).find(".preview").css('backgroundPosition', '0px -132px');
                }
            });

            // make sure the preview box does not close while the mouse is over it
            $previewBox.bind('mouseenter', function () {
                $previewBox.stop(true, true);
            });

            // the close button closes the preview immediately
            $("#preview-close").click(function (e) {
                e.preventDefault();
                $previewBox.removeClass("opened");
                $previewBox.stop(true, true).animate({
                    right: -600
                });
            });

            // mouse leaves search results means that we need to close the preview
            $("#search-results").bind('mouseleave', function () {
                $previewBox.removeClass("opened");
                movePreviewRight();
            });
        }
    }



    // ====================== DOWNLOAD CART ACTIONS ========================

    function setOddEven($table) {
        $table.find('tbody').find('tr').removeClass('odd').removeClass('even')
            .filter(':odd').addClass('even').end()
            .filter(':even').addClass('odd');
    }

    function downloadCartActions() {
        var $remove,
            $row,
            $this;

        $remove = $(".remove-from-cart");

        if ($remove.length) {
            $remove.bind('click', function (e) {
                e.preventDefault();
                $this = $(this);
                url = $this.attr('href');

                // remove the item from cart, remove from table, update cart count
                $.get(url, function (data) {

                    if (data.return_status) {

                        $row = $this.parent().parent();

                        // table row cannot be animated, so we need to add an inner
                        // wrapper div element that we can animate. At the end we
                        // remove the entire row
                        $row.children("td").each(function () {
                            $(this).wrapInner("<div />").children("div")
                                .slideUp("fast", function () {
                                    $row.remove();
                                    setOddEven($(".listing"));
                                });
                        });

                        // update cart count
                        updateCartItemCount();
                    } else {
                        var $portalMessage = $(".portalMessage");
                        $portalMessage.find("dd").text(data.message);
                        $portalMessage.find("dt").text("Error");
                        $portalMessage.removeClass('info').addClass('error');
                        $portalMessage.show();
                    }
                },  "json");
            });
        }
    }

    function onSearchResultsTableUpdate() {
        // whenever search results table is updated we need to manually run
        // search result page specific functions (alreadyDownloaded(),
        // previewBox(), etc.)

        // update the download cart number in the header on page load
        updateCartItemCount();

        // actions for add to cart buttons
        addToCartButtonActions();

        // check if an item has been downloaded, if so, color the row
        alreadyDownloaded();

        // item preview
        previewBox();
    }

    $("document").ready(function () {

        // init search page UI
        onSearchResultsTableUpdate();

        // actions for the download cart page
        downloadCartActions();

        /*
        Need to fix this at some point. Now the tooltip only has Add/Remove text
        and it should update dynamically

        $(".searchResults #add-to-cart").delegate('mouseenter', function() {
            if ($(this).hasClass("remove-button")) {
                $(".tooltip").text('Remove from Cart');
            } else {
                $(".tooltip").text('Add to Cart');
            }
            $(this).trigger("mouseover");
        });
        */
    });

}());